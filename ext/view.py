import discord
from discord.ext import commands
from discord.ui import Button, View, button


class GiveawayView(View):
    def __init__(self, bot: commands.Bot):
        self.db = bot.db
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
            "SELECT joins FROM gaway WHERE message = $1", interaction.message.id
        )
        entries = res[0].get("joins")
        print(entries)
        if str(interaction.author.id) in entries:
            await interaction.followup.send(
                "You are already enrolled in giveaway, Press this button to leave",
                ephemeral=True,
                view=Roll(),
            )


class Roll(View):
    def __init__(self, bot: commands.Bot):
        self.db = bot.db
        super().__init__(timeout=60)

    @button(
        label="Leave Giveaway",
        custom_id="leavegawaybutton",
        style=discord.ButtonStyle.danger,
        emoji="❌",
    )
    async def leave(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("WIP", ephemeral=True)
