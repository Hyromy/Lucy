import discord

from discord.ext import commands

class Commands(commands.Cog):
    def __init__(self, Lucy:commands.Bot):
        self.Lucy = Lucy

    @commands.command(name = "ping")
    async def ping(self, ctx:commands.Context):
        await ctx.send(f"Pong! {round(self.Lucy.latency * 1000)}ms")

async def setup(Lucy:commands.Bot):
    await Lucy.add_cog(Commands(Lucy))