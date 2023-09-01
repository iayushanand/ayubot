from typing import Optional
import asyncpg
import discord
from discord.ext import commands
from discord.ui import Button, View, button



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
            await self.db.execute(
                "UPDATE gaway SET joins = $1 WHERE message_id = $2",
                entries,
                interaction.message.id,
            )
            await interaction.followup.send(
                embed=discord.Embed(
                    description="You joined this giveaway!", color=discord.Color.green()
                ),
                ephemeral=True,
            )


class Ban_Appeal(View):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mongo = bot.mongo["bandb"]
        super().__init__(timeout=None)
    
    @button(label="Unban", style=discord.ButtonStyle.green, custom_id="unbanbtn")
    async def unban_user(self, interaction: discord.Interaction, button: Button):
        embed = interaction.message.embeds[0]
        user = await self.bot.fetch_user(int(embed.description))
        await self.mongo.delete_one({"_id": f"{user.id}"})
        try:
                await interaction.guild.unban(user,
                reason="Unbanned by {}".format(
                    interaction.user)
                )
        except:
            await interaction.response.send_message(embed=discord.Embed(
                title="User already Unbaned!",
                color=discord.Color.yellow()),
                ephemeral=True)
            embed.color = discord.Color.yellow()
            embed.set_footer(
                text=f"Not in Ban List"
            )
            await interaction.message.edit(embed=embed,
                view=None
            )
        else:
            await interaction.response.send_message(embed=discord.Embed(
                title="Unbanned",
                description=f"**{user}** has been unbanned",
                color=discord.Color.green()),
                ephemeral=True
            )
            embed.color = discord.Color.green()
            embed.set_footer(text="Unbanned by {}".format(
                interaction.user),
                icon_url=interaction.user.display_avatar
            )
            await interaction.message.edit(embed=embed, view=None)
    

    @button(label="Reject", custom_id="reject", style=discord.ButtonStyle.blurple)
    async def delete(self, interaction: discord.Interaction, button: Button):
        embed = interaction.message.embeds[0]
        user: discord.User = await self.bot.fetch_user(int(embed.description))
        await self.mongo.delete_one({"_id": f"{user.id}"})
        await interaction.response.send_message(embed=discord.Embed(title="Rejected",
            description="Appeal has been deleted",
            color=discord.Color.red()),
            ephemeral=True
        )
        embed.color = discord.Color.red()
        embed.set_footer(
            text="Rejected by {}".format(
            interaction.user),
            icon_url=interaction.user.display_avatar)
        await interaction.message.edit(
            embed=embed,
            view=None
        )

    @button(label="Block", custom_id="block", style=discord.ButtonStyle.red)
    async def block(self, interaction: discord.Interaction, button: Button):
        embed = interaction.message.embeds[0]
        user = await self.bot.fetch_user(int(embed.description))
        embed.color = discord.Color.blurple()
        await self.mongo.update_one({"_id": f"{user.id}"}, { "$set": { 'status': "banned" }})
        embed.set_footer(
            text=f"Blocked by: {interaction.user}",
            icon_url=interaction.user.display_avatar
        )
        await interaction.message.edit(
            embed=embed,
            view=None
        )
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Blocked",
                description="Appeal has been blocked",
                color=discord.Color.blurple()
            ),
            ephemeral=True
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
        res = await self.db.fetch(
            "SELECT joins FROM gaway WHERE message_id = $1",
            interaction.message.reference.message_id,
        )
        entries = res[0].get("joins")
        users = entries.split(", ")
        users.remove(str(interaction.user.id))
        entries = ", ".join(users)
        await self.db.execute(
            "UPDATE gaway SET joins = $1 WHERE message_id = $2",
            entries,
            interaction.message.reference.message_id,
        )
        await interaction.response.edit_message(
            embed=discord.Embed(
                description="Removed you from giveawawy!", color=discord.Color.red()
            ),
            view=None,
        )
