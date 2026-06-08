import asyncio
import logging
from functools import lru_cache

import discord

from config import Config, validate_url
from embed_helper import EmbedHelper
from constants import (
    MSG_STREAM_URL_NOT_FOUND,
    MSG_VOICE_CHANNEL_NOT_FOUND,
    MSG_STARTING_PLAYBACK,
    MSG_MAX_RETRIES,
    MSG_CONNECTION_RETRY,
)

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _cached_stream_url(pls_file_path: str) -> str | None:
    with open(pls_file_path, "r") as f:
        for line in f:
            if line.startswith("File1="):
                url = line.split("=", 1)[1].strip()
                validate_url(url)
                return url
    return None


def get_stream_url() -> str | None:
    return _cached_stream_url(str(Config.PLS_FILE))


def get_embed() -> EmbedHelper:
    return EmbedHelper()


async def play_audio(
    ctx: discord.ext.commands.Context,
    stream_url: str,
    voice_channel_id: int,
) -> None:
    embed = get_embed()
    retries = 0

    while retries < Config.MAX_RETRIES:
        try:
            voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

            if voice_client:
                logger.info("Disconnecting from existing voice channel...")
                await voice_client.disconnect()

            voice_channel = ctx.guild.get_channel(voice_channel_id)
            if voice_channel is None:
                await embed.send_info_embed(ctx, "Information", MSG_VOICE_CHANNEL_NOT_FOUND)
                return

            logger.info("Connecting to voice channel...")
            voice_client = await voice_channel.connect()

            logger.info("Playing audio...")
            ffmpeg_options = {"options": "-vn"}
            source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_options)
            voice_client.play(source)

            done = asyncio.Event()
            loop = asyncio.get_running_loop()

            def _on_finished(error: Exception | None) -> None:
                if error:
                    logger.warning("Playback finished with error: %s", error)
                loop.call_soon_threadsafe(done.set)

            voice_client.after = _on_finished

            await done.wait()
            logger.info("Audio stopped.")
            retries = 0
            await asyncio.sleep(2)

        except (discord.ClientException, discord.HTTPException) as e:
            retries += 1
            delay = Config.RETRY_DELAY_SECONDS * retries
            msg = MSG_CONNECTION_RETRY.format(retries=retries, max_retries=Config.MAX_RETRIES)
            logger.warning("Discord error (%s/%s): %s. Retrying in %ss...", retries, Config.MAX_RETRIES, e, delay)
            await embed.send_info_embed(ctx, "Information", msg)
            await asyncio.sleep(delay)

        except (ConnectionError, TimeoutError, OSError) as e:
            retries += 1
            delay = Config.RETRY_DELAY_SECONDS * retries
            logger.warning("Network error (%s/%s): %s. Retrying in %ss...", retries, Config.MAX_RETRIES, e, delay)
            await asyncio.sleep(delay)

    logger.error("Max retries (%s) reached. Giving up.", Config.MAX_RETRIES)
    await embed.send_info_embed(ctx, "Information", MSG_MAX_RETRIES)


async def reconnect_and_play(ctx: discord.ext.commands.Context) -> None:
    embed = get_embed()
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

    if voice_client:
        await voice_client.disconnect()
        logger.info("Bot disconnected from voice channel.")

    stream_url = get_stream_url()
    if stream_url is None:
        await embed.send_info_embed(ctx, "Information", MSG_STREAM_URL_NOT_FOUND)
        return

    await play_audio(ctx, stream_url, Config.CHANNEL_AUDIO_TORRE)
