import discord, json, time, datetime, pytz, os, threading
from discord.ext import commands
from data.config import VERSION, HOME

class Eventos(commands.Cog):
    def __init__(self, Lucy):
        self.Lucy = Lucy
        self.cooldown = 10
        Eventos.__doc__="Escucha de eventos"

        thread = threading.Thread(target = self.fix_all)
        thread.daemon = True
        thread.start()

    def fix_all(self):
        first = True
        if first:
            first = False
            time.sleep(self.cooldown)

        current:datetime.datetime
        f_t:str

        while True:
            if self.fix_json():
                current = datetime.datetime.now(pytz.timezone('America/Mexico_City'))
                f_t = current.strftime("%H:%M:%S")
                print(f"    (!) [{f_t}] carpeta json inexistente -> CREANDO")

                time.sleep(self.cooldown -1)

            else:
                if self.fix_prefix():
                    current = datetime.datetime.now(pytz.timezone('America/Mexico_City'))
                    f_t = current.strftime("%H:%M:%S")
                    print(f"    (!) [{f_t}] prefix corrupto -> REPARANDO")

                    time.sleep(self.cooldown -1)

                if self.fix_log():
                    current = datetime.datetime.now(pytz.timezone('America/Mexico_City'))
                    f_t = current.strftime("%H:%M:%S")
                    print(f"    (!) [{f_t}] log channel corrupto -> REPARANDO")

                    time.sleep(self.cooldown -1)

                if self.fix_mute():
                    current = datetime.datetime.now(pytz.timezone('America/Mexico_City'))
                    f_t = current.strftime("%H:%M:%S")
                    print(f"    (!) [{f_t}] mute rol corrupto -> REPARANDO")

                    time.sleep(self.cooldown -1)

                if self.fix_user():
                    current = datetime.datetime.now(pytz.timezone('America/Mexico_City'))
                    f_t = current.strftime("%H:%M:%S")
                    print(f"    (!) [{f_t}] user corrupto -> REPARANDO")

                    time.sleep(self.cooldown -1)
            
                if self.fix_chatbot():
                    current = datetime.datetime.now(pytz.timezone('America/Mexico_City'))
                    f_t = current.strftime("%H:%M:%S")
                    print(f"    (!) [{f_t}] chatbot corrupto -> REPARANDO")

                    time.sleep(self.cooldown -1)

            time.sleep(1)

    def fix_json(self):
        if not os.path.exists("json"):
            os.makedirs("json")

            self.fix_prefix()
            self.fix_log()
            self.fix_mute()
            self.fix_user()
            self.fix_chatbot()

            return True
        return False

    def fix_prefix(self):
        prefix = "json/prefix.json"
        if not os.path.exists(prefix) or os.path.getsize(prefix) <= 2:
            data = {}
            for guild in self.Lucy.guilds:
                data[str(guild.id)] = ","

            with open(prefix, "w") as f:
                json.dump(data, f, indent = 4)
            
            return True
        return False

    def fix_log(self):
        log = "json/log_channel.json"
        if not os.path.exists(log) or os.path.getsize(log) < 2:
            with open(log, "w") as f:
                json.dump({}, f, indent = 4)

            return True
        return False

    def fix_mute(self):
        mute = "json/mute_rol.json"
        if not os.path.exists(mute) or os.path.getsize(mute) < 2:
            with open(mute, "w") as f:
                json.dump({}, f, indent = 4)

            return True
        return False

    def fix_user(self):
        user = "json/user.json"
        if not os.path.exists(user) or os.path.getsize(user) < 2:
            with open(user, "w") as f:
                json.dump({}, f, indent = 4)

            return True
        return False
    
    def fix_chatbot(self):
        chatbot = "json/chatbot.json"
        if not os.path.exists(chatbot) or os.path.getsize(chatbot) < 2:
            with open(chatbot, "w") as f:
                json.dump({}, f, indent = 4)

            return True
        return False

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        path = "json/prefix.json"
        try: #establecer prefijo
            with open(f"./{path}", "r") as f:
                prefix = json.load(f)

            prefix[str(guild.id)] = ","

            with open(f"./{path}", "w") as f:
                json.dump(prefix, f, indent = 4)
        except Exception as e:
            time = datetime.datetime.now()
            f_t = time.strftime("%d/%m/%Y - %H:%M:%S")
            print(f"    (!) [{f_t}] Establecer prefijo por defecto: {e}")

        try: #carta de presentacion
            author:discord.Member = guild.owner
            home:discord.Guild = discord.utils.get(self.Lucy.guilds, id = HOME)

            embed = discord.Embed(title = f"Gracias por invitarme a {guild.name}!", color = 0x00bbff)
            embed.set_thumbnail(url = self.Lucy.user.avatar)
            embed.add_field(name = f"Soy {self.Lucy.user.name}", value =
                            "Soy aspirante a ser una bot multifuncional en español para tu servidor. Aunque actualmente sigo en desarrollo y con muchas tareas pendietes, me esforzaré para ayudarlos en lo que pueda, y hacer de tu servidor más agradable y acogedor.",
                            inline = False)

            embed.add_field(name = f"Primeros pasos", value = 
                            f"Puedes configurar mi prefijo con `,setprefix <nuevo prefijo>`. Si alguna vez olvidas mi prefijo puedes escribir {self.Lucy.user.mention} prefix.\n" + 
                            "Tambien puedes ver mi lista de comandos disponibles con el comando `help`. Estoy aqui para ayudarte en lo que necesites.",
                            inline = False)

            embed.add_field(name = "Contacto y ayuda adicional", value = 
                            f"Si hay algo en lo que no pueda ayudarte, tienes alguna sugerencia o has encontrado un bug, puedes unirte a [{home.name}](https://discord.gg/85hexN9TyM) o contactar con <@608870766586494976> para hablar sobre esa situación.",
                            inline = False)

            embed.set_footer(text = f"Versión: {VERSION}")

            await author.send(embed = embed)
        except Exception as e:
            time = datetime.datetime.now()
            f_t = time.strftime("%d/%m/%Y - %H:%M:%S")
            print(f"    (!) [{f_t}] Carta de presentacion: {e}")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        path = "json/mute_rol.json"
        try: #eliminar registro rol mute
            with open(f"./{path}", "r") as f:
                mute_role = json.load(f)

                mute_role.pop(str(guild.id))            

            with open(f"./{path}", "w") as f:
                mute_role = json.dump(mute_role, f, indent = 4)
        except KeyError:
            pass
        except Exception as e:
            time = datetime.datetime.now()
            f_t = time.strftime("%d/%m/%Y - %H:%M:%S")
            print(f"    (!) [{f_t}] Eliminar registro rol mute: {e}")
  
        path = "json/prefix.json"
        try: #eliminar registro del prefijo
            with open(f"./{path}", "r") as f:
                prefix = json.load(f)

            prefix.pop(str(guild.id))

            with open(f"./{path}", "w") as f:
                json.dump(prefix, f, indent = 4)
        except Exception as e:
            time = datetime.datetime.now()
            f_t = time.strftime("%d/%m/%Y - %H:%M:%S")
            print(f"    (!) [{f_t}] Eliminar registro del prefijo: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if "prefix" in message.content.lower() and self.Lucy.user.mention in message.content:
            path = "json/prefix.json"
            with open(f"./{path}", "r") as f:
                data = json.load(f)

            if str(message.guild.id) not in data:
                time = datetime.datetime.now()
                f_t = time.strftime("%d/%m/%Y - %H:%M:%S")
                print(f"    (!) [{f_t}] prefix perdido -> REPARANDO")

                data[str(message.guild.id)] = ","
                with open(f"./{path}", "w") as f:
                    json.dump(data, f, indent = 4)

            prefix = self.Lucy.command_prefix(self.Lucy, message)
            await message.channel.send(f"El prefijo de este servidor es `{prefix}`")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.HTTPException):
            time = datetime.datetime.now()
            f_t = time.strftime("%H:%M:%S")
            print(f"    (!) [{f_t}] Error de comando (General)")

async def setup(Lucy):
    await Lucy.add_cog(Eventos(Lucy))