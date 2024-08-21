import discord

from discord.ext import commands

class Commands(commands.Cog):
    def __init__(self, Lucy:commands.Bot):
        self.Lucy = Lucy
        self.description = "Comandos básicos"
        self.emoji = "🤖"

    @commands.command(
        name = "ping",
        help = "Muestra el ping del bot en milisegundos",
        usage = "ping"
    )
    async def ping(self, ctx:commands.Context):
        await ctx.send(f"Pong! {round(self.Lucy.latency * 1000)}ms")

async def setup(Lucy:commands.Bot):
    await Lucy.add_cog(Commands(Lucy))