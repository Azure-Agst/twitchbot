import json
import logging
from websockets.sync import client
from websockets.exceptions import ConnectionClosedError

from discordlib import DiscordWebhook, DiscordMessage, DiscordEmbed
from utils.config import get_config
from .rest import get_cur_user, sub_to_event, get_stream
from .constants import TWITCH_WS


def ws_event_loop():
    """
    Main Socket Connect Functions
    Returns Session ID
    """

    # Init Webhook
    logging.info("Initializing Discord Webhook...")
    config = get_config()
    webhook = DiscordWebhook(config.d_webhook)

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
            while True:
                message = json.loads(ws.recv())

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

    except ConnectionClosedError as e:
        logging.error("The WebSocket connection was closed!")
        logging.error(e)
