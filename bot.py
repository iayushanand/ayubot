# ======================= TEST PHASE ======================= #

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os


load_dotenv()

bot = commands.Bot(command_prefix='!')

bot.run()