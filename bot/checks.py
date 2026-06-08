from typing import Optional

import discord
from discord.ext import commands

from config import Config
from embed_helper import EmbedHelper
from constants import (
    MSG_WRONG_CHANNEL,
    MSG_NO_PERMISSION,
    MSG_NO_VOICE,
)


def _get_embed() -> EmbedHelper:
    return EmbedHelper()


async def check_permissions(ctx: commands.Context) -> bool:
    embed = _get_embed()

    if ctx.channel.id != Config.CHANNEL_TO_SEND_MESSAGE:
        await embed.send_info_embed(ctx, "Information", MSG_WRONG_CHANNEL)
        return False

    required_role: Optional[discord.Role] = discord.utils.get(
        ctx.guild.roles, id=Config.ROLE_TO_SEND_MESSAGE
    )
    if required_role not in ctx.author.roles:
        await embed.send_info_embed(ctx, "Information", MSG_NO_PERMISSION)
        return False

    return True


async def check_voice(ctx: commands.Context) -> bool:
    embed = _get_embed()

    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await embed.send_info_embed(ctx, "Information", MSG_NO_VOICE)
        return False

    return True
