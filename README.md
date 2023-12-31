<img src="./assets/twitch.svg" height=160>&nbsp;&nbsp;<img src="./assets/discord.svg" height=140>

# Twitch Discord Bridge

This project is a simple Docker-contained webapp that serves as a bridge between Twitch and Discord. Whenever the streamer who is logged in goes live, a Discord Webhook is dispatched.

## Setup

You'll need a registered Twitch application and a webhook.

1. Visit the [Twitch Dev Portal](https://dev.twitch.tv/console) and create an app. Name it whatever you want, make it of type "Confidential", and set the callback url to your desired domain with the endpoint `/callback`. Note that this URL does not have to be public facing, as long as you can access it.
2. Create a Discord Webhook in a channel of your choice
3. Fill in your config file
4. Profit?

## Running

This app can either be run using docker (preferred method) or by cloning and using `waitress-serve`.

### Docker

Below is an example command you can use to start up the Docker image

```bash
docker run -dp 8080:8080 \
    -v twitch_persist:/usr/src/app/data \
    -e CONFIG__HOSTNAME=http://localhost:8080 \
    -e CONFIG__DISCORD_WEBHOOK=https://discord.com/... \
    -e CONFIG__DISCORD_STATUS=https://discord.com/...
    -e CONFIG__TWITCH__CLIENTID=1234567890 \
    -e CONFIG__TWITCH__SECRET=abcdefgh \
    ghcr.io/azure-agst/twitchbot
```

### Local Install

Make sure you have a version of Python greater than or equal to 3.10. Clone the repo. Install requirements. Serve using the following command:

```bash
waitress-serve --call 'twitchbot:main'
```

## Config

The configuration for this is stored in `data/config.json`. There is an included example.

```json
{
    "hostname": "http://localhost:8080",
    "discord": {
        "webhook": "https://discord.com/api/webhooks/..."
    },
    "twitch": {
        "clientid": "...",
        "secret": "..."
    }
}
```

For those who prefer to use env vars for config, you can do so by the key and prefixing with `CONFIG__`. For nested config options, separate with two underscores.

```bash
CONFIG__HOSTNAME=http://localhost:8080
CONFIG__DISCORD__WEBHOOK=https://discord.com/api/webhooks/...
```

## License

This file is distributed under the GNU GPLv3 license. I offer no promises that this project will be maintained into the future. 👍

A full copy of the license can be found in [LICENSE](./LICENSE).

---

*Copyright (C) 2023 Andrew "Azure-Agst" Augustine*
