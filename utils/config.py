import os
import json
import logging


class Config:
    """
    Class to represent main app config
    """

    CONFIG_PREFIX = "CONFIG__"

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
        self.hostname = self.get_value(confdata, "hostname", "http://localhost:8080")
        self.d_webhook = self.get_value(confdata, "discord.webhook", "", mandatory=True)
        self.d_status_hook = self.get_value(confdata, "discord.status", self.d_webhook)
        self.t_clientid = self.get_value(confdata, "twitch.clientid", "", mandatory=True)
        self.t_secret = self.get_value(confdata, "twitch.secret", "", mandatory=True)

    def get_value(
            self,
            file: dict,
            key: str,
            default: str,
            mandatory: bool = False
            ):
        """
        Main function for parsing config key values
        - Accepts string of format "value" or "object.value"
        - Prioritizes env over file, for Docker
        """

        # First, try environment variables
        env_var = self.CONFIG_PREFIX + key.upper().replace(".", "__")
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

        # If mandatory and not found yet, error
        if mandatory:
            raise Exception(f"Unset config value '{key}' is mandatory!")

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
