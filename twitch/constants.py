import os
import logging

DEBUG = os.environ.get("DEBUG", False)

if DEBUG:
    TWITCH_WS = "ws://127.0.0.1:8081/ws"
    TWITCH_HELIX = "http://localhost:8080/mock"
    TWITCH_AUTH = "http://localhost:8080/auth"
    TWITCH_EVENTSUB = "http://127.0.0.1:8081"
    logging.warning("Using debug Twitch endpoints!")
else:
    TWITCH_WS = "wss://eventsub.wss.twitch.tv/ws"
    TWITCH_HELIX = "https://api.twitch.tv/helix"
    TWITCH_AUTH = "https://id.twitch.tv/oauth2"
    TWITCH_EVENTSUB = TWITCH_HELIX
