import json
import logging
import threading
from websockets.sync import client
from websockets.exceptions import ConnectionClosedError

from utils.config import get_config
from discord.webhooks import generate_webhook
from discord.discordlib import DiscordMessage, DiscordEmbed
from .rest import get_cur_user, sub_to_event, get_stream
from .constants import TWITCH_WS

STOP_EVTLOOP_EVENT = threading.Event()


def ws_event_loop():
    """
    Main Socket Connect Functions
    Returns Session ID
    """

    # Import event & reset
    global STOP_EVTLOOP_EVENT
    STOP_EVTLOOP_EVENT.clear()

    # Init Webhook
    logging.info("Initializing Discord Webhook...")
    config = get_config()
    webhook = generate_webhook(config.d_webhook)

    # Create connection
    logging.info("Starting Websocket Loop...")
    try:
        with client.connect(TWITCH_WS) as ws:

            # Get Session ID
            welcome = json.loads(ws.recv())
            sess_id = welcome['payload']['session']['id']
            logging.info(f"Websocket ID: {sess_id}")

            # Get User ID
            user = get_cur_user()
            if user is None:
                logging.error("Twitch Auth Error!")
                return None

            # Send off Sub Request
            sub_to_event(
                sess_id,
                event="stream.online",
                conditions={
                    "broadcaster_user_id": user['id']
                }
            )

            # Start Listening
            while not STOP_EVTLOOP_EVENT.is_set():

                # Get message on timeout
                try:
                    raw = ws.recv(5.0)
                except TimeoutError:
                    continue

                # Parse JSON
                message = json.loads(raw)

                # if a stream online message...
                if message['metadata']['message_type'] == "notification" and \
                        message['metadata']['subscription_type'] == "stream.online":

                    # We got a message! Weeeee!
                    # Get user Stream
                    stream = get_stream(user['id'])

                    # Send webhook
                    webhook.send_rich(DiscordMessage(
                        content=f"**{user['display_name']}** is now live on Twitch!",
                        embeds=[
                            DiscordEmbed(
                                title=f"{stream['title']}",
                                description=f"Playing: {stream['game_name']}",
                                image=stream['thumbnail_url'].replace("{width}x{height}", "853x480"),
                                footer="This message is from Azure's Twitchbot!",
                                url=f"https://twitch.tv/{user['login']}",
                                color=0x6441a5
                            )
                        ]
                    ))

            logging.info("Finished ws_event_loop!")

    except ConnectionClosedError as e:
        logging.error("The WebSocket connection was closed!")
        logging.error(e)


def stop_ws_event_loop():
    """
    Tells the websocket to stop looping
    Usually because a user logged out
    """
    global STOP_EVTLOOP_EVENT
    STOP_EVTLOOP_EVENT.set()
