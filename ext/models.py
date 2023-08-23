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
                    print(Fore.GREEN + f"Loaded {cog[:-3]} cog")
                except Exception as e:
                    print(Fore.RED + f"{e}")
                print(Style.RESET_ALL, end="\r")

    async def on_ready(self):
        self.db = await botdb.connection()
        # await botdb.delete_table(bot.db, 'gaway') # -- for testing purpose --
        # await botdb.create_table(bot.db)
        print(Style.BRIGHT)
        print(Fore.YELLOW + f"{self.user.name} has connected to Discord!")
        print(Fore.YELLOW + f"Latency: {round(self.latency*1000)} ms")
        print()
        await self.load_cogs()
        await self.tree.sync()
        self.add_view(view=view.GiveawayView(bot=self))
