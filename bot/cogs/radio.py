import logging

import discord
from discord.ext import commands

from config import Config
from checks import check_permissions, check_voice
from audio import get_stream_url, get_embed, play_audio, reconnect_and_play
from constants import (
    MSG_STREAM_URL_NOT_FOUND,
    MSG_STARTING_PLAYBACK,
    MSG_RECONNECTED,
    MSG_COOLDOWN,
)

logger = logging.getLogger(__name__)


class RadioCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def radio(self, ctx: commands.Context) -> None:
        if not await check_permissions(ctx):
            return
        if not await check_voice(ctx):
            return

        embed = get_embed()
        stream_url = get_stream_url()
        if stream_url is None:
            await embed.send_info_embed(ctx, "Information", MSG_STREAM_URL_NOT_FOUND)
            return

        logger.info("Starting audio playback...")
        await embed.send_info_embed(ctx, "Information", MSG_STARTING_PLAYBACK)
        await play_audio(ctx, stream_url, Config.CHANNEL_AUDIO_TORRE)

    @radio.error
    async def radio_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            embed = get_embed()
            await embed.send_info_embed(
                ctx, "Information",
                MSG_COOLDOWN.format(seconds=error.retry_after),
            )
        else:
            logger.error("Unhandled error in radio command: %s", error)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def reconnect(self, ctx: commands.Context) -> None:
        if not await check_permissions(ctx):
            return

        await reconnect_and_play(ctx)
        embed = get_embed()
        await embed.send_info_embed(ctx, "Information", MSG_RECONNECTED)

    @reconnect.error
    async def reconnect_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            embed = get_embed()
            await embed.send_info_embed(
                ctx, "Information",
                MSG_COOLDOWN.format(seconds=error.retry_after),
            )
        else:
            logger.error("Unhandled error in reconnect command: %s", error)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RadioCog(bot))
