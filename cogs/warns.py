# -------------- import(s) ------------- #

from time import time

import discord
from discord.ext import commands

from ext.consts import TICK_EMOJI
from utils.helper import generate_id


class Warns(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db

    @commands.command(name="warn")
    @commands.has_permissions(manage_channels=True)
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        _id = await generate_id(self.db, "warns")
        await self.db.execute(
            "INSERT INTO warns VALUES($1, $2, $3, $4, $5)",
            _id,
            member.id,
            reason,
            int(time()),
            ctx.author.id,
        )
        embed = discord.Embed(
            description=f"{TICK_EMOJI} warned {member.mention}",
            color=discord.Color.green(),
        )
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command(name="warns")
    @commands.has_permissions(kick_members=True)
    async def warns(self, ctx: commands.Context, member: discord.Member):
        res = await self.db.fetch("SELECT * FROM warns WHERE user_id = $1", member.id)
        if len(res) == 0:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"No active warns found for {member.mention}",
                    color=discord.Color.red(),
                )
            )
        warn_count = len(res)
        embed = discord.Embed(
            description=f"{member.mention} has {str(warn_count)+' warns' if warn_count>1 else str(warn_count)+' warn'}",
            color=discord.Color.blurple(),
        )
        for count, warn in enumerate(res):
            embed.add_field(
                name=f"Warn #{count+1}",
                value=f"id: {warn.get('unique_id')}\nreason: {warn.get('reason')}\ntime: <t:{warn.get('time')}:F>\n mod: <@{warn.get('moderator')}>",
            )
        await ctx.reply(embed=embed)

    @commands.command(name="clearwarn", aliases=["cw"])
    @commands.has_permissions(manage_guild=True)
    async def cwarn(self, ctx: commands.Context, member: discord.Member):
        await self.db.execute("DELETE FROM warns WHERE user_id = $1", (member.id))
        embed = discord.Embed(
            description=f"{TICK_EMOJI} cleared warns for {member.mention}",
            color=discord.Color.green(),
        )
        await ctx.reply(embed=embed)

    @commands.command(name="delwarn", aliases=["dw"])
    @commands.has_permissions(manage_guild=True)
    async def delwarn(self, ctx: commands.Context, unique_id: int):
        await self.db.execute("DELETE FROM warns WHERE unique_id = $1", int(unique_id))
        embed = discord.Embed(
            description=f"{TICK_EMOJI} deleted warn with id: `{unique_id}`",
            color=discord.Color.green(),
        )
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Warns(bot=bot))
