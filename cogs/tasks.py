# -------------- import(s) ---------------

import random
import time

import asyncpg
import discord
from discord.ext import commands, tasks


class TaskCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: asyncpg.Connection = bot.db

    async def cog_load(self) -> None:
        self.dump_level_data.start()
        self.giveaway_end.start()


    @tasks.loop(seconds=10)
    async def dump_level_data(self):
        print(f"Level Cache: {self.bot.level_cache}")
        for user_data in self.bot.level_cache:
            res = await self.db.fetch(
                "SELECT level, xp FROM level WHERE user_id = $1", user_data[0]
            )
            if len(res) == 0:
                await self.db.execute(
                    "INSERT INTO level VALUES ($1, $2, $3, $4, $5, $6)",
                    user_data[0],
                    user_data[1],
                    1,
                    "https://bit.ly/level-banner",
                    "#00ffff",
                    "#ffffff",
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
                    general = self.bot.get_channel(809642450935218216)
                    await general.send(
                        embed=discord.Embed(
                            description=f"<:upvote:810082923381784577> <@{user_data[0]}> You are now at **{level+1} level** GG!",
                            color=discord.Color.magenta(),
                        )
                    )
                    return
                await self.db.execute(
                    "UPDATE level SET xp=xp+$1 WHERE user_id = $2",
                    user_data[1],
                    user_data[0],
                )
        self.bot.level_cache = []

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


async def setup(bot: commands.Bot):
    await bot.add_cog(TaskCog(bot=bot))
