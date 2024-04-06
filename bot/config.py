import os

class Config:

    DISCORD_TOKEN_BOT = os.getenv('DISCORD_TOKEN_BOT')  # Bot token
    PREFIX = os.getenv('PREFIX')  # Command prefix
    CHANNEL_TO_SEND_MESSAGE = int(os.getenv('CHANNEL_TO_SEND_MESSAGE'))  # Text channel ID for sending messages
    CHANNEL_AUDIO_TORRE = int(os.getenv('CHANNEL_AUDIO_TORRE'))  # Voice channel ID for audio playback
    ROLE_TO_SEND_MESSAGE = int(os.getenv('ROLE_TO_SEND_MESSAGE'))  # Role ID for sending messages
    PLS_FILE = os.getenv('PLS_FILE')  # Path to the .pls file with the stream URL