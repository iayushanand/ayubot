import os

import discord
from colorama import Style
from discord.ext import commands
from dotenv import load_dotenv

from ext import consts, view
from utils import botdb

load_dotenv()


class AyuBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=consts.BOT_COMMAND_PREFIX,
            intents=consts.INTENTS,
            case_insensitive=True,
            status=consts.BOT_STATUS,
            activity=consts.BOT_ACTIVITY,
            guild=discord.Object(consts.GUILD_ID),
        )
        self.cog_list = os.listdir("./cogs")
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"

    async def load_cogs(self):
        for cog in self.cog_list:
            if cog.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{cog[:-3]}")
                    print("\033[38;2;166;227;161m" + f"Loaded {cog[:-3]} cog")
                except Exception as e:
                    print("\033[38;2;243;139;168m" + f"{e}")
        await self.load_extension("jishaku")
        print("\033[38;2;166;227;161m" + f"Loaded jishaku cog")

    async def on_ready(self):
        self.db = await botdb.connection()
        self.mongo = await botdb.mongo_connection()

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
        self.add_view(view=view.Ban_Appeal(bot=self))
