# -------------- import(s) ---------------

import datetime as dt
import os
import random
import string
import time
from io import BytesIO
from typing import Tuple

import aiohttp
import chat_exporter
import discord
import humanize
from captcha.image import ImageCaptcha
from cbvx import iml
from discord.ext import commands
from dotenv import load_dotenv
from easy_pil import Canvas, Editor
from github import Github
from PIL import Image, ImageChops, ImageDraw, ImageFont

load_dotenv()


def circle(pfp, size=(250, 250)):
    pfp = pfp.resize(size).convert("RGBA")

    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size)
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


class WelcomeBanner:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.font = {
            50: ImageFont.truetype("asset/fonts/font.ttf", 50),
            40: ImageFont.truetype("asset/fonts/font.ttf", 40),
            30: ImageFont.truetype("asset/fonts/font.ttf", 30),
        }
        self.color = {
            "black": "#000000",
            "white": "#ffffff",
            "purple": "#c6a6ff",
            "rosewater": "#f6dbd8",
        }

    async def create_banner(self, member: discord.Member) -> discord.File:
        inviter = None
        async for entry in member.guild.audit_logs(
            action=discord.AuditLogAction.invite_create, limit=1
        ):
            inviter = entry.user
        inv = None
        if inviter:
            inv = sum(
                i.uses
                for i in (await member.guild.invites())
                if i.inviter and i.inviter.id == inviter.id
            )

        heading = f"Welcome to {member.guild.name}"
        banner = Image.open("asset/imgs/welcomebg.png")
        inv_message = f"Invited by: {inviter.name if inviter else 'unknown'} {f'({inv if inv else 0} uses)'}"
        acc_created = f"Created: {humanize.naturaldelta(dt.timedelta(seconds=int(time.time()-member.created_at.timestamp())))} ago"
        data = Image.open(BytesIO(await member.display_avatar.read()))
        pfp = circle(data)

        draw = ImageDraw.Draw(banner)

        draw.text((120, 15), heading, fill=self.color["rosewater"], font=self.font[50])
        draw.text(
            (320, 125), member.name, fill=self.color["rosewater"], font=self.font[50]
        )
        draw.text(
            (320, 180),
            f"({member.id})",
            fill=self.color["rosewater"],
            font=self.font[30],
        )
        draw.text(
            (320, 250), inv_message, fill=self.color["rosewater"], font=self.font[40]
        )
        draw.text(
            (320, 300), acc_created, fill=self.color["rosewater"], font=self.font[40]
        )

        banner.paste(pfp, (40, 100), pfp)

        with BytesIO() as image_binary:
            banner.save(image_binary, "PNG")
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename="welcome.png")
            return file


class Verification:
    def __init__(self) -> None:
        self.string = str(random.randint(10000, 99999))

    def get_image(self) -> [str, discord.File]:
        text = self.string
        image = ImageCaptcha(width=280, height=90)
        data = image.generate(text)
        return text, discord.File(fp=data, filename="verification.png")


async def generate_id(db, table):
    _id = random.randint(100000, 999999)
    while True:
        res = await db.fetch(f"SELECT unique_id FROM {table} WHERE unique_id = $1", _id)
        if not len(res) > 0:
            break
        _id = random.randint(100000, 999999)
    return _id


def check_hex(color: str):
    if not (0 < len(color) < 8) and not color.startswith("#"):
        return False
    for ch in color[1:].lower():
        if (ch < "0" or ch > "9") and (ch < "a" or ch > "f"):
            return False
    return True


async def get_transcript(member: discord.Member, channel: discord.TextChannel):
    export = await chat_exporter.export(channel=channel)
    file_name = f"asset/tickets/{member.id}.html"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(export)


def upload(file_path: str, member_name: str):
    gtoken = os.getenv("github_token")
    github = Github(gtoken)
    repo = github.get_repo("iayushanand/ayuitzxyz")
    file_name = f"{int(time.time())}"
    repo.create_file(
        path=f"templates/tickets/{file_name}.html",
        message="Ticket Log for {0}".format(member_name),
        branch="main",
        content=open(f"{file_path}", "r", encoding="utf-8").read(),
    )
    os.remove(file_path)
    return file_name
