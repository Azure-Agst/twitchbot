#!/bin/sed -2,2!d;s/^#.//
# This file is intended to be a library, not executed.

# Copyright (C) 2023 Andrew "Azure-Agst" Augustine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import requests
from enum import Enum
from typing import List

# Constants
WEBHOOK_BASE = "https://discord.com/api/webhooks"


class DiscordEmbed():
    """Internal Class that represents a Discord Embed"""

    class Colors(int, Enum):
        """Main Color Enum, used in Discord embeds"""

        # If you havent noticed already, yes this is literally
        # getbootstrap.com's button color scheme, lmfao

        PRIMARY = int(0x0069d9)
        SECONDARY = int(0x5a6268)
        SUCCESS = int(0x218838)
        DANGER = int(0xc82333)
        WARNING = int(0xe0a800)
        INFO = int(0x138496)
        LIGHT = int(0xe2e6ea)
        DARK = int(0x23272b)

    def __init__(
            self,
            title: str = "",
            description: str = "",
            image: str = None,
            color: int = Colors.PRIMARY,
            timestamp: str = "",
            footer: str = "",
            url: str = ""
            ):

        self.title = title
        self.description = description
        self.image = image
        self.color = color
        self.timestamp = timestamp
        self.footer = footer
        self.url = url

    def __repr__(self):
        return f"DiscordEmbed(title='{self.title}')"

    @staticmethod
    def from_dict(data: dict):
        """Method to generate DiscordEmbed from parsed JSON"""

        image = data['image']['url'] if 'image' in data.keys() else None
        timestamp = data['timestamp'] if 'timestamp' in data.keys() else ""
        footer = data['footer']['text'] if 'footer' in data.keys() else None

        return DiscordEmbed(
            title=data["title"],
            description=data["description"],
            color=data["color"],
            image=image,
            timestamp=timestamp,
            footer=footer,
            url=data["url"]
        )

    def to_dict(self):
        """Returns data in dict for JSON formatting"""

        temp_dict = {
            "title": self.title,
            "description": self.description,
            "color": self.color,
            "timestamp": self.timestamp,
            "url": self.url
        }

        if self.image:
            temp_dict["image"] = {
                "url": self.image
            }

        if self.footer:
            temp_dict["footer"] = {
                "text": self.footer
            }

        return temp_dict


class DiscordMessage():
    """Internal Class that represents a Discord Message"""

    class Flags(int, Enum):
        """Extra Flags for Allowed Mentions"""

        SILENT_MESSAGE = int(0x0001)
        ALLOW_MENTION_ROLE = int(0x0010)
        ALLOW_MENTION_USER = int(0x0100)
        ALLOW_MENTION_EVERYONE = int(0x1000)

    def __init__(
            self,
            content: str = "",
            embeds: List[DiscordEmbed] = [],
            flags: int = 0,
            id: str = ""):

        self.content = content
        self.embeds = embeds
        self.flags = flags
        self.id = id

    def __repr__(self):
        return f"DiscordMessage(id='{self.id}', " +\
               f"content='{self.content}', " +\
               f"embeds={len(self.embeds)}, " +\
               f"flags={self.flags})"

    @staticmethod
    def from_dict(data: dict):
        """Method to generate DiscordMessage from parsed JSON"""

        # Allowed Mentions Parsing
        tempflag = 0
        if 'allowed_mentions' in data.keys() and \
                'parse' in data['allowed_mentions'].keys():
            if data['allowed_mentions']['parse'] == []:
                tempflag |= DiscordMessage.Flags.SILENT_MESSAGE
            if "roles" in data['allowed_mentions']['parse']:
                tempflag |= DiscordMessage.Flags.ALLOW_MENTION_ROLE
            if "users" in data['allowed_mentions']['parse']:
                tempflag |= DiscordMessage.Flags.ALLOW_MENTION_USER
            if "everyone" in data['allowed_mentions']['parse']:
                tempflag |= DiscordMessage.Flags.ALLOW_MENTION_EVERYONE

        return DiscordMessage(
            data["content"], data["embeds"],
            tempflag, data["id"]
        )

    def to_dict(self):
        """Returns data in dict for JSON formatting"""

        temp_dict = {
            "id": self.id,
            "content": self.content,
            "embeds": [e.to_dict() for e in self.embeds]
        }

        # Allowed Mentions Formatting
        if self.flags & 0x1111:
            temp_dict["allowed_mentions"] = {}
            temp_dict["allowed_mentions"]["parse"] = []
            if self.flags & DiscordMessage.Flags.ALLOW_MENTION_ROLE:
                temp_dict["allowed_mentions"]["parse"] += ["roles"]
            if self.flags & DiscordMessage.Flags.ALLOW_MENTION_USER:
                temp_dict["allowed_mentions"]["parse"] += ["users"]
            if self.flags & DiscordMessage.Flags.ALLOW_MENTION_EVERYONE:
                temp_dict["allowed_mentions"]["parse"] += ["everyone"]

        return temp_dict


class DiscordWebhook():
    """Main Discord Webhook Post Class"""

    def __init__(
            self,
            url: str,
            name: str = "Python Webhook",
            pfp_url: str = ""):

        # Error checking
        if not url:
            raise Exception("Must have post URL!")

        # Check if this is a valid url
        if not url.startswith(WEBHOOK_BASE):
            raise Exception("Invalid webhook, wtf?")

        # Save vars
        self.name = name
        self.pfp = pfp_url
        self.url = url

    #
    # Sends
    #

    def send_plain(self, content: str, flags: int = 0):
        """Text-only Discord Message Function"""
        return self.send_rich(DiscordMessage(content, flags=flags))

    def send_rich(self, message: DiscordMessage):
        """Rich Discord Message Function"""

        if message.content == "" and len(message.embeds) == 0:
            logging.error("Cannot send empty webhook!")
            return

        json = message.to_dict()
        json['username'] = self.name
        json['avatar_url'] = self.pfp

        res = requests.post(
            f"{self.url}?wait=true",
            json=json
        )

        return DiscordMessage.from_dict(res.json())

    #
    # Updates
    #

    def update(self, message: DiscordMessage):
        """
        Updates a message in a Discord channel
        NOTE: 'message.id' must point to a valid, existing message
        """

        # update the message
        return requests.patch(
            f"{self.url}/messages/{message.id}",
            json=message.to_dict()
        ).json()

    #
    # Deletes
    #

    def delete(self, message: DiscordMessage):
        """
        Deletes a message in a Discord channel
        NOTE: 'message.id' must point to a valid, existing message
        """

        # delete the message
        return requests.delete(
            f"{self.url}/messages/{message.id}"
        )


# Disclaimer for accidental invocations
if __name__ == "__main__":
    logging.error("This file is intended to be a library, not executed.")
    exit(0)
