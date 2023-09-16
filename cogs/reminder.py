import time

import discord
from discord.ext import commands
from pytimeparser import parse

from ext.consts import TICK_EMOJI
from utils.helper import generate_id


class Reminder(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = bot.db

    @commands.command(name="remind", invoke_without_command=True)
    async def remind(self, ctx: commands.Context, _time: str, *, reminder: str):
        unique_id = await generate_id(self.db, "reminder")
        user_id = ctx.author.id
        ttime = int(time.time() + parse(_time).total_seconds())
        message = reminder

        await self.db.execute(
            "INSERT INTO reminder VALUES ($1,$2,$3,$4)",
            unique_id,
            user_id,
            ttime,
            message,
        )

        await ctx.reply(
            embed=discord.Embed(
                description=TICK_EMOJI + f"I will remind at <t:{ttime}:F>: {message}"
            )
        )

    @commands.command(name="reminder")
    async def reminder(self, ctx: commands.Context):
        user_id = ctx.author.id
        res = await self.db.fetch("SELECT * FROM reminder WHERE user_id = $1", user_id)
        if len(res) == 0:
            return await ctx.reply(
                embed=discord.Embed(
                    description=":x: You don't have any upcoming reminders",
                    color=discord.Color.red(),
                )
            )
        embed = discord.Embed(color=discord.Color.blurple(), description="")
        for i, _ in enumerate(res):
            unique_id = res[i].get("unique_id")
            _t = res[i].get("time")
            message = res[i].get("message")
            embed.description = (
                embed.description + f"`{unique_id}` - {message} (<t:{_t}:R>)\n"
            )
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Reminder(bot=bot))
