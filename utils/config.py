import os
import json
import logging


class Config:
    """
    Class to represent main app config
    """

    CONFIG_PREFIX = "CONFIG_"

    def __init__(self, config_path: str = "config.json"):
        """Constructor"""

        # Read file and parse
        confdata = None
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                contents = f.read()
            confdata = json.loads(contents)

        # Load values
        # NOTE: If reusing this in future projects, only edit this section here!
        self.hostname = self.get_value(confdata, "hostname", "http://localhost:5000")
        self.d_webhook = self.get_value(confdata, "discord.webhook", "")
        self.t_clientid = self.get_value(confdata, "twitch.clientid", "")
        self.t_secret = self.get_value(confdata, "twitch.secret", "")

    def get_value(self, file: dict, key: str, default: str):
        """
        Main function for parsing config key values
        - Accepts string of format "value" or "object.value"
        - Prioritizes env over file, for Docker
        """

        # First, try environment variables
        env_var = self.CONFIG_PREFIX + key.upper().replace(".", "_")
        env_value = os.environ.get(env_var)
        if env_value is not None:
            return env_value

        # Then, try config file
        try:
            if file is not None:
                data = file
                for part in key.split("."):
                    data = data[part]
                return data
        except KeyError:
            pass

        # Lastly, return default
        return default


# static
config: Config = None


def init_config(path: str):
    """Initializes static config"""
    global config
    config = Config(path)
    if os.environ.get("DEBUG"):
        logging.debug(config.__dict__)
    return config


def get_config():
    """Returns initialized config"""
    return config
