import discord
from discord.ext import commands
import json, asyncio, random, math
from data.config import NEXT_LEVEL

class Nivel(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla
        Nivel.__doc__ = "Sistema de niveles de usuario"

        import os
        user = "json/user.json"
        if not os.path.exists(user) or os.path.getsize(user) == 0:
            with open(user, "w") as f:
                json.dump({}, f, indent = 4)

        self.Layla.loop.create_task(self.save())
        
        with open(f"./{user}", "r") as f:
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
            path = "json/user.json"
            with open(f"./{path}", "r") as f:
                data = json.load(f)

            for user_id, items in data.items():
                self.users[user_id]["Adv"] = items["Adv"]

            with open(f"./{path}", "w") as f:
                json.dump(self.users, f, indent = 4)

            await asyncio.sleep(3)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:            
            author_id = str(message.author.id)
            if not author_id in self.users:                
                self.users[author_id] = {}
                self.users[author_id]["Lvl"] = 0
                self.users[author_id]["Exp"] = 0
                self.users[author_id]["Adv"] = True

            self.users[author_id]["Exp"] += random.randint(1, 5)
            if self.level_up(author_id) and self.users[author_id]["Adv"]:
                level = self.users[author_id]["Lvl"]
                exp = NEXT_LEVEL(level)

                embed = discord.Embed(title = f"Subida a nivel {level}", color = 0x00bbff)
                embed.add_field(name = f"Felicidades has subido a nivel {level}", value = f"Para llegar al siguiente nivel necesitarás {exp}exp", inline = False)
                embed.set_footer(text = f"Puedes desactivar estas notificaciones escribiendo 'level @{message.author.name} False'")

                await message.author.send(embed = embed)

async def setup(Layla):
    await Layla.add_cog(Nivel(Layla))