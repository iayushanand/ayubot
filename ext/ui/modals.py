import discord
from discord.interactions import Interaction
from discord.ui import Modal, TextInput

from ext.ui import view
from datetime import datetime
from discord.ext import commands

class UserHelpModal(Modal):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None, title="User Help")
        self.bot = bot
        self.add_item(
            TextInput(
                label = "Language",
                placeholder = "Coding Language you need help in",
                required = True,
                style = discord.TextStyle.short,
                max_length=10
            )
        )
        self.add_item(
            TextInput(
                label = "Topic",
                placeholder = "Help Topic",
                required = True,
                style = discord.TextStyle.short,
                max_length = 40
            )
        )
        self.add_item(
            TextInput(
                label = "Details",
                style = discord.TextStyle.long,
                placeholder = "Give meaningful and sufficient points on your problem",
                required = True,
                min_length = 20,
                max_length = 500
            )
        )
        self.add_item(
            TextInput(
                label = "Code",
                style = discord.TextStyle.long,
                placeholder = "Paste code, if any also wrap it in ```lang ```",
                required = False,
                max_length = 1990
            )
        )
        self.add_item(
            TextInput(
                label = "Error",
                style = discord.TextStyle.long,
                placeholder = "Paste error, if any also wrap it in ```lang ```",
                required = False,
                max_length = 1990
            )
        )
    
    async def on_submit(self, interaction: Interaction) -> None:
        embed = discord.Embed(
            color = discord.Color.random(),
            timestamp = datetime.utcnow()
        ).set_author(
            name = interaction.user.name,
            icon_url = interaction.user.avatar.url
        ).add_field(
            name = "Language:",
            value = self.children[0].value,
            inline = False
        ).add_field(
            name = "Topic:",
            value = self.children[1].value,
            inline = False
        ).add_field(
            name = "Description:",
            value = self.children[2].value,
            inline = False
        )
        await interaction.response.send_message("Join thread to get help!",ephemeral=True)
        msg=await interaction.channel.send(embed=embed)
        await interaction.channel.send(
            embed=discord.Embed(
                description="Get Help by clicking the button below!",
                color=discord.Color.og_blurple()),
                view=view.UserHelpView(self.bot)
            )
        thread = await msg.create_thread(
            name=self.children[1].value
        )
        await interaction.message.delete()
        await thread.send(
            interaction.user.mention,
            embed=discord.Embed(
                description="Our helpers will be here soon!\nPlease don't ping anyone.",
                color=discord.Color.blurple()
            )
        )
        await thread.send(
            f"Code:\n{self.children[3].value}"
        )
        await thread.send(
            f"Error:\n{self.children[4].value}"
        )
