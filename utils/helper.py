# -------------- import(s) ---------------

import datetime as dt
import string
from io import BytesIO
from typing import Tuple
import contextlib


import aiohttp
import discord
from cbvx import iml
from discord.ext import commands
from easy_pil import Canvas, Editor
from PIL import Image, ImageChops, ImageDraw, ImageFont


def circle(pfp, size=(110, 110)):
    pfp = pfp.resize(size, Image.ANTIALIAS).convert("RGBA")

    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)
    return pfp


def make_banner(av, bg, lvl, xp, req, text, color, color2):
    percent = round(xp / req * 100)

    if xp >= 1000:
        xp = f"{round(xp/1000,1)}K"
    else:
        xp = round(xp)
    if req >= 1000:
        req = f"{round(req/1000,1)}K"
    else:
        req = round(req)

    sub = f"Level: {lvl}   XP : {xp}/{req}"

    font1 = ImageFont.truetype("asset/fonts/font.otf", 44)
    font2 = ImageFont.truetype("asset/fonts/font.otf", 38)
    pfp = Image.open(av)
    # bg     = Image.open(bg)

    pfp = circle(pfp)
    bg = bg.crop((0, 0, 800, 200))
    bg.paste(pfp, (15, 15), pfp)
    draw = ImageDraw.Draw(bg)
    draw.text((148, 20), text, color2, font1)
    draw.text((148, 75), sub, color2, font2)
    bg = Editor(bg)
    bg.rectangle((10, 150), width=630, height=34, fill=color2, radius=20)
    bg.bar(
        (10, 150), max_width=630, height=34, fill=color, radius=20, percentage=percent
    )
    bg.rectangle((145, 75), width=256, height=3, fill=color)
    border = Canvas((400, 400), color=color)
    border = Editor(border)
    border.rotate(45.0, expand=True)
    bg.paste(border, (531, -290))

    return bg


def get_xp(content: str, multiplier: float) -> float:
    return round(len(content) * multiplier, 2)


# This code is directly taken and modified from The-Coding-Realm/coding-bot-v6
# https://github.com/The-Coding-Realm/coding-bot-v6
class Spotify:
    __slots__ = ("member", "bot", "embed", "regex", "headers", "counter")

    def __init__(self, *, bot, member) -> None:
        """
        Class that represents a Spotify object, used for creating listening embeds
        Parameters:
        ----------------
        bot : commands.Bot
            represents the Bot object
        member : discord.Member
            represents the Member object whose spotify listening is to be handled
        """
        self.member: discord.Member | discord.User = member
        self.bot: commands.Bot = bot
        self.counter = 0

    @staticmethod
    def pil_process(pic: BytesIO, name, artists, time, time_at, track) -> discord.File:
        """
        Makes an image with spotify album cover with Pillow

        Parameters:
        ----------------
        pic : BytesIO
            BytesIO object of the album cover
        name : str
            Name of the song
        artists : list
            Name(s) of the Artists
        time : int
            Total duration of song in xx:xx format
        time_at : int
            Total duration into the song in xx:xx format
        track : int
            Offset for covering the played bar portion
        Returns
        ----------------
        discord.File
            contains the spotify image
        """

        # Resize imput image to 300x300
        # TODO: Remove hardcoded domentions frpm cbvx
        d = Image.open(pic).resize((300, 300))
        # Save to a buffer as PNG
        buffer = BytesIO()
        d.save(buffer, "png")
        buffer.seek(0)
        # Pass raw bytes to cbvx.iml (needs to be png data)
        csp = iml.Spotify(buffer.getvalue())
        # Spotify class has 3 config methods - rate (logarithmic rate of interpolation),
        #  contrast, and shift (pallet shift)
        csp.rate(0.55)  # Higner = less sharp interpolation
        csp.contrast(20.0)  # default, Higner = more contrast
        csp.shift(0)  # default
        # _ is the bg color (non constrasted), we only care about foreground color
        _, fore = csp.pallet()
        fore = (fore.r, fore.g, fore.b)
        # We get the base to write text on
        result = csp.get_base()
        base = Image.frombytes("RGB", (600, 300), result)

        font0 = ImageFont.truetype("asset/fonts/spotify.ttf", 35)  # For title
        font2 = ImageFont.truetype("asset/fonts/spotify.ttf", 18)  # Time stamps

        draw = ImageDraw.Draw(
            base,
        )
        draw.rounded_rectangle(
            ((50, 230), (550, 230)),
            radius=1,
            fill=tuple(map(lambda c: int(c * 0.5), fore)),
        )  # play bar
        draw.rounded_rectangle(
            ((50, 230 - 1), (int(50 + track * 500), 230 + 1)),
            radius=1,
            fill=fore,
        )  # pogress
        draw.ellipse(
            (int(50 + track * 500) - 5, 230 - 5, int(50 + track * 500) + 5, 230 + 5),
            fill=fore,
            outline=fore,
        )  # Playhead
        draw.text((50, 245), time_at, fore, font=font2)  # Current time
        draw.text((500, 245), time, fore, font=font2)  # Total duration
        draw.text((50, 50), name, fore, font=font0)  # Track name
        draw.text((50, 100), artists, fore, font=font2)  # Artists

        output = BytesIO()
        base.save(output, "png")
        output.seek(0)
        return discord.File(fp=output, filename="spotify.png")

    async def get_from_local(self, bot, act: discord.Spotify) -> discord.File:
        """
        Makes an image with spotify album cover with Pillow

        Parameters:
        ----------------
        bot : commands.Bot
            represents our Bot object
        act : discord.Spotify
            activity object to get information from
        Returns
        ----------------
        discord.File
            contains the spotify image
        """
        s = tuple(f"{string.ascii_letters}{string.digits}{string.punctuation} ")
        artists = ", ".join(act.artists)
        artists = "".join([x for x in artists if x in s])
        artists = f"{artists[:36]}..." if len(artists) > 36 else artists
        time = act.duration.seconds
        time_at = (
            dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc) - act.start
        ).total_seconds()
        track = time_at / time
        time = f"{time // 60:02d}:{time % 60:02d}"
        time_at = (
            f"{int((time_at if time_at > 0 else 0) // 60):02d}:"
            f"{int((time_at if time_at > 0 else 0) % 60):02d}"
        )
        pog = act.album_cover_url
        name = "".join([x for x in act.title if x in s])
        name = name[0:21] + "..." if len(name) > 21 else name
        async with aiohttp.ClientSession() as session:
            rad = await session.get(pog)
            rad = await rad.read()
        pic = BytesIO(rad)
        return self.pil_process(pic, name, artists, time, time_at, track)

    async def get_embed(self) -> Tuple[discord.Embed, discord.File, discord.ui.View]:
        """
        Creates the Embed object

        Returns
        ----------------
        Tuple[discord.Embed, discord.File]
            the embed object and the file with spotify image
        """
        activity = discord.utils.find(
            lambda activity: isinstance(activity, discord.Spotify),
            self.member.activities,
        )
        if not activity:
            return False
        url = activity.track_url
        image = await self.get_from_local(self.bot, activity)
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                url=url,
                style=discord.ButtonStyle.green,
                label="\u2007Open in Spotify",
                emoji="<:spotify:983984483755765790>",
            )
        )
        return (image, view)


class WelcomeBanner():
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.font = {
            48: ImageFont.truetype("asset/fonts/font.ttf", 48)
        }
    
    async def create_banner(self, member: discord.Member):
        banner = Image.open("asset/imgs/banner.png")
        heading = f"Welcome to {member.guild.name}"

        draw = ImageDraw.Draw(banner)
        # 120, 15
        draw.text((120, 15), heading, fill="#000000", font=self.font[48])
        # 160, 230 image

        # 320, 125 name
        draw.text((320, 125), member.name, fill="#000000", font=self.font[48])


        inviter = await self.bot.tracker.fetch_inviter(member)
        invites = None
        vanity = None
        if inviter:
            invites = sum(
                i.uses
                for i in (await member.guild.invites())
                if i.inviter and i.inviter.id == inviter.id
            )
        else:
            vanity = await member.guild.vanity_invite()
        
        if invites:
            invite_message = f"Invited by: {(inviter.name[0:10]+'...') if len(inviter.name)>10 else vanity} ({invites} uses) "
        if vanity:
            invite_message = f"Vanity Invite: {(vanity[0:10]+'...') if len(vanity)>10 else vanity}"
        print(invite_message)





        with BytesIO() as image_binary:
            banner.save(image_binary, "PNG")
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename="welcome.png")
            return file