<div align="center">
<img height="200px" width="200px" src="https://cdn.discordapp.com/attachments/1154140630914699355/1226298553488375840/ATC_BOT.png?ex=66244286&is=6611cd86&hm=1b811b16cb71ae067ecc9020c4b99d6e804609c4f1d2b8f367caab84a19c9e1e&"></img>
</div>

# ATC Discord Bot for LiveATC Streams

This Discord bot allows users to stream air traffic control (ATC) audio from LiveATC.net in a voice channel. It fetches the stream URLs from LiveATC.net using the specified ICAO code, allowing users to listen to real-time ATC communications.

## Features

- Fetches stream URLs from LiveATC.net using a specified ICAO code
- Plays ATC audio streams in a voice channel
- Commands for starting and reconnecting the audio stream
- Permission checks to ensure only authorized users can control the bot
- Error handling for playback errors and missing stream URLs

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/NicoEugui/atc-discord-bot.git
    cd atc-discord-bot
    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html) or install it using [Chocolatey](https://chocolatey.org/):

    ```bash
    choco install ffmpeg
    ```

4. Create a `.env` file based on `.env.example` and fill in the necessary values such as Discord token, channel IDs, and roles.

5. Run the bot:

    ```bash
    python bot\bot.py
    ```

## Usage

Once the bot is running and added to your Discord server, you can use the following commands:

- `!radio`: Start playing the ATC audio stream in the voice channel.
- `!reconnect`: Reconnect the bot to the voice channel.

## Configuration

You need to configure the following constants in `.env`:

- `DISCORD_TOKEN_BOT`: Your Discord bot token.
- `CHANNEL_TO_SEND_MESSAGE`: ID of the channel where bot messages will be sent.
- `CHANNEL_AUDIO_TORRE`: ID of the voice channel where the ATC audio stream will be played.
- `ROLE_TO_SEND_MESSAGE`: ID of the role required to use bot commands.

## Dependencies

- [discord.py](https://github.com/Rapptz/discord.py): Discord API wrapper

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
