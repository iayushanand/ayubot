# ======================= TEST PHASE ======================= #
import os

from dotenv import load_dotenv

from ext.models import AyuBot

load_dotenv()

bot = AyuBot()
bot.run(os.getenv("token"))
