import discord
from discord import app_commands
from discord.ext import commands
from data.config import LAYLA_HOME

class Slash(commands.Cog):
    def __init__(self, Layla:commands.Bot):
        self.Layla = Layla

    @commands.Cog.listener()
    async def on_ready(self):
        await self.sync_commands()

    async def sync_commands(self):
        guild = self.Layla.get_guild(LAYLA_HOME)
        if guild:
            fmt = await self.Layla.tree.sync(guild = guild)
            print(f"{len(fmt)} comandos de barra diagonal cargados")

    @app_commands.command(name="ping", description="Mide la latencia del bot en milisegundos")
    async def ping(self, interaction:discord.Interaction):
        latencia = round(self.Layla.latency * 1000)
        await interaction.response.send_message(f"Pong! {latencia}ms")

async def setup(Layla):
    await Layla.add_cog(Slash(Layla), guilds = [discord.Object(id = LAYLA_HOME)])