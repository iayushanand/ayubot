# -------------- import(s) ---------------

import random
import time

import asyncpg
import discord
from discord.ext import commands, tasks

from ext.consts import GENERAL_CHAT_ID


class TaskCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: asyncpg.Connection = bot.db

    async def cog_load(self) -> None:
        self.set_slowmode.start()
        self.giveaway_end.start()
        self.send_bump_message.start()

    @tasks.loop(minutes=1)
    async def set_slowmode(self):
        channel: discord.TextChannel = self.bot.get_channel(GENERAL_CHAT_ID)
        if self.bot.msgs > 30 and channel.slowmode_delay == 0:
            await channel.edit(slowmode_delay=2)
            await channel.send(
                embed=discord.Embed(
                    description=f"<:tick:966707201064464395> Slowmode set for **2s** because chat is fast!",
                    color=discord.Color.green(),
                )
            )
        if self.bot.msgs < 30 and channel.slowmode_delay > 0:
            await channel.edit(slowmode_delay=0)
            await channel.send(
                embed=discord.Embed(
                    description=f"<:tick:966707201064464395> Slowmode set for **0s** because chat is fast!",
                    color=discord.Color.green(),
                )
            )
        self.bot.msgs = 0

    @tasks.loop(minutes=1)
    async def giveaway_end(self):
        res = await self.db.fetch(
            "SELECT * FROM gaway WHERE time <= $1", int(time.time())
        )
        if len(res) == 0:
            return
        channel = self.bot.get_channel(int(res[0].get("channel_id")))
        message_id = int(res[0].get("message_id"))
        message = await channel.fetch_message(message_id)
        if not message:
            return await self.db.execute(
                "DELETE FROM gaway WHERE message_id = $1", message_id
            )
        prize = res[0].get("prize")
        win_count = res[0].get("winners")
        raw_entries = res[0].get("joins")
        entries = [entry for entry in raw_entries.split(", ") if entry]
        if not (len(entries) >= win_count):
            await message.edit(
                embeds=[
                    message.embeds[0],
                    discord.Embed(
                        description="Giveaway Cancelled!\nReason: Not enough entries.",
                        color=discord.Color.red(),
                    ),
                ],
                view=None,
            )
            return await self.db.execute(
                "DELETE FROM gaway WHERE message_id = $1", message_id
            )
        win_message = ""
        for i in range(win_count):
            winner = random.choice(entries)
            entries.remove(winner)
            win_message = win_message + f"<@{winner}> "

        new_embed = (
            discord.Embed(
                description="Giveaway Ended!",
                color=discord.Color.green(),
            )
            .add_field(name="Prize:", value=prize, inline=False)
            .add_field(name="Winner(s):", value=win_message, inline=False)
        )

        await message.edit(embed=new_embed, view=None)

        await message.reply(
            content=f"Giveaway Winners ({win_message}), please open a ticket to claim the prize!"
        )
        return await self.db.execute(
            "DELETE FROM gaway WHERE message_id = $1", message_id
        )

    @tasks.loop(seconds=10)
    async def send_bump_message(self):
        with open(
            "bumper.txt",
            "r"
        ) as f:
            content = f.read()
            in_list = content.split(
                ", "
            )
        try:
            if int(in_list[1]) <= int(time()):
                channel = await self.bot.get_channel(
                    int(
                        in_list[2]
                    )
                )
                await channel.send(
                    embed=discord.Embed(
                        description="Bump Available Now.",
                        color=discord.Color.green()
                    )
                )
                with open(
                    "bumper.txt",
                    "w"
                ) as f:
                    f.write(
                        "000"
                    )
        except IndexError:
            pass



async def setup(bot: commands.Bot):
    await bot.add_cog(TaskCog(bot=bot))
