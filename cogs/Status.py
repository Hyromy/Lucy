import discord
from discord.ext import commands, tasks
import random

status = discord.Status.idle

class Status(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla
        Status.__doc__="Variabilidad de estados del bot"

    @commands.Cog.listener()
    async def on_ready(self):
        self.newstatus.start()

    @tasks.loop(seconds=60)
    async def newstatus(self):
        with open("./data/status.txt", "r", encoding="utf-8") as f:
            activities = f.readlines()
            name = random.choice(activities)

        activity = discord.Game(name=name)
        await self.Layla.change_presence(status=status, activity=activity)

async def setup(Layla):
    await Layla.add_cog(Status(Layla))