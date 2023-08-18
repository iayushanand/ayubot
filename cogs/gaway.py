# ---------- import(s) ----------

import discord
from discord.ext import commands

import asyncpg
from datetime import datetime

import time
import pytimeparser
from ext.view import GiveawayView

class Giveaways(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: asyncpg.Connection = bot.db
        super().__init__()
    
    @commands.command(name="gstart")
    # ------------ add a role check --------------
    async def gstart(self, ctx: commands.Context):
        questions =  [
            "Which channel should giveaway be hosted in?",
            "How long should the giveaway last?",
            "How many winners should be there in giveaway?(1-10)",
            "What should be the prize of the giveaway?"
        ]
        answers = []
        og_message = await ctx.reply("Answer Questions:")
        msg = await ctx.send("** **")
        for ques in questions:
            try:
                await msg.edit(content=f"**{ques}**")
                reply = await self.bot.wait_for("message", check = lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30)
            except TimeoutError:
                await msg.delete()
                await og_message.edit(content='**Timeout**, be quicker next time')
            else:
                await reply.delete()
                answers.append(reply.content)
            
            channel = self.bot.get_channel(int(answers[0][2:-1]))
            end = int(time.time()+pytimeparser.parse(answers[1]).total_seconds())
            winner = answers[2]
            prize = answers[3]
        
        await msg.delete()

        embed = discord.Embed(
            description = "**New Giveaway 🎉**",
            color = 0xffffff,
            timestamp = datetime.utcnow()
        ).add_field(
            name = "Prize:",
            value = prize,
            inline = False
        ).add_field(
            name = "Host:",
            value = ctx.author.mention,
            inline = False
        ).add_field(
            name = "Winners:",
            value = winner,
            inline = False
        ).add_field(
            name = "Ends:",
            value = f"<t:{end}:F> (<t:{end}:R)",
            inline = False
        )

        message = await channel.send(embed = embed, view = GiveawayView(self.bot))
        await self.db.execute("INSERT INTO gaway VALUES ($1, $2, $3, $4, $5, $6)", channel.id, "", message.id, prize, end, winner)
        await og_message.edit(content="**Giveaway Started!**")


async def setup(bot: commands.Bot):
    await bot.add_cog(Giveaways(bot))