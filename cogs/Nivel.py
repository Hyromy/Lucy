import discord
from discord.ext import commands
import json, asyncio, random, math
from data.config import NEXT_LEVEL

class Nivel(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla
        Nivel.__doc__="Sistema de niveles de usuario"
        self.Layla.loop.create_task(self.save())
        with open("./json/users.json", "r") as f:
            self.users = json.load(f)

    def level_up(self, author_id):
        level = self.users[author_id]["Lvl"]
        exp = self.users[author_id]["Exp"]
        next_level = NEXT_LEVEL(level)

        if exp >= next_level:
            self.users[author_id]["Exp"] -= next_level
            self.users[author_id]["Lvl"] += 1
            return True
        else:
            return False

    async def save(self):
        await self.Layla.wait_until_ready()
        while not self.Layla.is_closed():
            with open("./json/users.json", "w") as f:
                json.dump(self.users, f, indent = 4)

            await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:            
            author_id = str(message.author.id)
            if not author_id in self.users:                
                self.users[author_id] = {}
                self.users[author_id]["Lvl"] = 0
                self.users[author_id]["Exp"] = 0

            self.users[author_id]["Exp"] += random.randint(1, 5)

            if self.level_up(author_id):
                level = self.users[author_id]["Lvl"]
                await message.author.send(f"Felicidades, subiste a nivel {level}.")

async def setup(Layla):
    await Layla.add_cog(Nivel(Layla))