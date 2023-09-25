# ------------- import(s) ------------- #

import asyncio
from datetime import datetime
from time import time

import asyncpg
import discord
from discord.ext import commands

from ext.consts import (BAN_FORM_CHANNEL, BUMPER_ROLE, DEFAULT_LEVEL_IMAGE,
                        GENERAL_CHAT_ID, GUILD_BOOST_ROLE, LEVEL_PRIMARY_COLOR,
                        LEVEL_SECONDARY_COLOR, LOG_CHANNEL_ID,
                        WELCOME_CHANNEL_ID)
from ext.view import Ban_Appeal
from utils.helper import WelcomeBanner, get_xp


class Listeners(commands.Cog):
    """
    cog consisting of all event listeners
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: asyncpg.Connection = bot.db
        self.bot.msgs: int = 0

    @commands.Cog.listener(name="on_message")
    async def _afk_setup(self, message: discord.Message):
        if message.author.bot:
            return
        res = await self.db.fetch(
            "SELECT afk_reason FROM afk WHERE user_id = $1", message.author.id
        )
        if len(res) != 0 and not message.content.startswith(self.bot.command_prefix[0]):
            await self.db.execute(
                "DELETE FROM afk WHERE user_id = $1", message.author.id
            )
            await message.reply(
                embed=discord.Embed(
                    description=f"Welcome back {message.author.mention}! I removed your AFK status.",
                    color=discord.Color.blurple(),
                ),
                delete_after=5,
            )
            try:
                await message.author.edit(
                    nick=message.author.name.removeprefix("[AFK]").strip()
                )
            except discord.Forbidden:
                pass
        if message.mentions:
            for user in message.mentions:
                res = await self.db.fetch(
                    "SELECT afk_reason, time FROM afk WHERE user_id = $1", user.id
                )
                if len(res) != 0:
                    await message.reply(
                        embed=discord.Embed(
                            description=f"{user.display_name} is AFK: {res[0].get('afk_reason')} (<t:{res[0].get('time')}:R>)",
                            color=discord.Color.yellow(),
                        )
                    )

    @commands.Cog.listener()
    async def on_reaction_add(self, react: discord.Reaction, user: discord.Member):
        msg = react.message
        if user.guild_permissions.manage_messages:
            if str(react.emoji) != "📌":
                return
            await msg.pin(reason=f"Pinned by {user.name}#{user.discriminator}")
            em = (
                discord.Embed(
                    title="",
                    description="📌 Pinned a message",
                    color=discord.Color.dark_teal(),
                )
                .add_field(name="Pin request by:", value=user.mention)
                .add_field(
                    name="Jump URL", value=f"[click here]({react.message.jump_url})"
                )
            )
            logc = self.bot.get_channel(LOG_CHANNEL_ID)
            await logc.send(embed=em)

    @commands.Cog.listener()
    async def on_reaction_remove(self, react: discord.Reaction, user: discord.Member):
        msg = react.message
        if user.guild_permissions.manage_messages:
            if str(react.emoji) != "📌":
                return
            await msg.unpin(
                reason=f"Pinned Removed by {user.name}#{user.discriminator}"
            )
            em = (
                discord.Embed(
                    title="",
                    description="📌 Unpinned a message",
                    color=discord.Color.dark_teal(),
                )
                .add_field(name="Unpin request by:", value=user.mention)
                .add_field(
                    name="Jump URL", value=f"[click here]({react.message.jump_url})"
                )
            )
            logc = self.bot.get_channel(LOG_CHANNEL_ID)
            await logc.send(embed=em)

    @commands.Cog.listener(name="on_message")
    async def level_cache(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        bumper_role = message.guild.get_role(BUMPER_ROLE)
        booster = message.guild.get_role(GUILD_BOOST_ROLE)
        xp = (
            0.3
            if booster in message.author.roles
            else 0.2
            if bumper_role in message.author.roles
            else 0.1
        )
        user_data = [message.author.id, get_xp(message.content, xp)]
        res = await self.db.fetch(
            "SELECT level, xp FROM level WHERE user_id = $1", user_data[0]
        )
        if len(res) == 0:
            await self.db.execute(
                "INSERT INTO level VALUES ($1, $2, $3, $4, $5, $6)",
                user_data[0],
                user_data[1],
                1,
                DEFAULT_LEVEL_IMAGE,
                LEVEL_PRIMARY_COLOR,
                LEVEL_SECONDARY_COLOR,
            )
        else:
            level = res[0].get("level")
            xp = res[0].get("xp")
            new_xp = xp + user_data[1]
            if new_xp > level * 100:
                await self.db.execute(
                    "UPDATE level SET xp=0, level=level+1 WHERE user_id = $1",
                    user_data[0],
                )
                await message.channel.send(
                    embed=discord.Embed(
                        description=f"<:upvote:810082923381784577> <@{user_data[0]}> has reached level **{level+1}**. GG!",
                        color=discord.Color.og_blurple(),
                    )
                )
                # I may try do this in a simpler way but I am feeling sleepy rn so will fix it later
                for lev in range(level):
                    for role in message.guild.roles:
                        if f"「 Level {lev} + 」" in role.name:
                            await message.author.add_roles(role)
                            break
                return
            await self.db.execute(
                "UPDATE level SET xp=xp+$1 WHERE user_id = $2",
                user_data[1],
                user_data[0],
            )

    @commands.Cog.listener(name="on_message")
    async def autoslowmode(self, message: discord.Message):
        if message.channel.id == GENERAL_CHAT_ID:
            self.bot.msgs += 1

    @commands.Cog.listener(name="on_message")
    async def ban_appeal(self, message: discord.Message):
        if (
            not message.webhook_id == 1021724997061976074
            or message.author.id == self.bot.user.id
            or not message.channel.id == BAN_FORM_CHANNEL
        ):
            return
        try:
            await message.delete()
        except:
            pass  # type: ignore
        embed = message.embeds[0]
        user = await self.bot.fetch_user(int(embed.description))
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
        await message.channel.send(embed=embed, view=Ban_Appeal(self.bot))

    @commands.Cog.listener(name="on_member_update")
    async def boost_message(self, before, after: discord.Member):
        # role: discord.Role = after.guild.premium_subscriber_role <- # NOTE: this will work for every server
        role = after.guild.get_role(GUILD_BOOST_ROLE)
        if role in after.roles and not role in before.roles:
            em = (
                discord.Embed(
                    description=f"<a:boost:983636359686279168> Thank you for boosting **{after.guild.name}**!\n\n",
                    color=discord.Color.nitro_pink(),
                )
                .add_field(
                    name="** **",
                    value="We are at **{}** boosts!".format(
                        after.guild.premium_subscription_count
                    ),
                )
                .add_field(
                    name="** **",
                    value="We are boost level: **{}**".format(after.guild.premium_tier),
                )
                .set_thumbnail(
                    url="https://c.tenor.com/HIqZKBb8sHgAAAAi/discord-boost-yellow-boost.gif"
                )
            )
            await after.guild.system_channel.send(content=f"{after.mention}", embed=em)

    @commands.Cog.listener(name="on_message")
    async def bump_handler(self, message: discord.Message):
        if not message.guild:
            return
        bump_role = message.guild.get_role(BUMPER_ROLE)
        author = message.author

        if (
            message.author.id == 302050872383242240
            and "Bump done" in message.embeds[0].description
            and message.interaction
        ):
            await message.delete()
            await asyncio.sleep(0.5)
            user: discord.Member = message.guild.get_member(message.interaction.user.id)

            with open("bumper.txt", "w") as f:
                f.write(f"{user.id}, {int(time()+(2*60*60))}, {message.channel.id}")

            await user.add_roles(bump_role)

            embed = discord.Embed(
                description="Bump Done!\nThanks for bumping.\nYou have been given {0} role, it will boost your message xp gain by 200% for 2 hours.".format(
                    bump_role.mention
                ),
                color=discord.Color.og_blurple(),
                timestamp=datetime.utcnow(),
            )

            await message.channel.send(content=user.mention, embed=embed)

            return
        if message.author.bot:
            return
        if bump_role in author.roles:
            with open("bumper.txt", "r") as f:
                data = f.read().split(", ")
            if not author.id == int(data[0]):
                await author.remove_roles(bump_role)
                return

    @commands.Cog.listener(name="on_member_join")
    async def welcome_message(self, member: discord.Member):
        banner = await WelcomeBanner(self.bot).create_banner(member=member)
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        await channel.send(file=banner)


async def setup(bot: commands.Bot):
    await bot.add_cog(Listeners(bot))
