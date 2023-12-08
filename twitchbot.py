#!/usr/bin/env python3

import logging
from flask import Flask
from pathlib import Path

from utils.logging import configure_logging
configure_logging()

from routes import routes  # noqa: E402
from twitch.oauth import validate_token  # noqa: E402
from twitch.websocket import ws_event_loop  # noqa: E402
from utils.db import init_db  # noqa: E402
from utils.config import init_config  # noqa: E402
from utils.threads import WorkerThread, queue  # noqa: E402


def main():
    """Main Entrypoint"""

    logging.info("Starting up...")

    # Read config
    logging.info("Reading config...")
    Path("data").mkdir(parents=True, exist_ok=True)
    init_config("data/config.json")

    # Init Twitch Database
    logging.info("Initializing Twitch DB...")
    init_db("data/twitch.db")

    # Start Worker Thread
    logging.info("Spawning Worker Thread...")
    WorkerThread("Worker-1").start()

    # Validate Twitch Token
    status = validate_token()
    if status is not None:
        logging.info("Found valid cached token! Using...")
        queue.push(ws_event_loop)
    else:
        logging.warn("No cached token found or token didn't pass validation! Must re-auth!")

    # Configure webapp
    web = Flask(__name__)
    web.register_blueprint(routes)

    # Return main webapp
    return web


if __name__ == "__main__":
    exit(main())
