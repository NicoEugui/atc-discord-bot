import asyncio
import logging

import discord
from discord.ext import commands

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True


async def main() -> None:
    if not Config.PLS_FILE.exists():
        logger.critical("PLS_FILE '%s' does not exist. Exiting.", Config.PLS_FILE)
        return

    bot = commands.Bot(command_prefix=Config.PREFIX, intents=intents)

    @bot.event
    async def on_ready() -> None:
        logger.info("Bot is ready. Logged in as %s", bot.user)

    await bot.load_extension("cogs.radio")
    await bot.start(Config.DISCORD_TOKEN_BOT)


if __name__ == "__main__":
    asyncio.run(main())
