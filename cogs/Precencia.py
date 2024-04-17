import discord
from discord.ext import commands, tasks
import random

class Precencia(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla
        Precencia.__doc__ = "Precencia del bot"

    @commands.Cog.listener()
    async def on_ready(self):        
        try:
            with open("data/Layla.gif", "rb") as avatar:
                await self.Layla.user.edit(avatar = avatar.read())
        except Exception as e:
            print(f"    (!) Icono animado: {e}")
        self.newstatus.start()

    @tasks.loop(hours = 8)
    async def newstatus(self):
        with open("./data/status.txt", "r", encoding = "utf-8") as f:
            activities = f.readlines()

        name = random.choice(activities)
        activity = discord.Game(name = name)
        await self.Layla.change_presence(activity = activity)

async def setup(Layla):
    await Layla.add_cog(Precencia(Layla))