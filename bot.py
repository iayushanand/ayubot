# ======================= TEST PHASE ======================= #

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os


load_dotenv()

bot = commands.Bot(
    command_prefix='!',
    intents=discord.Intents.all(),
    case_insensitive=True,
    status=discord.Status.idle,
    activity=discord.Activity(type=discord.ActivityType.watching, name="my development")
)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(os.getenv('token'))