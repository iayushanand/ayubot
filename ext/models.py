import os

import discord
from colorama import Fore, Style
from discord.ext import commands
from dotenv import load_dotenv

from ext import consts, view
from utils import botdb

load_dotenv()


class AyuBot(commands.Bot):
    def __init__(self):
        self.cog_list = os.listdir("./cogs")
        super().__init__(
            command_prefix=consts.BOT_COMMAND_PREFIX,
            intents=consts.INTENTS,
            case_insensitive=True,
            status=consts.BOT_STATUS,
            activity=consts.BOT_ACTIVITY,
            guild=discord.Object(os.getenv("guild_id")),
        )

    async def load_cogs(self):
        for cog in self.cog_list:
            if cog.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{cog[:-3]}")
                    print("\033[38;2;166;227;161m" + f"Loaded {cog[:-3]} cog")
                except Exception as e:
                    print("\033[38;2;243;139;168m" + f"{e}")

    async def on_ready(self):
        self.db = await botdb.connection()
        # await botdb.delete_table(self.db, 'level') # -- for testing purpose --
        # await botdb.create_table(self.db)
        print()
        await self.load_cogs()
        await self.tree.sync()
        print(Style.BRIGHT)
        print("\033[38;2;249;226;175m" + f"{self.user.name} has connected to Discord!")
        print("\033[38;2;249;226;175m" + f"Latency: {round(self.latency*1000)} ms")
        print(Style.RESET_ALL, end="\r")
        self.add_view(view=view.GiveawayView(bot=self))
