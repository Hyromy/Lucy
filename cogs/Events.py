import discord
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla
        
async def setup(Layla):
    await Layla.add_cog(Events(Layla))