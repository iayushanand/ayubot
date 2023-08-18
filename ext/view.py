import discord
from discord.ext import commands
from discord.ui import Button, View, button
import asyncpg

class GiveawayView(View):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: asyncpg.Connection = bot.db
        super().__init__(timeout=None)

    @button(
        label="Enter Giveaway",
        custom_id="gawaybutton",
        style=discord.ButtonStyle.blurple,
        emoji="🎉",
    )
    async def enter(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        res = await self.db.fetch(
            "SELECT joins FROM gaway WHERE message_id = $1", interaction.message.id
        )
        entries = res[0].get("joins")
        if str(interaction.user.id) in entries:
            await interaction.followup.send(
                "You are already enrolled in giveaway, Press this button to leave",
                ephemeral=True,
                view=Roll(self.bot),
            )
        else:
            users = entries.split(", ")
            users.append(str(interaction.user.id))
            entries = ", ".join(users)
            await self.db.execute("UPDATE gaway SET joins = $1 WHERE message_id = $2", entries, interaction.message.id)
            await interaction.followup.send(
                embed = discord.Embed(
                    description = "You joined this giveaway!",
                    color = discord.Color.green()
                ),
                ephemeral = True
            )


class Roll(View):
    def __init__(self, bot: commands.Bot):
        self.db: asyncpg.Connection = bot.db
        super().__init__(timeout=30)

    @button(
        label="Leave Giveaway",
        custom_id="leavegawaybutton",
        style=discord.ButtonStyle.danger,
    )
    async def leave(self, interaction: discord.Interaction, button: Button):
        res = await self.db.fetch("SELECT joins FROM gaway WHERE message_id = $1", interaction.message.reference.message_id)
        entries = res[0].get('joins')
        users = entries.split(", ")
        users.remove(str(interaction.user.id))
        entries = ", ".join(users)
        await self.db.execute("UPDATE gaway SET joins = $1 WHERE message_id = $2", entries, interaction.message.reference.message_id)
        await interaction.response.edit_message(
            embed = discord.Embed(
                description = "Removed you from giveawawy!",
                color = discord.Color.red()
            ),
            view = None
        )

