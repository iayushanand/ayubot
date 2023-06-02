# ------------- import(s) ------------- #

import asyncpg
import discord
from discord.ext import commands


class Listeners(commands.Cog):
    """
    cog consisting of all event listeners
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: asyncpg.Connection = bot.db

    @commands.Cog.listener(name="on_message")
    async def _message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.content.startswith("!"):
            return await self.bot.process_commands(message)

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


async def setup(bot: commands.Bot):
    await bot.add_cog(Listeners(bot))
