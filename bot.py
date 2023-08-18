# ======================= TEST PHASE ======================= #

import os

from discord.ext import commands
from dotenv import load_dotenv

from ext import models
from utils import botdb

load_dotenv()

bot = models.AyuBot()

bot.db: None

cog_list = os.listdir("./cogs")

async def load_cogs():
    for cog in cog_list:
        if cog.endswith(".py"):
            await bot.load_extension(f"cogs.{cog[:-3]}")
            print(f"Loaded {cog[:-3]} cog")

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")
    print(f"Latency: {round(bot.latency*1000)} ms")
    bot.db = await botdb.connection()
    await botdb.create_table(bot.db)
    # await botdb.delete_table(bot.db, 'afk') # -- for testing purpose --
    # await botdb.create_table(bot.db) # -- for testing purpose --
    await load_cogs()
    await bot.tree.sync()

bot.run(os.getenv("token"))