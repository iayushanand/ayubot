# -------- import(s) -------- #

import sys

import discord
import psutil
from discord.ext import commands
from utils.helper import Verification
from ext.view import VerificationView

class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mongo = bot.mongo["codedb"]

    def get_cpu_usage(self):
        return psutil.cpu_percent()

    def get_ram_usage(self):
        used = psutil.virtual_memory().used // 1048576
        total = psutil.virtual_memory().total // 1048576
        return f"{round(used)}MB / {round(total)}MB"

    def get_disk_usage(self):
        used = psutil.disk_usage("/").used // 1073741824
        total = psutil.disk_usage("/").total // 1073741824
        return f"{round(used, 2)}GB / {round(total, 2)}GB"

    def get_ram_usage_percent(self):
        return psutil.virtual_memory().percent

    def get_disk_usage_percent(self):
        return psutil.disk_usage("/").percent

    def get_python_version(self):
        return sys.version

    def get_discord_version(self):
        return discord.__version__

    @commands.command(name="botstats", help="Get bot stats")
    @commands.has_permissions(administrator=True)
    async def botstats(self, ctx):
        embed = discord.Embed(title="Bot Stats", color=discord.Color.green())
        embed.add_field(
            name="<:CPU:1016016795909488651> CPU Usage",
            value=f"```{self.get_cpu_usage()}%```",
            inline=False,
        )
        embed.add_field(
            name="<:memory:1016016586584363079> Memory Usage",
            value=f"```{self.get_ram_usage_percent()}%```",
            inline=False,
        )
        embed.add_field(
            name="<:disk:1016016616271650946> Disk Usage",
            value=f"```{self.get_disk_usage_percent()}%```",
            inline=False,
        )
        embed.add_field(
            name="<:python:1016025084789530714> Python Version",
            value=f"```{self.get_python_version()}```",
            inline=False,
        )
        embed.add_field(
            name="<a:discordspin:942445611473596459> Discord Version",
            value=f"```{self.get_discord_version()}```",
            inline=False,
        )
        embed.add_field(
            name="<a:api_latency:1016016946594058321> Latency",
            value=f"```{round(self.bot.latency * 1000)}ms```",
            inline=False,
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.reply(embed=embed)

    @commands.command(name="upload-code")
    @commands.is_owner()
    async def upload_code(self, ctx: commands.Context, title: str, url: str):
        await self.mongo.insert_one({"title": title, "url": url})
        await ctx.reply(
            "Uploaded the code on [website](<https://ayuitz.vercel.app/codes>)!"
        )

    @commands.command(name="verification-button")
    @commands.is_owner()
    async def verify_button(self, ctx: commands.Context):
        await ctx.send(content="# Click button below to verify!",view=VerificationView(self.bot))



async def setup(bot: commands.Bot):
    await bot.add_cog(Owner(bot))
