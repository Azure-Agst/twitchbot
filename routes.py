import os
import logging
from flask import Blueprint, request, render_template, \
    redirect, abort, url_for

from utils.threads import queue
from utils.db import clear_token
from twitch.oauth import request_token
from twitch.websocket import ws_event_loop, stop_ws_event_loop
from twitch.rest import format_auth_url, get_cur_user

routes = Blueprint(
    "main", __name__,
    template_folder="templates"
)


@routes.route("/")
def index():
    user = get_cur_user()
    auth_url = format_auth_url() \
        if not os.environ.get("DEBUG") \
        else url_for("main.debug_get_token")
    return render_template(
        "index.html",
        auth_url=auth_url,
        user=user
    )


@routes.route("/callback")
def oauth_callback():
    """Callback for OAuth"""

    code = request.args.get("code")

    res = request_token(code)
    if res is None:
        return "Server-side error. Check Logs.", 500

    logging.info("User has logged in!")
    queue.push(ws_event_loop)

    return redirect("/")


@routes.route("/logout")
def logout():
    """Stop the bot!"""

    if get_cur_user() is None:
        return "Already logged out.", 400

    clear_token()
    stop_ws_event_loop()

    logging.info("User has logged out!")

    return redirect("/")


@routes.route("/debug-get-token")
def debug_get_token():
    """For Local Testing"""

    if not os.environ.get("DEBUG"):
        return abort(404)

    res = request_token("")
    if res is None:
        return "Server-side error. Check Logs.", 500

    queue.push(ws_event_loop)

    return redirect("/")
