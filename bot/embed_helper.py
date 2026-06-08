import os
from typing import Optional
from datetime import datetime, timezone

import discord


class EmbedHelper:
    _instance: Optional["EmbedHelper"] = None

    def __new__(cls) -> "EmbedHelper":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self.color: int = 0x6699FF
        self.author_name: str = os.getenv("EMBED_AUTHOR_NAME", "ATC Bot")
        self.thumbnail_url: str = os.getenv("EMBED_THUMBNAIL_URL", "")
        self.author_icon_url: str = os.getenv("EMBED_AUTHOR_ICON_URL", "")
        self.footer_text: str = os.getenv("EMBED_FOOTER_TEXT", "ATC Bot")
        self.footer_icon_url: str = os.getenv("EMBED_FOOTER_ICON_URL", "")

    def create_embed(
        self,
        title: str,
        description: str,
        timestamp: Optional[datetime] = None,
    ) -> discord.Embed:
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        embed = discord.Embed(
            title=title,
            description=description,
            colour=self.color,
            timestamp=timestamp,
        )
        embed.set_author(name=self.author_name, icon_url=self.author_icon_url)
        embed.set_footer(text=self.footer_text, icon_url=self.footer_icon_url)
        embed.set_thumbnail(url=self.thumbnail_url)
        return embed

    async def send_info_embed(
        self,
        ctx: discord.ext.commands.Context,
        title: str,
        description: str,
        timestamp: Optional[datetime] = None,
    ) -> None:
        embed = self.create_embed(title, description, timestamp)
        await ctx.send(embed=embed)

    async def send_error_embed(
        self,
        ctx: discord.ext.commands.Context,
        title: str,
        description: str,
        timestamp: Optional[datetime] = None,
    ) -> None:
        await self.send_info_embed(ctx, title, description, timestamp)
        from logging import getLogger
        getLogger(__name__).error("%s: %s", title, description)
