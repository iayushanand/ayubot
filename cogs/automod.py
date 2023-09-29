"""
I made a new cog as I am aiming to make fairly complex auto mod system 
so I thought it's better to have them in one single file
"""

import time

import aiohttp
import discord
from discord.ext import commands

from utils.helper import generate_id


class Automod(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = bot.db

    def get_banned_words(self):
        return open("asset/misc/banned_words.txt").read().lower().split(", ")

    def filter_words(self, filter_words: str, message: str) -> str:
        for word in filter_words:
            word_length = len(word) // 2
            stars = "\*" * word_length
            message = message.replace(word, f"{stars}{word[word_length:]}")
        return message

    async def send_new_message(
        self, channel: discord.TextChannel, message: discord.Message
    ):
        webhook = await channel.create_webhook(name=message.author.display_name)
        data = data = {
            "message": message.content,
            "avatar_url": message.author.display_avatar.url,
            "webhook_url": webhook.url,
        }
        # I have hosted my own api on my website server because my host was raising 1015
        url = "https://ayuitz.vercel.app/sendwebhook"
        async with aiohttp.ClientSession() as session:
            response = await session.post(url=url, json=data)
        if not response.status == 200:
            await channel.send(
                embed=discord.Embed(description=message.content).set_author(
                    name=message.author.display_name,
                    icon_url=message.author.display_avatar.url,
                )
            )

    async def auto_warn(self, member: discord.Member, *, reason: str):
        _id = await generate_id(self.db, "warns")
        await self.db.execute(
            "INSERT INTO warns VALUES($1, $2, $3, $4, $5)",
            _id,
            member.id,
            reason,
            int(time.time()),
            self.bot.user.id,
        )

    @commands.Cog.listener(name="on_message")
    async def check_messages(self, message: discord.Message):
        banned_words = self.get_banned_words()
        found_words = []
        # words check
        for word in banned_words:
            if word.lower() in message.content.lower().split():
                found_words.append(word)
        member = message.author
        reason = "Used Banned word(s): `" + " ".join(found_words) + "`"
        if len(found_words) != 0:
            await self.auto_warn(member=member, reason=reason)
        new_content = self.filter_words(banned_words, message.content.lower())
        if not message.content.lower() == new_content.lower():
            await message.delete()
            message.content = new_content
            channel = message.channel
            await self.send_new_message(channel=channel, message=message)


async def setup(bot: commands.Bot):
    await bot.add_cog(Automod(bot=bot))
