import asyncio
import time

import asyncpg
import discord
from discord.ext import commands
from discord.ui import Button, View, button

from ext.consts import *
from ext.ui import modals
from utils.helper import Verification, get_transcript, upload


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
            await interaction.guild.unban(
                user, reason="Unbanned by {}".format(interaction.user)
            )
        except:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="User already Unbaned!", color=discord.Color.yellow()
                ),
                ephemeral=True,
            )
            embed.color = discord.Color.yellow()
            embed.set_footer(text=f"Not in Ban List")
            await interaction.message.edit(embed=embed, view=None)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Unbanned",
                    description=f"**{user}** has been unbanned",
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )
            embed.color = discord.Color.green()
            embed.set_footer(
                text="Unbanned by {}".format(interaction.user),
                icon_url=interaction.user.display_avatar,
            )
            await interaction.message.edit(embed=embed, view=None)

    @button(label="Reject", custom_id="reject", style=discord.ButtonStyle.blurple)
    async def delete(self, interaction: discord.Interaction, button: Button):
        embed = interaction.message.embeds[0]
        user: discord.User = await self.bot.fetch_user(int(embed.description))
        await self.mongo.delete_one({"_id": f"{user.id}"})
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Rejected",
                description="Appeal has been deleted",
                color=discord.Color.red(),
            ),
            ephemeral=True,
        )
        embed.color = discord.Color.red()
        embed.set_footer(
            text="Rejected by {}".format(interaction.user),
            icon_url=interaction.user.display_avatar,
        )
        await interaction.message.edit(embed=embed, view=None)

    @button(label="Block", custom_id="block", style=discord.ButtonStyle.red)
    async def block(self, interaction: discord.Interaction, button: Button):
        embed = interaction.message.embeds[0]
        user = await self.bot.fetch_user(int(embed.description))
        embed.color = discord.Color.blurple()
        await self.mongo.update_one(
            {"_id": f"{user.id}"}, {"$set": {"status": "banned"}}
        )
        embed.set_footer(
            text=f"Blocked by: {interaction.user}",
            icon_url=interaction.user.display_avatar,
        )
        await interaction.message.edit(embed=embed, view=None)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Blocked",
                description="Appeal has been blocked",
                color=discord.Color.blurple(),
            ),
            ephemeral=True,
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


class VerificationView(View):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__(timeout=None)

    @button(
        label="Verify",
        style=discord.ButtonStyle.blurple,
        custom_id="verificationbutton",
        emoji=VERIFICATION_BUTTON_EMOJI,
    )
    async def verify(self, interaction: discord.Interaction, button: discord.Button):
        try:
            text, image = Verification().get_image()
            dm_msg = await interaction.user.send(
                content=VERIFICATION_MESSAGE_EMOJI + " Enter Captcha: ", file=image
            )
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + "Check your dms!",
                    color=discord.Color.blurple(),
                ),
                ephemeral=True,
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=":x: Please turn on your dms!",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
            return

        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: interaction.user == m.author and not m.guild,
                timeout=30,
            )

        except asyncio.TimeoutError:
            await interaction.user.send(
                embed=discord.Embed(
                    description=":x: Timeout! Please try again.",
                    color=discord.Color.red(),
                ),
                delete_after=5,
            )
            await dm_msg.edit(
                content=None,
                attachments=[],
                embed=discord.Embed(
                    description=":x: Verification Failed!", color=discord.Color.red()
                ),
            )
        else:
            if msg.content.lower() == text.lower():
                role = interaction.guild.get_role(VERIFICATION_ROLE_ID)
                await interaction.user.add_roles(role)
                await interaction.user.send(
                    embed=discord.Embed(
                        description=TICK_EMOJI + "You're verified!",
                        color=discord.Color.green(),
                    ),
                    delete_after=5,
                )
                await dm_msg.edit(
                    content=None,
                    attachments=[],
                    embed=discord.Embed(
                        description=TICK_EMOJI + "Verification Success!",
                        color=discord.Color.green(),
                    ),
                )
            else:
                await interaction.user.send(
                    embed=discord.Embed(
                        color=discord.Color.red(), description=":x: Invalid Captcha!"
                    ),
                    delete_after=5,
                )
                await dm_msg.edit(
                    content=None,
                    attachments=[],
                    embed=discord.Embed(
                        description=":x: Verification Failed!",
                        color=discord.Color.red(),
                    ),
                )


class StaffApplyView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @button(
        label="Apply",
        style=discord.ButtonStyle.blurple,
        custom_id="staffapply",
        emoji=STAFF_BADGES_EMOJI,
    )
    async def apply_button(
        self,
        interaction: discord.Interaction,
        button: discord.Button,
        emoji=BADGES_EMOJI,
    ):
        questions = [
            [
                "How old are you?",
                "How many servers are you moderating?",
                "Why do you want to moderate this server?",
                "What is your timezone?",
                "How long can you moderate in a day",
                "Do you have any previous expreince moderating any server?, If yes describe your expreince.",
                "What is 2+2?",
            ],
            [
                "What will you do when 7 people joins the server within 30 seconds?",
                "What will you do when chat is very fast and it's getting hard to moderate?",
                "What if someone is doing client modification?",
                "You suspect a member changing status very fast, whats happening there? What could be your action?",
                "How will you prevent a raid?",
                "Someone is spamming in the server, describe your action?",
                "Why should we choose you and not someone else?",
            ],
            [
                "Your Speciality",
                "Describe yourself in 3 words.",
                "Descrie server in 3 words.",
            ],
        ]
        required_role = interaction.guild.get_role(REQUIRED_STAFF_APPLY_ROLE)
        if not required_role in interaction.user.roles:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    description=":x: You do not meet the minimum requirement to fill up this form.",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
        try:
            og_message = await interaction.user.send(
                content=LOADING_EMOJI + " **Fetching Questions**"
            )
        except discord.Forbidden:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    description=":x: Turn on your dms", color=discord.Color.red()
                ),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + " Check your dms",
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )
        await og_message.edit(
            embed=discord.Embed(
                color=discord.Color.random(),
                description="Answer the following questions:",
            ),
            content=None,
        )
        embed = discord.Embed()
        sset = []
        for count, sets in enumerate(questions):
            answers = []
            for qc, ques in enumerate(sets):
                embed.description = f"**{count+1}/{qc+1} - {ques}**"
                embed.color = discord.Color.random()
                await interaction.user.send(embed=embed)

                try:
                    ans = await self.bot.wait_for(
                        "message",
                        check=lambda m: not m.guild and m.author == interaction.user,
                        timeout=60,
                    )
                except asyncio.TimeoutError:
                    await interaction.user.send(
                        embed=discord.Embed(
                            description=":x: Timeout!", color=discord.Color.red()
                        )
                    )
                    return
                else:
                    answers.append(ans.content)
            sset.append(answers)

        embed = discord.Embed(
            description=f"`{interaction.user.id}` - {interaction.user.mention} filled up the staff form!",
            color=discord.Color.yellow(),
        ).set_thumbnail(url=interaction.user.display_avatar.url)

        for count, sett in enumerate(sset):
            for qc, ans in enumerate(sett):
                embed.add_field(
                    name=f"{count+1}/{qc+1} - {questions[count][qc]}",
                    value=ans,
                    inline=False,
                )

        channel = self.bot.get_channel(STAFF_FORM_CHANNEL)
        await channel.send(embed=embed, view=StaffProcessView(bot=self.bot))
        await interaction.user.send(
            embed=discord.Embed(
                description=TICK_EMOJI
                + "Form submitted, you will recieve a dm if you are selected in staff.",
                color=discord.Color.green(),
            )
        )


class StaffProcessView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @button(label="Accept", style=discord.ButtonStyle.green, custom_id="acceptstaff")
    async def accept(self, interaction: discord.Interaction, button: discord.Button):
        user = interaction.guild.get_member(748053138354864229)
        print(interaction.message.content)
        role_ids = [TRIAL_MOD_ROLE, STAFF_ROLE]
        roles = [interaction.guild.get_role(role) for role in role_ids]
        await user.add_roles(roles[0], roles[1])
        await interaction.response.send_message(
            embed=discord.Embed(
                description=TICK_EMOJI + f"accepted {user.mention} as staff!",
                color=discord.Color.green(),
            )
        )
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.set_footer(
            text=f"Accepted by {interaction.user.name}",
            icon_url=interaction.user.display_avatar.url,
        )
        await interaction.message.edit(embed=embed, view=None)
        try:
            await user.send(
                embed=discord.Embed(
                    description=ANNOUNCE_EMOJI
                    + f"You have been accepted as a staff in **{interaction.guild.name}**!",
                    color=discord.Color.og_blurple(),
                )
            )
        except discord.Forbidden:
            pass  # type: ignore

    @button(label="Reject", style=discord.ButtonStyle.red, custom_id="rejectstaff")
    async def reject(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.send_message(
            embed=discord.Embed(
                description=TICK_EMOJI + "rejected!", color=discord.Color.red()
            )
        )
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.set_footer(
            text=f"Rejected by {interaction.user.name}",
            icon_url=interaction.user.display_avatar.url,
        )
        await interaction.message.edit(embed=embed, view=None)


class SelfRoleView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot


class SelfRoleView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @button(label="Coding Roles", custom_id="codingRoles")
    async def coding_roles(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        await interaction.response.send_message(
            view=CodingRoles(self.bot), ephemeral=True
        )

    @button(label="Gender Roles", custom_id="genderRoles")
    async def gender_roles(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        await interaction.response.send_message(
            view=GenderRoles(self.bot), ephemeral=True
        )

    @button(label="Ping Roles", custom_id="pingRoles")
    async def ping_roles(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        await interaction.response.send_message(
            view=PingRoles(self.bot), ephemeral=True
        )


class CodingRoles(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @button(
        label="Python",
        emoji="<:python:1016025084789530714>",
        style=discord.ButtonStyle.blurple,
    )
    async def cl_py(self, interaction: discord.Interaction, button: discord.Button):
        role: discord.Role = interaction.guild.get_role(1156309813798633572)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} removed!",
                    color=discord.Color.yellow(),
                ),
                ephemeral=True,
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} added!",
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )

    @button(
        label="Javascript",
        emoji="<:JavaScript:1156300862185021482>",
        style=discord.ButtonStyle.blurple,
    )
    async def cl_js(self, interaction: discord.Interaction, button: discord.Button):
        role: discord.Role = interaction.guild.get_role(1156309872455983227)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} removed!",
                    color=discord.Color.yellow(),
                ),
                ephemeral=True,
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} added!",
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )

    @button(
        label="Other",
        emoji="<:code:942623640967577630>",
        style=discord.ButtonStyle.blurple,
    )
    async def cl_ot(self, interaction: discord.Interaction, button: discord.Button):
        role: discord.Role = interaction.guild.get_role(1156309928106012733)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} removed!",
                    color=discord.Color.yellow(),
                ),
                ephemeral=True,
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} added!",
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )


class GenderRoles(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @button(
        label="Male",
        emoji="<a:Male:997896650955694210>",
        style=discord.ButtonStyle.blurple,
    )
    async def gm(self, interaction: discord.Interaction, button: discord.Button):
        role: discord.Role = interaction.guild.get_role(809985079282499594)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} removed!",
                    color=discord.Color.yellow(),
                ),
                ephemeral=True,
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} added!",
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )

    @button(
        label="Female",
        emoji="<a:Female:997896655670087701>",
        style=discord.ButtonStyle.blurple,
    )
    async def gf(self, interaction: discord.Interaction, button: discord.Button):
        role: discord.Role = interaction.guild.get_role(809985239773872138)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} removed!",
                    color=discord.Color.yellow(),
                ),
                ephemeral=True,
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} added!",
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )

    @button(
        label="Non Binary",
        emoji="<:NonBinary:1000042393967542344>",
        style=discord.ButtonStyle.blurple,
    )
    async def go(self, interaction: discord.Interaction, button: discord.Button):
        role: discord.Role = interaction.guild.get_role(1003320420730146896)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} removed!",
                    color=discord.Color.yellow(),
                ),
                ephemeral=True,
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} added!",
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )


class PingRoles(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @button(
        label="QOTD",
        emoji="<a:Ping:1156312660518908048>",
        style=discord.ButtonStyle.blurple,
        row=0,
    )
    async def qotd(self, interaction: discord.Interaction, button: discord.Button):
        role: discord.Role = interaction.guild.get_role(810131877616812062)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} removed!",
                    color=discord.Color.yellow(),
                ),
                ephemeral=True,
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} added!",
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )

    @button(
        label="Poll",
        emoji="<a:Ping:1156312660518908048>",
        style=discord.ButtonStyle.blurple,
        row=0,
    )
    async def poll(self, interaction: discord.Interaction, button: discord.Button):
        role: discord.Role = interaction.guild.get_role(810131946587291668)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} removed!",
                    color=discord.Color.yellow(),
                ),
                ephemeral=True,
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} added!",
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )

    @button(
        emoji="<a:Ping:1156312660518908048>",
        label="Announcements",
        style=discord.ButtonStyle.blurple,
        row=0,
    )
    async def ping(self, interaction: discord.Interaction, button: discord.Button):
        role: discord.Role = interaction.guild.get_role(810131991080992788)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} removed!",
                    color=discord.Color.yellow(),
                ),
                ephemeral=True,
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} added!",
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )

    @button(
        label="Giveaway",
        emoji="<a:Ping:1156312660518908048>",
        style=discord.ButtonStyle.blurple,
        row=1,
    )
    async def gaway(self, interaction: discord.Interaction, button: discord.Button):
        role: discord.Role = interaction.guild.get_role(827041561413287946)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} removed!",
                    color=discord.Color.yellow(),
                ),
                ephemeral=True,
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} added!",
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )

    @button(
        label="Helper",
        emoji="<a:Ping:1156312660518908048>",
        style=discord.ButtonStyle.blurple,
        row=1,
    )
    async def helper(self, interaction: discord.Interaction, button: discord.Button):
        role: discord.Role = interaction.guild.get_role(889014603563032576)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} removed!",
                    color=discord.Color.yellow(),
                ),
                ephemeral=True,
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} added!",
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )

    @button(
        label="Chat Revival",
        emoji="<a:Ping:1156312660518908048>",
        style=discord.ButtonStyle.blurple,
        row=1,
    )
    async def revival(self, interaction: discord.Interaction, button: discord.Button):
        role: discord.Role = interaction.guild.get_role(810132068150673420)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} removed!",
                    color=discord.Color.yellow(),
                ),
                ephemeral=True,
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=TICK_EMOJI + f"{role.mention} added!",
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )


class UserHelpView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="Get Help",
        custom_id="UserHelpButton",
        style=discord.ButtonStyle.blurple,
        emoji="<:developer:942447062476288050>",
    )
    async def gethelp(self, interaction: discord.Interaction, button: discord.Button):
        modal = modals.UserHelpModal(self.bot)
        await interaction.response.send_modal(modal)


class TicketOpenView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @button(
        label="Click Here",
        emoji="🎫",
        style=discord.ButtonStyle.blurple,
        custom_id="ticketopen",
    )
    async def open_ticket(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        category = discord.utils.get(
            interaction.guild.categories, id=OPEN_TICKET_CATEGOARY
        )

        for channel in category.text_channels:
            if channel.topic == interaction.user.id:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        description=f":x:You already have a ticket here ({channel.mention})",
                        color=discord.Color.red(),
                    ),
                    ephemeral=True,
                )

        staff = interaction.guild.get_role(STAFF_ROLE)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(
                read_messages=False
            ),
            staff: discord.PermissionOverwrite(read_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True),
        }

        channel = await category.create_text_channel(
            name="ticket-" + interaction.user.name,
            topic=interaction.user.id,
            overwrites=overwrites,
        )

        await interaction.response.send_message(
            embed=discord.Embed(
                description=TICK_EMOJI + f"ticket created: {channel.mention}",
                color=discord.Color.green(),
            ),
            ephemeral=True,
        )
        em = discord.Embed(
            title="Welcome!",
            description=f"Support will arrive shortly,\nmake sure not to ping anyone.\nFor fast support make sure\nto drop your question before hand.",
            color=discord.Color.dark_blue(),
        ).set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar
        )
        await channel.send(embed=em, view=TicketCloseView(self.bot))


class TranscriptButton(Button):
    def __init__(self, url: str):
        super().__init__(
            style=discord.ButtonStyle.url,
            emoji="<:link:942623752523501678>",
            url=url,
            label="Trasncript",
        )


class PostCloseView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(
        label="Delete Ticket",
        style=discord.ButtonStyle.gray,
        custom_id="delete",
        emoji="🚮",
    )
    async def delete_ticket(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        await interaction.response.send_message("**Deleting Ticket in 5 seconds!**")
        await asyncio.sleep(5)
        await interaction.channel.delete()


class TicketCloseView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @button(label="Close", style=discord.ButtonStyle.red, custom_id="closebtn")
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.Button,
    ):
        await interaction.response.send_message(
            embed=discord.Embed(
                description=TICK_EMOJI + "Closing Ticket", color=discord.Color.green()
            ),
            ephemeral=True,
        )
        await interaction.message.edit(embed=interaction.message.embeds[0], view=None)
        category = discord.utils.get(
            interaction.guild.categories, id=CLOSE_TICKET_CATEGOARY
        )
        channel = interaction.channel
        staff = interaction.guild.get_role(STAFF_ROLE)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(
                read_messages=False
            ),
            staff: discord.PermissionOverwrite(read_messages=True),
        }
        await channel.edit(category=category, overwrites=overwrites)
        await channel.send(
            embed=discord.Embed(
                description=f"Ticked Closed by {interaction.user.mention}",
                color=discord.Color.blurple(),
            ),
            view=PostCloseView(),
        )
        handle = interaction.guild.get_member(int(interaction.channel.topic))
        log_channel = interaction.guild.get_channel(TICKET_LOGS_CHANNEL)

        await get_transcript(member=handle, channel=interaction.channel)
        file_name = upload(f"asset/tickets/{handle.id}.html", handle.name)
        link = f"https://ayuitz.vercel.app/ticket?id={file_name}"
        embed = (
            discord.Embed(
                title="Ticket Closed",
                color=discord.Color.og_blurple(),
            )
            .add_field(name="Opened by:", value=handle.mention, inline=False)
            .add_field(name="Closed by:", value=interaction.user.mention, inline=False)
            .add_field(
                name="Closing Time:", inline=False, value=f"<t:{int(time.time())}:f>"
            )
        )
        view = View(timeout=None)
        view.add_item(TranscriptButton(link))
        log_message = await log_channel.send(embed=embed, view=view)
        embed.add_field(name="Logs:", inline=False, value=log_message.jump_url)
        try:
            await handle.send(embed=embed, view=view)
        except discord.Forbidden:
            pass
