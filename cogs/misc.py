# ------------------ imports ------------------ #

from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from utils.helper import Spotify


class Misc(commands.Cog):
    """
    A cog containing miscellaneous commands.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Returns a pong message.")
    async def ping(self, interaction: discord.Interaction):
        bot_ping = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"{bot_ping} ms")

    @commands.command(aliases=["sm"], name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx: commands.Context, time: int = 0):
        """
        Sets slowmode for the channel
        **Syntax:** +[slowmode|sm] [seconds]
        """
        await ctx.channel.edit(slowmode_delay=time)
        await ctx.reply(
            embed=discord.Embed(
                description=f"<:tick:966707201064464395> Slowmode set for **{time}s**",
                color=discord.Color.green(),
            )
        )

    @commands.command(name="avatar", aliases=["av"], description="""Shows the avatar""")
    async def avatar(self, ctx: commands.Context, user: discord.Member = None):
        user = user or ctx.author
        em = discord.Embed(
            title=" ",
            description=f"Avatar of {user.mention}",
            color=discord.Color.dark_theme(),
        ).set_image(url=user.display_avatar)
        await ctx.reply(embed=em)

    @commands.command(name="whois")
    async def whois(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        hypesquad_class = (
            str(member.public_flags.all())
            .replace("[<UserFlags.", "")
            .replace(">]", "")
            .replace("_", " ")
            .replace(":", "")
            .title()
        )

        # Remove digits from string
        hypesquad_class = "".join([i for i in hypesquad_class if not i.isdigit()])

        if hypesquad_class == "[]":
            hypesquad_class = "None"

        if "Brilliance" in hypesquad_class:
            hypesquad = "<:BrillianceLogo:942444927869136946>"
        elif "Bravery" in hypesquad_class:
            hypesquad = "<:BraveryLogo:942444973872283678>"
        elif "Balance" in hypesquad_class:
            hypesquad = "<:BalanceLogo:942446526813327430>"
        else:
            hypesquad = "None"

        roles = [role for role in member.roles[1:]]
        embed = discord.Embed(
            colour=member.color,
            timestamp=datetime.utcnow(),
            title=f"User Info - {member}",
        )
        embed.set_thumbnail(url=member.display_avatar)

        embed.add_field(name="ID:", value=member.id, inline=True)
        embed.add_field(name="Display Name:", value=member.display_name, inline=True)

        embed.add_field(
            name="Account Created:",
            value=f"<t:{int(datetime.timestamp(member.created_at))}:R>",
            inline=True,
        )
        embed.add_field(
            name="Server Joined:",
            value=f"<t:{int(datetime.timestamp(member.joined_at))}:R>",
            inline=True,
        )

        embed.add_field(
            name="Roles:", value=",".join([role.mention for role in roles]), inline=True
        )
        embed.add_field(
            name="Highest Role:", value=f"{member.top_role.mention}", inline=True
        )

        embed.add_field(name="Hypesquad", value=f"{hypesquad}", inline=True)

        await ctx.reply(embed=embed)

    @commands.command(name="serverinfo", aliases=["sinfo"])
    async def serverinfo(self, ctx):
        guild: discord.Guild = ctx.guild
        embed = discord.Embed(
            colour=guild.me.color,
            timestamp=datetime.utcnow(),
            title=f"Server Info - {guild}",
        )
        embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="ID:", value=guild.id, inline=True)
        embed.add_field(name="Name:", value=guild.name, inline=True)
        embed.add_field(name="Owner:", value=f"{guild.owner}", inline=True)
        embed.add_field(name="Region:", value=guild.region, inline=True)
        embed.add_field(name="Members:", value=f"{guild.member_count}", inline=True)
        embed.add_field(name="Channels:", value=f"{len(guild.channels)}", inline=True)
        embed.add_field(name="Roles:", value=f"{len(guild.roles)}", inline=True)
        embed.add_field(
            name="Created:",
            value=f"{guild.created_at.strftime('%d/%m/%y')}",
            inline=True,
        )
        embed.add_field(
            name="Verification Level:", value=f"{guild.verification_level}", inline=True
        )
        embed.add_field(
            name="Explicit Content Filter:",
            value=f"{guild.explicit_content_filter}",
            inline=True,
        )
        embed.add_field(
            name="AFK Channel:", value=f"{guild.afk_channel.mention}", inline=True
        )
        embed.add_field(name="AFK Timeout:", value=f"{guild.afk_timeout}", inline=True)
        embed.add_field(
            name="System Channel:", value=f"{guild.system_channel.mention}", inline=True
        )

        await ctx.reply(embed=embed)

    @commands.command(name="channelinfo", aliases=["cinfo"])
    async def channelinfo(self, ctx: commands.Context):
        boostemo = "<a:boost:983636359686279168>"
        """View information/statistics about the server."""
        guild = ctx.guild
        assert guild
        creation = ((guild.id >> 22) + 1420070400000) // 1000
        boost_emoji = (
            "<:shiny_boost:1007971330332839996>"
            if guild.premium_subscription_count > 0
            else "<:boost:1007970712977420338>"
        )

        embed = (
            discord.Embed(
                title=guild.name,
                description=f"**ID:** {guild.id}\n\n**Features:**\n"
                + "\n".join(f"- {f.replace('_', ' ').title()}" for f in guild.features),
                color=0x0060FF,
            )
            .add_field(
                name="Members",
                value=f"Total: {guild.member_count}\nBots: {sum(m.bot for m in guild.members)}",
            )
            .add_field(
                name="Time of Creation",
                value=f"<t:{creation}>\n<t:{creation}:R>",
            )
            .add_field(
                name="Channels",
                value=f"Text: {len(guild.text_channels)}\nVoice: {len(guild.voice_channels)}"
                f"\nCategories: {len(guild.categories)}",
            )
            .add_field(
                name="Roles",
                value=f"{len(guild._roles)} roles\nHighest:\n{guild.roles[-1].mention}",
            )
            .add_field(
                name="Boost Status",
                value=f"Level {guild.premium_tier}\n"
                f"{boost_emoji}{guild.premium_subscription_count} boosts",
            )
            .set_footer(
                text=f"Requested by {ctx.author}",
                icon_url=ctx.author.display_avatar.url,
            )
        )
        if owner := guild.owner:
            embed.insert_field_at(0, name="Owner", value=f"{owner}\n{owner.mention}")
        if icon := guild.icon:
            embed.set_thumbnail(url=icon.url)
        await ctx.reply(embed=embed)

    @commands.command(name="joined")
    async def joined(self, ctx: commands.Context, rank: int):
        if rank > ctx.guild.member_count:
            return await ctx.send(
                embed=ctx.error("There are not that many members here")
            )
        all_members = list(ctx.guild.members)
        all_members.sort(key=lambda m: m.joined_at)

        def ord(n):
            return str(n) + (
                "th"
                if 4 <= n % 100 <= 20
                else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
            )

        embed = discord.Embed(
            title=f"The {ord(rank)} person to join is: ",
            description=all_members[rank - 1].mention,
        )
        await ctx.reply(embed=embed)

    @commands.command(name="joinpos")
    async def joinpos(self, ctx: commands.Context, member: discord.Member):
        all_members = list(ctx.guild.members)
        all_members.sort(key=lambda m: m.joined_at)

        def ord(n):
            return str(n) + (
                "th"
                if 4 <= n % 100 <= 20
                else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
            )

        embed = discord.Embed(
            title="Member info",
            description=f"{member.mention} was the {ord(all_members.index(member) + 1)} person to join",
        )
        await ctx.reply(embed=embed)

    @commands.command(name="calc")
    async def calc(self, ctx, *, equation: str):
        try:
            await ctx.reply(
                embed=discord.Embed(
                    description=f"Result: {eval(equation)}", color=0x00FF00
                )
            )
        except Exception as e:
            await ctx.reply(
                embed=discord.Embed(description=f"Error: {e}", color=0xFF0000)
            )

    @commands.command(aliases=["sp"])
    @commands.cooldown(5, 60.0, type=commands.BucketType.user)
    async def spotify(self, ctx: commands.Context, member: discord.Member = None):
        """
        Shows the spotify status of a member.

        Usage:
        ------
        `{prefix}spotify`: *will show your spotify status*
        `{prefix}spotify [member]`: *will show the spotify status of [member]*
        """
        member = ctx.guild.get_member((member or ctx.author).id)

        spotify = Spotify(bot=self.bot, member=member)
        result = await spotify.get_embed()
        if not result:
            if member == ctx.author:
                return await ctx.reply(
                    "You are currently not listening to spotify!", mention_author=False
                )
            return await self.bot.reply(
                ctx,
                f"{member.mention} is not listening to Spotify",
                mention_author=False,
                allowed_mentions=discord.AllowedMentions(users=False),
            )
        file, view = result
        await ctx.send(file=file, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Misc(bot))
