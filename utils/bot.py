from ast import Num
import logging
import logging.handlers
from aiohttp import ClientSession
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

from typing import Dict, List, Optional

import discord
from discord.ext import commands

class ModBot(commands.Bot):
    def __init__(
        self,
        *args,
        initial_cogs: List[str],
        client: ClientSession,
        debug: bool = False,
        testing_guild_id: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.client = client
        self.debug = debug
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_cogs
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("discord")
        logger.setLevel(logging.INFO)
        time = datetime.datetime.now()
        handler = logging.handlers.RotatingFileHandler(
        filename=f"logs/{time.strftime('%Y-%m-%d')}.log",
        encoding="utf-8", 
        mode="a", 
        maxBytes=10 * 1024 * 1024, 
        backupCount=5)
        handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
        logger.addHandler(handler)

    async def setup_hook(self) -> None:

        for extension in self.initial_extensions:
            await self.load_extension(f"cogs.{extension}")
        await self.load_extension('jishaku')

        # if debug is enabled, then don't sync slash commands
        if not self.debug:
           try:
            logging.info("Syncing slash commands...")
            await self.tree.sync()
            logging.info("Slash commands synced!")
           except Exception as e:
            logging.error("Failed to sync slash commands.")
            logging.error(e)
        else:
            pass

async def main():
    intents = discord.Intents.default()
    intents.members = True
    intents.emojis = True
    intents.emojis_and_stickers = True
    intents.bans = True
    intents.webhooks = True
    ext = ['moderation', 'errors', 'config', 'level', 'info', 'case', 'ticket']
    async with ClientSession() as server_client:
     async with ModBot(debug=False, command_prefix="!", allowed_mentions=discord.AllowedMentions(everyone=False, roles=True, users=True, replied_user=True),  activity=discord.Game("Working on it"), client=server_client, intents=intents, help_command=None, initial_cogs=ext) as bot:
      token = os.getenv("DISCORD_TOKEN")
      await bot.start(f"{token}", reconnect=True)