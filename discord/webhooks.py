from utils.config import get_config
from .discordlib import DiscordWebhook, DiscordMessage, DiscordEmbed


def generate_webhook(url: str):
    """Returns a webhook object with the PFP and Name set"""
    return DiscordWebhook(
        url,
        name="Twitch Notifier",
        pfp_url="https://static-cdn.jtvnw.net/jtv_user_pictures/8a6381c7-d0c0-4576-b179-38bd5ce1d6af-profile_image-300x300.png"
    )


def send_status_notif(message: str, warn: bool = False, error: bool = False):
    """Sends a notif to the status channel"""

    color = DiscordEmbed.Colors.DANGER if error \
        else DiscordEmbed.Colors.WARNING if warn \
        else DiscordEmbed.Colors.SUCCESS

    config = get_config()
    hook = generate_webhook(config.d_status_hook)
    hook.send_rich(DiscordMessage(
        embeds=[
            DiscordEmbed(
                title="System Notification",
                description=message,
                footer="This message is from Azure's Twitchbot!",
                color=color
            )
        ]
    ))