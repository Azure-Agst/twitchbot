import logging
import requests
import urllib.parse

from utils.config import get_config
from utils.db import get_token
from .constants import TWITCH_EVENTSUB, TWITCH_HELIX, TWITCH_AUTH


def format_auth_url():
    """Returns a formatted URL for authorization"""

    # Format params
    config = get_config()
    params = urllib.parse.urlencode({
        "client_id": config.t_clientid,
        "redirect_uri": urllib.parse.urljoin(
            config.hostname, "callback"
        ),
        "response_type": "code",
        "scope": ""
    })

    # return formatted URL
    return TWITCH_AUTH + "/authorize?" + params


def get_cur_user():
    """
    Gets data from API on current user
    Returns None if an error is occurred
    """

    token = get_token()
    if token is None:
        return None

    config = get_config()
    res = requests.get(f'{TWITCH_HELIX}/users', headers={
        "Authorization": f"Bearer {token['access']}",
        "Client-Id": config.t_clientid
    })

    # If bad response, error
    if res.status_code != 200:
        logging.error(f"User data failed with code {res.status_code}!")
        logging.error(res.json())
        return None

    return res.json()['data'][0]


def get_stream(user_id):
    """
    Gets data from API on user's stream
    Returns None if an error is occurred
    """

    token = get_token()
    if token is None:
        return None

    config = get_config()
    res = requests.get(
        f'{TWITCH_HELIX}/streams?user_id={user_id}',
        headers={
            "Authorization": f"Bearer {token['access']}",
            "Client-Id": config.t_clientid
        }
    )

    # If bad response, error
    if res.status_code != 200:
        logging.error(f"User data failed with code {res.status_code}!")
        logging.error(res.json())
        return None

    logging.info(f"Successfully fetched stream info for {user_id} via REST!")
    return res.json()['data'][0]


def sub_to_event(ws_session: str, event: str, conditions: dict):
    """
    Gets data from API on current user
    Returns None if an error is occurred
    """

    token = get_token()
    if token is None:
        return None

    config = get_config()
    res = requests.post(
        f"{TWITCH_EVENTSUB}/eventsub/subscriptions",
        headers={
            "Authorization": f"Bearer {token['access']}",
            "Client-Id": config.t_clientid,
            "Content-Type": "application/json"
        },
        json={
            "type": event,
            "version": "1",
            "condition": conditions,
            "transport": {
                "method": "websocket",
                "session_id": ws_session
            }
        }
    )

    # If bad response, error
    if res.status_code != 202:
        logging.error(f"EventSub add subscription failed with code {res.status_code}!")
        logging.error(res.json())
        return None

    # log and return
    logging.info(f"Successfully subscribed WebSocket {ws_session} to '{event}' via REST!")
    return res.json()
