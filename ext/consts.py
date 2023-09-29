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

WARNING_CONFIG_SCHEMA = """
CREATE TABLE IF NOT EXISTS warns (
        unique_id BIGINT,
        user_id BIGINT,
        reason TEXT,
        time BIGINT,
        moderator BIGINT
    )
"""

TODO_CONFIG_SCHEMA = """
CREATE TABLE IF NOT EXISTS todo (
        unique_id BIGINT,
        user_id BIGINT,
        time BIGINT,
        task TEXT
)
"""

REMINDER_CONFIG_SCHEMA = """
CREATE TABLE IF NOT EXISTS reminder (
        unique_id BIGINT,
        user_id BIGINT,
        time BIGINT,
        message TEXT
)
"""

# ----------------------- config ---------------------- #

GENERAL_CHAT_ID = 809642450935218216

LOG_CHANNEL_ID = 1000070843449217175

COMMANDS_CHANNEL_ID = 809642453505933312

WELCOME_CHANNEL_ID = 809642450935218216

STAFF_LIST_CHANNEL = 983610422412337172

LEAVE_MESSAGE_CHANNEL_ID = 809642446899380254

DEFAULT_LEVEL_IMAGE = "https://wallpaperaccess.com/full/2200497.jpg"

LEVEL_PRIMARY_COLOR = "#9422e6"

LEVEL_SECONDARY_COLOR = "#9b9a9c"

VERIFICATION_ROLE_ID = 809642429744414730

BAN_FORM_CHANNEL = 1019616803804151921

BUMPER_ROLE = 1147265527778128042

TICK_EMOJI = "<:tick:966707201064464395> "

TODO_ARROW_EMOJI = "<a:arrow_arrow:993887543873507328> "

VERIFICATION_BUTTON_EMOJI = "<a:verify:942444862484131920>"

VERIFICATION_MESSAGE_EMOJI = "<a:done:942447861075968000>"

BADGES_EMOJI = "<a:badges:942447265744842762>"

LOADING_EMOJI = "<a:loading:1155575800280653945>"

DISCORD_SPIN_EMOJI = "<a:discordspin:942445611473596459>"

STAFF_BADGES_EMOJI = "<:Staff:1083757009880502273>"

GUILD_ID = 809456664084348972

GUILD_BOOST_ROLE = 852950166968991795

REQUIRED_STAFF_APPLY_ROLE = 810419731638386698

STAFF_FORM_CHANNEL = 1000071870609109062

TRIAL_MOD_ROLE = 809756164019322890

STAFF_ROLE = 1000072283282477158

ANNOUNCE_EMOJI = "<a:announce:942623347886420000>"

OPEN_TICKET_CATEGOARY = 1000072064574701568

CLOSE_TICKET_CATEGOARY = 1000072177875419216

TICKET_LOGS_CHANNEL = 1000072784938025060
