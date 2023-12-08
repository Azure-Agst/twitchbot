import os
import logging
import requests
import urllib.parse

from utils.config import get_config
from utils.db import get_token, set_token, clear_token
from .constants import TWITCH_AUTH


def request_token(code: str):
    """
    Requests token from API using code
    """

    # Send request
    config = get_config()
    if os.environ.get("DEBUG"):
        params = urllib.parse.urlencode({
            "client_id": config.t_clientid,
            "client_secret": config.t_secret,
            "grant_type": "user_token",
            "user_id": "40764486",  # hardcoded
            "scope": ""
        })
        res = requests.post(f'{TWITCH_AUTH}/authorize?' + params)
    else:
        res = requests.post(f'{TWITCH_AUTH}/token', data={
            "grant_type": "authorization_code",
            "client_id": config.t_clientid,
            "client_secret": config.t_secret,
            "code": code,
            "redirect_uri": urllib.parse.urljoin(
                config.hostname, "callback"
            ),
        })

    # If bad response, error
    if res.status_code != 200:
        logging.error(f"Twitch token retrieval failed with code {res.status_code}!")
        logging.error(res.json())
        return None

    # Else, set db
    set_token(res.json())
    return "Ok"


def refresh_token():
    """
    Refreshes the token using the values stored in the DB
    """

    # Get token
    token = get_token()
    if token is None:
        return None

    # If recovering from a dev run and refresh is blank
    if 'refresh' not in token:
        clear_token()
        return None

    # Send request
    config = get_config()
    res = requests.post(f'{TWITCH_AUTH}/token', data={
        "grant_type": "refresh_token",
        "client_id": config.t_clientid,
        "client_secret": config.t_secret,
        "refresh_token": token.refresh,
        "redirect_uri": urllib.parse.urljoin(
            config.hostname, "callback"
        ),
    })

    # if bad refresh token
    if res.status_code == 400:
        logging.error("Bad refresh token! User must log in again!")
        clear_token()
        return None

    # If other bad response, error
    if res.status_code != 200:
        logging.error(f"Twitch token refresh failed with code {res.status_code}!")
        logging.error(res.json())
        return None

    # Else, set db
    set_token(res.json())
    return "Ok"


def validate_token():
    """
    Validates the token stored in the DB
    """
    logging.info("Validating Twitch token...")

    # Get token
    token = get_token()
    if token is None:
        return None

    # Send request
    res = requests.get(f'{TWITCH_AUTH}/validate', headers={
        "Authorization": f"Bearer {token['access']}",
    })
    logging.info(res.text)

    # If unauthorized, refresh token
    if res.status_code == 401:
        logging.info("Refreshing token...")

        refresh = refresh_token()
        if refresh is not None:
            return validate_token()
        return None

    # If bad response, error
    if res.status_code != 200:
        logging.error(f"Twitch token refresh failed with code {res.status_code}!")
        logging.error(res.json())
        return None

    # We good
    return "Ok"
