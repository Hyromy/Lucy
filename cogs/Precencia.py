import discord
from discord.ext import commands, tasks
import random, json

class Precencia(commands.Cog):
    def __init__(self, Lucy):
        self.Lucy = Lucy
        Precencia.__doc__ = "Precencia del bot"

    @commands.Cog.listener()
    async def on_ready(self):
        self.newstatus.start()

    @tasks.loop(hours = 1)
    async def newstatus(self):
        with open("./data/status.json", encoding = "utf-8") as f:
            data = json.load(f)

        key = random.choice(list(data.keys()))
        status = random.choice(data[key])

        activity = discord.CustomActivity(name = f"{key} {status}", emoji = key)
        await self.Lucy.change_presence(activity = activity)

async def setup(Lucy):
    await Lucy.add_cog(Precencia(Lucy))