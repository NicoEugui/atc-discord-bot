import os
import sys


def _require_env(name):
    value = os.getenv(name)
    if value is None or value == "":
        print(f"FATAL: Required environment variable '{name}' is not set.")
        sys.exit(1)
    return value


def _require_int_env(name):
    raw = _require_env(name)
    try:
        return int(raw)
    except ValueError:
        print(f"FATAL: Environment variable '{name}' must be an integer, got: '{raw}'")
        sys.exit(2)


def _validate_url(url):
    if not url.startswith(("http://", "https://")):
        print(f"FATAL: Stream URL must use http:// or https:// scheme, got: '{url}'")
        sys.exit(3)
    return url


class Config:

    DISCORD_TOKEN_BOT = _require_env("DISCORD_TOKEN_BOT")
    PREFIX = os.getenv("PREFIX", "!")
    CHANNEL_TO_SEND_MESSAGE = _require_int_env("CHANNEL_TO_SEND_MESSAGE")
    CHANNEL_AUDIO_TORRE = _require_int_env("CHANNEL_AUDIO_TORRE")
    ROLE_TO_SEND_MESSAGE = _require_int_env("ROLE_TO_SEND_MESSAGE")
    PLS_FILE = _require_env("PLS_FILE")
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
    RETRY_DELAY_SECONDS = int(os.getenv("RETRY_DELAY_SECONDS", "10"))
