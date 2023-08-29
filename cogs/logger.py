from datetime import datetime

import discord
from discord.ext import commands

from ext.consts import LEAVE_MESSAGE_CHANNEL_ID, LOG_CHANNEL_ID


class Logs(commands.Cog):
    """
    A cog to handle all the member logs
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log = self.bot.get_channel(LOG_CHANNEL_ID)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        embed = (
            discord.Embed(
                title="Member Joined!",
                description=f"{member.mention}",
                timestamp=datetime.utcnow(),
                color=discord.Color.random(),
            )
            .set_thumbnail(url=member.display_avatar)
            .set_footer(text="id: {0}".format(member.id))
        )
        await self.log.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return
        embed = (
            discord.Embed(
                title="Member Left!",
                description=f"{member.mention}",
                timestamp=datetime.utcnow(),
                color=discord.Color.random(),
            )
            .set_thumbnail(url=member.display_avatar)
            .set_footer(text="id: {0}".format(member.id))
        )
        await self.log.send(embed=embed)
        embed = discord.Embed(
            description=f"**{member}** left the server. Hope they will not get there dinner today <:Bruh:811480176868327437>",
            color=discord.Color.dark_theme(),
        )
        await self.bot.get_channel(LEAVE_MESSAGE_CHANNEL_ID).send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, member):
        if member.bot:
            return
        embed = (
            discord.Embed(
                title="Member Banned!",
                description=f"{member.mention}",
                timestamp=datetime.utcnow(),
                color=discord.Color.random(),
            )
            .set_thumbnail(url=member.display_avatar)
            .set_footer(text="id: {0}".format(member.id))
        )
        await self.log.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, member):
        if member.bot:
            return
        embed = (
            discord.Embed(
                title="Member Unbanned!",
                description=f"{member.mention}",
                timestamp=datetime.utcnow(),
                color=discord.Color.random(),
            )
            .set_thumbnail(url=member.display_avatar)
            .set_footer(text="id: {0}".format(member.id))
        )
        await self.log.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after: discord.Member):
        if before.bot:
            return
        if before.nick != after.nick:
            embed = (
                discord.Embed(
                    title="Member Nickname Changed!",
                    timestamp=datetime.utcnow(),
                    color=discord.Color.random(),
                )
                .set_thumbnail(url=before.display_avatar)
                .set_footer(text="id: {0}".format(before.id))
                .add_field(name="Before", value="{0}".format(before.nick))
                .add_field(name="After", value=f"{after.nick}")
            )
            await self.log.send(embed=embed)
        if before.roles != after.roles:
            embed = (
                discord.Embed(
                    title="Member Role Changed!",
                    timestamp=datetime.utcnow(),
                    color=discord.Color.random(),
                )
                .set_thumbnail(url=before.display_avatar)
                .set_footer(text="id: {0}".format(before.id))
                .add_field(
                    name="Before",
                    value="{0}".format(
                        ",".join(role.mention for role in before.roles[1:])
                    ),
                )
                .add_field(
                    name="After",
                    value=f"{','.join(role.mention for role in after.roles[1:])}",
                )
            )
            await self.log.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        embed = (
            discord.Embed(
                title="Message Deleted!",
                description=f"{message.author.mention} deleted a message in {message.channel.mention}",
                timestamp=datetime.utcnow(),
                color=discord.Color.random(),
            )
            .set_thumbnail(url=message.author.display_avatar)
            .set_footer(text="id: {0}".format(message.author.id))
            .add_field(name="** **", value=message.content)
        )
        await self.log.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        if before.content != after.content:
            embed = (
                discord.Embed(
                    title="Message Edited!",
                    description=f"{before.author.mention} edited a message in {before.channel.mention}",
                    timestamp=datetime.utcnow(),
                    color=discord.Color.random(),
                )
                .set_thumbnail(url=before.author.display_avatar)
                .set_footer(text="id: {0}".format(before.author.id))
                .add_field(name="Before", value=before.content)
                .add_field(name="After", value=after.content)
            )
            await self.log.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Logs(bot))
