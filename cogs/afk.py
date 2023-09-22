# ---------- import(s) ----------
from time import time

import asyncpg
import discord
from discord.ext import commands


class AFK(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: asyncpg.Connection = bot.db

    @commands.command(name="afk", help="Sets your afk status.")
    async def afk(self, ctx: commands.Context, *, reason: str = None):
        reason = reason or "AFK"
        res = await self.db.fetch(
            "SELECT afk_reason FROM afk WHERE user_id = $1", ctx.author.id
        )
        if len(res) != 0:  # if user is already afk
            await ctx.reply(f"You are already AFK: {res[0].get('afk_reason')}")
            return
        await self.db.execute(
            "INSERT INTO afk VALUES ($1, $2, $3)", ctx.author.id, reason, int(time())
        )
        try:
            await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}")
        except discord.Forbidden:
            pass  # type: ignore
        await ctx.reply(
            embed=discord.Embed(
                description="I set your AFK! " + reason, color=discord.Color.green()
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(AFK(bot))
