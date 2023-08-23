# ------------- import(s) ---------------

from io import BytesIO

import discord
import requests
from discord.ext import commands
from PIL import Image

from utils.helper import make_banner


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
        main_text = str(member)
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


async def setup(bot: commands.Bot):
    await bot.add_cog(Levelling(bot=bot))
