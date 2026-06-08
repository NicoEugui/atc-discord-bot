import discord
from discord.ext import commands
import asyncio
import logging
from config import Config, _validate_url
from embed_helper import EmbedHelper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = Config.DISCORD_TOKEN_BOT
PLS_FILE = Config.PLS_FILE
CHANNEL_TO_SEND_MESSAGE = Config.CHANNEL_TO_SEND_MESSAGE
CHANNEL_AUDIO_TORRE = Config.CHANNEL_AUDIO_TORRE
ROLE_TO_SEND_MESSAGE = Config.ROLE_TO_SEND_MESSAGE
MAX_RETRIES = Config.MAX_RETRIES
RETRY_DELAY_SECONDS = Config.RETRY_DELAY_SECONDS

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True


def get_stream_url(pls_file):
    with open(pls_file, "r") as f:
        for line in f:
            if line.startswith("File1="):
                url = line.split("=", 1)[1].strip()
                _validate_url(url)
                return url


async def play_audio(ctx, stream_url, voice_channel_id):
    embed_helper = EmbedHelper()
    retries = 0

    while retries < MAX_RETRIES:
        try:
            voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

            if voice_client:
                logger.info("Disconnecting from existing voice channel...")
                await voice_client.disconnect()

            voice_channel = ctx.guild.get_channel(voice_channel_id)
            if voice_channel is None:
                await embed_helper.send_info_embed(
                    ctx, "Information",
                    "`The specified voice channel was not found for the frequency`"
                )
                return

            logger.info("Connecting to voice channel...")
            voice_client = await voice_channel.connect()

            logger.info("Playing audio...")
            ffmpeg_options = {"options": "-vn"}
            voice_client.play(discord.FFmpegPCMAudio(stream_url, **ffmpeg_options))

            while voice_client.is_playing():
                await asyncio.sleep(1)

            voice_client.stop()
            logger.info("Audio stopped.")
            await asyncio.sleep(2)

        except (discord.ClientException, discord.HTTPException) as e:
            retries += 1
            delay = RETRY_DELAY_SECONDS * retries
            logger.warning(
                "Discord error (attempt %s/%s): %s. Retrying in %ss...",
                retries, MAX_RETRIES, e, delay
            )
            await embed_helper.send_info_embed(
                ctx, "Information",
                f"`Connection error, retrying ({retries}/{MAX_RETRIES})...`"
            )
            await asyncio.sleep(delay)

        except (ConnectionError, TimeoutError, OSError) as e:
            retries += 1
            delay = RETRY_DELAY_SECONDS * retries
            logger.warning(
                "Network error (attempt %s/%s): %s. Retrying in %ss...",
                retries, MAX_RETRIES, e, delay
            )
            await asyncio.sleep(delay)

    logger.error("Max retries (%s) reached. Giving up.", MAX_RETRIES)
    await embed_helper.send_info_embed(
        ctx, "Information",
        "`Max reconnection attempts reached. Playback stopped.`"
    )


async def reconnect_bots(ctx):
    embed_helper = EmbedHelper()
    for voice_channel in ctx.guild.voice_channels:
        voice_client = discord.utils.get(ctx.bot.voice_clients, channel=voice_channel)
        if voice_client:
            await voice_client.disconnect()
            logger.info("Bot disconnected from voice channel.")
            voice_channel_id = CHANNEL_AUDIO_TORRE
            if voice_channel_id is not None:
                stream_url = get_stream_url(PLS_FILE)
                if stream_url is not None:
                    await play_audio(ctx, stream_url, voice_channel_id)
                    logger.info("Bot reconnected to voice channel.")
    await embed_helper.send_info_embed(
        ctx, "Information",
        "`The bot has been disconnected and reconnected to the voice channel`"
    )


async def start_bot(token, pls_file):
    embed_helper = EmbedHelper()

    bot = commands.Bot(command_prefix=Config.PREFIX, intents=intents)

    @bot.event
    async def on_ready():
        logger.info("Bot is ready. Logged in as %s", bot.user)

    @bot.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def radio(ctx):

        allowed_channel_id = CHANNEL_TO_SEND_MESSAGE

        if ctx.channel.id != allowed_channel_id:
            await embed_helper.send_info_embed(
                ctx, "Information",
                "`You cannot use this command in this channel.`"
            )
            return

        required_role_id = ROLE_TO_SEND_MESSAGE
        required_role = discord.utils.get(ctx.guild.roles, id=required_role_id)
        if required_role not in ctx.author.roles:
            await embed_helper.send_info_embed(
                ctx, "Information",
                "`You do not have permission to use this command.`"
            )
            return

        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await embed_helper.send_info_embed(
                ctx, "Information",
                "`You need to join a voice channel first!`"
            )
            return

        stream_url = get_stream_url(pls_file)
        if stream_url is None:
            await embed_helper.send_info_embed(
                ctx, "Information",
                "`The stream URL was not found in the file.`"
            )
            return

        voice_channel_id = CHANNEL_AUDIO_TORRE
        if voice_channel_id is None:
            await embed_helper.send_info_embed(
                ctx, "Information",
                "`The voice channel corresponding to the Channel ID was not found.`"
            )
            return

        logger.info("Starting audio playback...")
        await embed_helper.send_info_embed(
            ctx, "Information", "`Starting playback...`"
        )
        await play_audio(ctx, stream_url, voice_channel_id)

    @radio.error
    async def radio_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await embed_helper.send_info_embed(
                ctx, "Information",
                f"`This command is on cooldown. Try again in {error.retry_after:.1f}s.`"
            )
        else:
            logger.error("Unhandled error in radio command: %s", error)

    @bot.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def reconnect(ctx):

        allowed_channel_id = CHANNEL_TO_SEND_MESSAGE

        if ctx.channel.id != allowed_channel_id:
            await embed_helper.send_info_embed(
                ctx, "Information",
                "`You cannot use this command in this channel.`"
            )
            return

        required_role_id = ROLE_TO_SEND_MESSAGE
        required_role = discord.utils.get(ctx.guild.roles, id=required_role_id)
        if required_role not in ctx.author.roles:
            await embed_helper.send_info_embed(
                ctx, "Information",
                "`You do not have permission to use this command.`"
            )
            return

        await reconnect_bots(ctx)

    @reconnect.error
    async def reconnect_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await embed_helper.send_info_embed(
                ctx, "Information",
                f"`This command is on cooldown. Try again in {error.retry_after:.1f}s.`"
            )
        else:
            logger.error("Unhandled error in reconnect command: %s", error)

    await bot.start(token)


async def main():
    if not TOKEN:
        logger.critical("DISCORD_TOKEN_BOT is not set. Exiting.")
        return

    if not os.path.exists(PLS_FILE):
        logger.critical("PLS_FILE '%s' does not exist. Exiting.", PLS_FILE)
        return

    await start_bot(TOKEN, PLS_FILE)


if __name__ == "__main__":
    asyncio.run(main())
