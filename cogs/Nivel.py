import discord
from discord.ext import commands
import json, random, threading, time
from data.config import NEXT_LEVEL

class Nivel(commands.Cog):
    def __init__(self, Lucy):
        self.Lucy = Lucy
        Nivel.__doc__ = "Sistema de niveles de usuario"

        with open("./json/user.json", "r") as f:
            self.users = json.load(f)

        thread = threading.Thread(target = self.save)
        thread.daemon = True
        thread.start()

    def save(self):
        while not self.Lucy.is_closed():
            try:
                path = "json/user.json"
                with open(f"./{path}", "r") as f:
                    data = json.load(f)
            except Exception:
                pass

            try:
                for user_id, items in data.items():
                    self.users[user_id]["Adv"] = items["Adv"]
            except Exception:
                pass

            with open(f"./{path}", "w") as f:
                json.dump(self.users, f, indent = 4)

            time.sleep(60)
            
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

async def setup(Lucy):
    await Lucy.add_cog(Nivel(Lucy))