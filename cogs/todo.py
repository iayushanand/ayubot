import time

import discord
from discord.ext import commands

from ext.consts import TICK_EMOJI, TODO_ARROW_EMOJI
from utils.helper import generate_id


class Todo(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = bot.db

    @commands.group(name="todo", invoke_without_command=True)
    async def todo(self, ctx: commands.Context):
        """
        Shows todo based commands
        """
        embed = (
            discord.Embed(
                description="Todo based commands!", color=discord.Color.blurple()
            )
            .add_field(name="show", value="Shows your todo list", inline=False)
            .add_field(name="add", value="Adds a todo", inline=False)
            .add_field(name="remove", value="Remove a todo", inline=False)
            .add_field(name="strike", value="Strike out a todo", inline=False)
            .add_field(name="clear", value="Clear your todo list", inline=False)
        )
        await ctx.reply(embed=embed)

    @todo.command(name="show", help="Shows your todo list")
    async def todo_show(self, ctx: commands.Context):
        user_id = ctx.author.id
        res = await self.db.fetch("SELECT * FROM todo WHERE user_id = $1", user_id)
        if len(res) == 0:
            return await ctx.reply(
                embed=discord.Embed(
                    description=":x: Your todo list is empty", color=discord.Color.red()
                )
            )
        embed = discord.Embed(color=discord.Color.blurple(), description="")
        for i, _ in enumerate(res):
            unique_id = res[i].get("unique_id")
            _t = res[i].get("time")
            task = res[i].get("task")
            embed.description = (
                embed.description
                + TODO_ARROW_EMOJI
                + f"`{unique_id}` - {task} (<t:{_t}:R>)\n"
            )
        await ctx.reply(embed=embed)

    @todo.command(name="add")
    async def todo_add(self, ctx: commands.Context, todo: str):
        unique_id = await generate_id(self.db, "todo")
        user_id = ctx.author.id
        _t = int(time.time())
        task = todo
        await self.db.execute(
            "INSERT INTO todo VALUES ($1, $2, $3, $4)", unique_id, user_id, _t, task
        )
        embed = discord.Embed(
            description=TICK_EMOJI + f"added `{task}` to your todo list.",
            color=discord.Color.green(),
        )
        await ctx.reply(embed=embed)

    @todo.command(name="remove")
    async def todo_remove(self, ctx: commands.Context, unique_id: int):
        user_id = ctx.author.id
        await self.db.execute(
            "DELETE FROM todo WHERE unique_id = $1 AND user_id = $2", unique_id, user_id
        )
        embed = discord.Embed(
            description=TICK_EMOJI + f"deleted `{unique_id}` from your todo list.",
            color=discord.Color.green(),
        )
        await ctx.reply(embed=embed)

    @todo.command(name="strike")
    async def todo_strike(self, ctx: commands.Context, unique_id: int):
        user_id = ctx.author.id
        res = await self.db.fetch(
            "SELECT task FROM todo WHERE unique_id = $1 AND user_id = $2",
            unique_id,
            user_id,
        )
        if len(res) == 0:
            return await ctx.send(
                embed=discord.Embed(
                    description=":x: todo not found", color=discord.Color.red()
                )
            )
        task = res[0].get("task")
        await self.db.execute(
            "UPDATE todo SET task = $1 WHERE unique_id = $2", f"~~{task}~~", unique_id
        )
        embed = discord.Embed(
            description=TICK_EMOJI + f"striked `{task}` from todo list",
            color=discord.Color.green(),
        )
        await ctx.reply(embed=embed)

    @todo.command(name="clear")
    async def todo_clear(self, ctx: commands.Context):
        user_id = ctx.author.id
        await self.db.execute("DELETE FROM todo WHERE user_id = $1", user_id)
        embed = discord.Embed(
            description=TICK_EMOJI + "cleared your todo list",
            color=discord.Color.green(),
        )
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Todo(bot))
