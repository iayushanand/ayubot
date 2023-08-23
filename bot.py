# ======================= TEST PHASE ======================= #

import os
from colorama import Fore, Style

from dotenv import load_dotenv

from ext import models, view
from utils import botdb

load_dotenv()

bot = models.AyuBot()

bot.db: None

cog_list = os.listdir("./cogs")


async def load_cogs():
    for cog in cog_list:
        if cog.endswith(".py"):
            await bot.load_extension(f"cogs.{cog[:-3]}")
            print(Fore.GREEN + f"Loaded {cog[:-3]} cog")
            print(Style.RESET_ALL, end="\r")

@bot.event
async def on_ready():
    bot.db = await botdb.connection()
    # await botdb.delete_table(bot.db, 'gaway') # -- for testing purpose --
    # await botdb.create_table(bot.db)
    print(Style.BRIGHT)
    print(Fore.YELLOW + f"{bot.user.name} has connected to Discord!")
    print(Fore.YELLOW + f"Latency: {round(bot.latency*1000)} ms")
    print()
    await load_cogs()
    await bot.tree.sync()
    bot.add_view(view=view.GiveawayView(bot=bot))
    


bot.run(os.getenv("token"))
