import discord
from dotenv import load_dotenv

load_dotenv()

# ---------------------- bot ---------------------- #

INTENTS = discord.Intents.all()

BOT_COMMAND_PREFIX = "!"

BOT_STATUS = discord.Status.idle

BOT_ACTIVITY = discord.Activity(
    type=discord.ActivityType.watching, name="my development"
)

GENERAL_CHAT_ID = 809642450935218216

LOG_CHANNEL_ID = 1000070843449217175

LEAVE_MESSAGE_CHANNEL_ID = 809642446899380254

# ---------------------- db ---------------------- #

AFK_CONFIG_SCHEMA = """
CREATE TABLE IF NOT EXISTS afk (
        user_id BIGINT,
        afk_reason TEXT,
        time BIGINT
    )
"""

GIVEAWAY_CONFIG_SCHEMA = """
CREATE TABLE IF NOT EXISTS gaway (
        channel_id BIGINT,
        message_id BIGINT,
        time BIGINT,
        prize TEXT,
        winners INTEGER,
        joins TEXT
    )
"""

LEVELLING_CONFIG_SCHEMA = """
CREATE TABLE IF NOT EXISTS level (
        user_id BIGINT,
        xp FLOAT,
        level INTEGER,
        img_url TEXT,
        prim_col TEXT,
        sec_col TEXT
    )
"""
