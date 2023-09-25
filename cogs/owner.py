# -------- import(s) -------- #

import sys

import discord
import psutil
from discord.ext import commands

from ext.consts import DISCORD_SPIN_EMOJI, STAFF_LIST_CHANNEL, TICK_EMOJI
from ext.view import StaffApplyView, VerificationView


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
        await ctx.send(
            content="# Click the button below to verify!",
            view=VerificationView(self.bot),
        )

    @commands.command(name="update-staff-list")
    @commands.has_permissions(administrator=True)
    async def update_staff_list(self, ctx: commands.Context):
        staff_list_channel = self.bot.get_channel(STAFF_LIST_CHANNEL)
        mod_roles = [
            809642412535971882,
            810108284073017384,
            809642414423801916,
            809744895350407168,
            809756163214147665,
            983229059259588608,
            809756162962620448,
            809756164019322890,
            919243964647895071,
        ]
        embed = discord.Embed(title="**Staff List**", color=0xFFFFFF)
        embed.description = ""
        all_members = []
        for role in mod_roles:
            role = ctx.guild.get_role(role)
            valid_members = [
                member for member in ctx.guild.members if role in member.roles
            ]
            embed.description += f"\n\n{role.mention} | **{len(role.members)}**"
            for member in valid_members:
                if not member.id in all_members:
                    embed.description += f"\n- {member.mention} - `{member.id}`"
                    all_members.append(member.id)

        await staff_list_channel.purge(limit=1)
        await staff_list_channel.send(embed=embed)
        staff_role = ctx.guild.get_role(1000072283282477158)
        count = len(staff_role.members)
        await staff_list_channel.edit(topic=f"Staff Count: {count}")
        await ctx.reply(
            embed=discord.Embed(description=TICK_EMOJI + "updated staff list")
        )

    @commands.command(name="staff-form")
    @commands.is_owner()
    async def staff_form(self, ctx: commands.Context):
        embed = discord.Embed(title="**Staff Form**", color=discord.Color.blue())
        embed.description = f"## Requirements\n- {DISCORD_SPIN_EMOJI} You must follow Discord ToS and Privacy Policy\n- {DISCORD_SPIN_EMOJI} You must have 2fa enabled\n- {DISCORD_SPIN_EMOJI} You need to be above level 5 in server\n- {DISCORD_SPIN_EMOJI} You should have a good and clean record on this server\n\n## Note\nFilling up the form will require 4-5 minutes so make sure got enough time in your hand"
        await ctx.send(embed=embed, view=StaffApplyView(bot=self.bot))


async def setup(bot: commands.Bot):
    await bot.add_cog(Owner(bot))
