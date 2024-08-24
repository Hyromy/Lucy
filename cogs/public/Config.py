import discord

from discord.ext import commands

class Config(commands.Cog):
    def __init__(self, Lucy:commands.Bot):
        self.Lucy = Lucy
        self.description = "Configuración e información"
        self.emoji = "⚙️"

async def setup(Lucy:commands.Bot):
    await Lucy.add_cog(Config(Lucy))