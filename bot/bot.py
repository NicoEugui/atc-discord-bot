import discord
from discord.ext import commands
import asyncio
import os
import logging
from config import Config
from embed_helper import EmbedHelper

# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
TOKEN = Config.DISCORD_TOKEN_BOT
PLS_FILE = Config.PLS_FILE
CHANNEL_TO_SEND_MESSAGE = Config.CHANNEL_TO_SEND_MESSAGE
CHANNEL_AUDIO_TORRE = Config.CHANNEL_AUDIO_TORRE
ROLE_TO_SEND_MESSAGE = Config.ROLE_TO_SEND_MESSAGE

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Function to get the stream URL from the .pls file
def get_stream_url(pls_file):
    with open(pls_file, 'r') as f:
        for line in f:
            if line.startswith('File1='):
                return line.split('=')[1].strip()

# Function to play audio
async def play_audio(ctx, stream_url, voice_channel_id):
    embed_helper = EmbedHelper()
    while True:
        try:
            voice_channel = ctx.guild.get_channel(voice_channel_id)
            if voice_channel is None:
                await embed_helper.send_info_embed(ctx, "Information", "`Specified voice channel for frequency not found`")
                return

            logging.info("Connecting to voice channel...")
            voice_client = await voice_channel.connect()
            logging.info("Successfully connected to voice channel.")

            logging.info("Playing audio...")
            ffmpeg_options = {'options': '-vn'}
            voice_client.play(discord.FFmpegPCMAudio(stream_url, **ffmpeg_options))

            while voice_client.is_playing():
                await asyncio.sleep(1)

            voice_client.stop()  # Stop playback when audio finishes
            await asyncio.sleep(2)  # Wait before attempting to restart playback

            logging.info("Audio finished.")

        except Exception as e:
            logging.error(f"Playback error: {e}", exc_info=True)
            await embed_helper.send_info_embed(ctx, "Information", "`An error occurred while playing audio`")
            await asyncio.sleep(10)  # Wait before attempting again

# Function to reconnect the bot
async def reconnect_bots(ctx):
    embed_helper = EmbedHelper()
    for voice_channel in ctx.guild.voice_channels:
        voice_client = discord.utils.get(ctx.bot.voice_clients, channel=voice_channel)
        if voice_client:
            await voice_client.disconnect()
            logging.info("Bot disconnected from voice channel.")
            voice_channel_id = CHANNEL_AUDIO_TORRE
            if voice_channel_id is not None:
                stream_url = get_stream_url(PLS_FILE)
                if stream_url is not None:
                    await play_audio(ctx, stream_url, voice_channel_id)
                    logging.info("Bot reconnected to voice channel.")
    await embed_helper.send_info_embed(ctx, "Information", "`The bot has been disconnected and reconnected to the voice channel`")

# Function to start the bot
async def start_bot(token, pls_file):
    embed_helper = EmbedHelper()

    bot = commands.Bot(command_prefix=Config.PREFIX, intents=intents)

    @bot.command()
    async def radio(ctx):

        allowed_channel_id = CHANNEL_TO_SEND_MESSAGE

        if ctx.channel.id != allowed_channel_id:
            await embed_helper.send_info_embed(ctx, "Information", "`You cannot use this command in this channel.`")
            return

        required_role_id = ROLE_TO_SEND_MESSAGE
        required_role = discord.utils.get(ctx.guild.roles, id=required_role_id)
        if required_role not in ctx.author.roles:
            await embed_helper.send_info_embed(ctx, "Information", "`You do not have permission to use this command.`")
            return

        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await embed_helper.send_info_embed(ctx, "Information", "`You need to join a voice channel first!`")
            return

        stream_url = get_stream_url(pls_file)
        if stream_url is None:
            await embed_helper.send_info_embed(ctx, "Information", "`The stream URL was not found in the file.`")
            return

        voice_channel_id = CHANNEL_AUDIO_TORRE
        if voice_channel_id is None:
            await embed_helper.send_info_embed(ctx, "Information", "`The voice channel corresponding to the Channel ID was not found.`")
            return

        logging.info("Starting audio playback...")
        await embed_helper.send_info_embed(ctx, "Information", "`Starting playback...`")
        await play_audio(ctx, stream_url, voice_channel_id)
        logging.info("Audio playback started.")

    @bot.command()
    async def reconnect(ctx):
        await reconnect_bots(ctx)

    await bot.start(token)

# Main function to execute the bot
async def main():
    await start_bot(TOKEN, PLS_FILE)

if __name__ == "__main__":
    asyncio.run(main())
