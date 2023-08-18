from typing import Optional
from discord.ui import View, Button, button
import discord
from discord.ext import commands


class GiveawayView(View):
    def __init__(self, bot: commands.Bot):
        self.db = bot.db
        super().__init__(timeout=None)
    
    @button(label="Enter Giveaway", custom_id="gawaybutton", style=discord.ButtonStyle.blurple, emoji="🎉")
    async def enter(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        res = await self.db.execute("SELECT entries FROM gaway WHERE message = ?", (interaction.message.id))
        entries = await res.fetchone()
        print(entries)
        if str(interaction.author.id) in entries:
            await interaction.followup.send("You are already enrolled in giveaway, Press this button to leave", ephemeral=True, view=Roll())


class Roll(View):
    def __init__(self, bot: commands.Bot):
        self.db = bot.db
        super().__init__(timeout=60)
    
    @button(label="Leave Giveaway", custom_id = "leavegawaybutton", style = discord.ButtonStyle.danger, emoji="❌")
    async def leave(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("WIP", ephemeral=True)