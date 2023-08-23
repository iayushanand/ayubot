# ------------- import(s) ------------- #

import asyncpg
import discord
from discord.ext import commands

from utils.helper import get_xp


class Listeners(commands.Cog):
    """
    cog consisting of all event listeners
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: asyncpg.Connection = bot.db
        self.bot.level_cache: list = []

    @commands.Cog.listener(name="on_message")
    async def _afk_setup(self, message: discord.Message):
        if message.author.bot:
            return
        res = await self.db.fetch(
            "SELECT afk_reason FROM afk WHERE user_id = $1", message.author.id
        )
        if len(res) != 0:
            await self.db.execute(
                "DELETE FROM afk WHERE user_id = $1", message.author.id
            )
            await message.reply(
                f"Welcome back {message.author.mention}! I removed your AFK status."
            )
            try:
                await message.author.edit(nick=message.author.display_name[5:])
            except discord.Forbidden:
                pass
        if message.mentions:
            for user in message.mentions:
                res = await self.db.fetch(
                    "SELECT afk_reason, time FROM afk WHERE user_id = $1", user.id
                )
                if len(res) != 0:
                    await message.reply(
                        f"{user.display_name} is AFK: {res[0].get('afk_reason')} (<t:{res[0].get('time')}:R>)"
                    )

    @commands.Cog.listener(name="on_message")
    async def generate_level_cache(self, message: discord.Message):
        if message.author.bot:
            return
        for user_data in self.bot.level_cache:
            if message.author.id == user_data[0]:
                current_xp = user_data[1]
                new_xp = get_xp(message.content, 0.1) + current_xp
                self.bot.level_cache.remove(user_data)
                self.bot.level_cache.append((user_data[0], new_xp))
                print(self.bot.level_cache)
                return

        self.bot.level_cache.append((message.author.id, get_xp(message.content, 0.1)))
        print(self.bot.level_cache)


async def setup(bot: commands.Bot):
    await bot.add_cog(Listeners(bot))
