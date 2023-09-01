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

# ----------------------- config ---------------------- #

GENERAL_CHAT_ID = 809642450935218216

LOG_CHANNEL_ID = 1000070843449217175

LEAVE_MESSAGE_CHANNEL_ID = 809642446899380254

DEFAULT_LEVEL_IMAGE = "https://images.unsplash.com/photo-1571096896260-3836f7afaf4f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1374&q=80"

LEVEL_PRIMARY_COLOR = "#9422e6"

LEVEL_SECONDARY_COLOR = "#9b9a9c"

BAN_FORM_CHANNEL = 1019616803804151921