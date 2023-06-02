import discord
from discord.ext import commands

import os
from ext import consts

from dotenv import load_dotenv
load_dotenv()

class AyuBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = consts.BOT_COMMAND_PREFIX,
            intents = consts.INTENTS,
            case_insensitive=True,
            status = consts.BOT_STATUS,
            activity = consts.BOT_ACTIVITY,
            guild=discord.Object(
            os.getenv('guild_id')
        )
    )

