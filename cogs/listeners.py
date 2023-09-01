# ------------- import(s) ------------- #

import asyncpg
import discord
from discord.ext import commands

from ext.consts import GENERAL_CHAT_ID, LOG_CHANNEL_ID, DEFAULT_LEVEL_IMAGE, LEVEL_PRIMARY_COLOR, LEVEL_SECONDARY_COLOR
from utils.helper import get_xp


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
        user_data = [message.author.id, get_xp(message.content, 0.1)]
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

async def setup(bot: commands.Bot):
    await bot.add_cog(Listeners(bot))
