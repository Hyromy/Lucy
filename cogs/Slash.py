import discord
from discord import app_commands
from discord.ext import commands

class Slash(commands.Cog):
    def __init__(self, Layla:commands.Bot):
        self.Layla = Layla

    @commands.command()
    async def sync(self, ctx) -> None:
        fmt = await self.Layla.tree.sync(guild = ctx.guild)
        await ctx.send(f"{len(fmt)} comandos cargados")
        return

    @app_commands.command(name="ping", description="Mide la latencia del bot en milisegundos")
    async def ping(self, interaction:discord.Interaction):
        latencia = round(self.Layla.latency * 1000)
        await interaction.response.send_message(f"Pong! {latencia}ms")

async def setup(Layla):
    await Layla.add_cog(Slash(Layla), guilds = [discord.Object(id = 822176592196534283)])