import discord
from discord.ext import commands, tasks

from itertools import cycle

Layla_status = cycle(["Estudiando", "Durmiendo", "Mirando las estrellas"])

class BasicEvents(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla

    """ @commands.Cog.listener()
    async def on_readdy(self):
        print("holaaa") """

    @tasks.loop(seconds = 5)
    async def status():
        await Layla.change_presence(activity = discord.Game(next(Layla_status)))

async def setup(Layla):
    await Layla.add_cog(BasicEvents(Layla))