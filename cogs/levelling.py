# ------------- import(s) ---------------

from io import BytesIO

import discord
import requests
from discord.ext import commands
from PIL import Image

from ext.consts import TICK_EMOJI
from utils.helper import check_hex, make_banner


class Levelling(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = bot.db

    @commands.group(name="level")
    async def show_level(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        if member.bot:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{member.mention} is a bot!", color=discord.Color.red()
                )
            )
        res = await self.db.fetch("SELECT * FROM level WHERE user_id = $1", member.id)
        if len(res) == 0:
            return await ctx.reply(
                embed=discord.Embed(
                    description="No data found {0.mention}!".format(member),
                    color=discord.Color.red(),
                )
            )

        av = member.display_avatar
        av = BytesIO(await av.read())
        bg_url = res[0].get("img_url")
        main_text = member.name
        bg = Image.open(requests.get(url=bg_url, stream=True).raw)
        xp = res[0].get("xp")
        lev = res[0].get("level")
        req = lev * 100
        prim = res[0].get("prim_col")
        sec = res[0].get("sec_col")

        banner = make_banner(av, bg, lev, xp, req, main_text, prim, sec)

        with BytesIO() as image_binary:
            banner.save(image_binary, "PNG")
            image_binary.seek(0)
            await ctx.reply(
                content=f"**{member.mention}'s level:**",
                file=discord.File(fp=image_binary, filename=f"level.png"),
            )

    @commands.command(name="banner-image")
    @commands.has_any_role(810419731575996416, 1000072283282477158)
    async def _banner_image(self, ctx: commands.Context, image: str):
        try:
            Image.open(requests.get(image, stream=True).raw)
        except Exception as e:
            await ctx.reply(
                embed=discord.Embed(
                    description=":x:That image cannot be fetched by bot!",
                    color=discord.Color.red(),
                )
            )
        await self.db.execute(
            "UPDATE level SET img_url = $1 WHERE user_id = $2", image, ctx.author.id
        )
        await ctx.reply(
            embed=discord.Embed(
                description=TICK_EMOJI + "Banner Background Updated!",
                color=discord.Color.green(),
            )
        )

    @commands.command(name="banner-pri")
    @commands.has_any_role(810419731638386698, 1000072283282477158)
    async def _banner_primirary_color(self, ctx: commands.Context, color: str):
        if not check_hex(color):
            return await ctx.reply(
                embed=discord.Embed(
                    description=":x: Please enter a valid color in hex format (#rrggbb)",
                    color=discord.Color.red(),
                )
            )
        await self.db.execute(
            "UPDATE level SET prim_col = $1 WHERE user_id = $2", color, ctx.author.id
        )
        await ctx.reply(
            embed=discord.Embed(
                description=TICK_EMOJI + "Banner Primary Color Updated!",
                color=discord.Color.green(),
            )
        )

    @commands.command(name="banner-sec")
    @commands.has_any_role(810419731638386698, 1000072283282477158)
    async def _banner_secondary_color(self, ctx: commands.Context, color: str):
        if not check_hex(color):
            return await ctx.reply(
                embed=discord.Embed(
                    description=":x: Please enter a valid color in hex format (#rrggbb)",
                    color=discord.Color.red(),
                )
            )
        await self.db.execute(
            "UPDATE level SET sec_col = $1 WHERE user_id = $2", color, ctx.author.id
        )
        await ctx.reply(
            embed=discord.Embed(
                description=TICK_EMOJI + "Banner Secondary Color Updated!",
                color=discord.Color.green(),
            )
        )

    # I was forced by my manager to add this command ;-; (please help I am trapped in his basement)
    @commands.command(name = "level-set")
    @commands.has_role(812523394779709482)
    async def _level_set(self, ctx: commands.Context, member: discord.Member, level: int):
        try:await self.db.execute("UPDATE level SET level = $1, xp = 0 WHERE user_id = $2", level, member.id)
        except:await ctx.reply(embed=discord.Embed(description=":x: Something went wrong!",color=discord.Color.red()));raise Exception
        await ctx.reply(
            embed = discord.Embed(
                description = TICK_EMOJI+f"updated level for {member.mention} set it to {level}",
                color = discord.Color.green()
            )
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Levelling(bot=bot))
