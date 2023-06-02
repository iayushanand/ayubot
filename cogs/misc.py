# ------------------ imports ------------------ #

import discord
from discord import app_commands
from discord.ext import commands


class Misc(commands.Cog):
    """
    A cog containing miscellaneous commands.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Returns a pong message.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Misc(bot))
