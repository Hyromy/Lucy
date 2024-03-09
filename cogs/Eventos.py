import discord
from discord.ext import commands, tasks
import json, datetime, os
from data.config import VERSION, HOME

default_prefix = ","

class Eventos(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla
        Eventos.__doc__="Escucha de eventos"

    @commands.Cog.listener()
    async def on_ready(self):
        self.fix.start()

    @tasks.loop(seconds = 1)
    async def fix(self):
        if not os.path.exists("json"):
            time = datetime.datetime.now()
            f_t = time.strftime("%d/%m/%Y - %H:%M:%S")
            print(f"    (!) [{f_t}] carpeta json inexistente -> CREANDO")
            os.makedirs("json")

        prefix = "json/prefix.json"
        if not os.path.exists(prefix) or os.path.getsize(prefix) == 0:
            time = datetime.datetime.now()
            f_t = time.strftime("%d/%m/%Y - %H:%M:%S")
            print(f"    (!) [{f_t}] prefix corrupto -> REPARANDO")
            
            data = {}
            with open(prefix, "w") as f:
                for guild in self.Layla.guilds:
                    data[str(guild.id)] = ","
                json.dump(data, f, indent = 4)

        log = "json/log_channel.json"
        if not os.path.exists(log) or os.path.getsize(log) == 0:
            time = datetime.datetime.now()
            f_t = time.strftime("%d/%m/%Y - %H:%M:%S")
            print(f"    (!) [{f_t}] log channel corrupto -> REPARANDO")

            with open(log, "w") as f:
                json.dump({}, f, indent = 4)

        mute = "json/mute_rol.json"
        if not os.path.exists(mute) or os.path.getsize(mute) == 0:
            time = datetime.datetime.now()
            f_t = time.strftime("%d/%m/%Y - %H:%M:%S")
            print(f"    (!) [{f_t}] mute rol corrupto -> REPARANDO")

            with open(mute, "w") as f:
                json.dump({}, f, indent = 4)

        user = "json/user.json"
        if not os.path.exists(user) or os.path.getsize(user) == 0:
            time = datetime.datetime.now()
            f_t = time.strftime("%d/%m/%Y - %H:%M:%S")
            print(f"    (!) [{f_t}] user corrupto -> REPARANDO")

            with open(user, "w") as f:
                json.dump({}, f, indent = 4)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        path = "json/prefix.json"
        try: #establecer prefijo
            with open(f"./{path}", "r") as f:
                prefix = json.load(f)

            prefix[str(guild.id)] = default_prefix

            with open(f"./{path}", "w") as f:
                json.dump(prefix, f, indent = 4)
        except Exception as e:
            time = datetime.datetime.now()
            f_t = time.strftime("%d/%m/%Y - %H:%M:%S")
            print(f"    (!) [{f_t}] Establecer prefijo por defecto: {e}")

        try: #carta de presentacion
            author:discord.Member = guild.owner
            home:discord.Guild = discord.utils.get(self.Layla.guilds, id = HOME)

            embed = discord.Embed(title = f"Gracias por invitarme a {guild.name}!", color = 0x00bbff)
            embed.set_thumbnail(url = self.Layla.user.avatar)
            embed.add_field(name = f"Soy {self.Layla.user.name}", value =
                            "Soy aspirante a ser una bot multifuncional en español para tu servidor. Aunque actualmente sigo en desarrollo y con muchas tareas pendietes, me esforzaré para ayudarlos en lo que pueda, y hacer de tu servidor más agradable y acogedor.",
                            inline = False)

            embed.add_field(name = f"Primeros pasos", value = 
                            f"Puedes configurar mi prefijo con `,setprefix <nuevo prefijo>`. Si alguna vez olvidas mi prefijo puedes escribir {self.Layla.user.mention} prefix.\n" + 
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
        if "prefix" in message.content.lower() and self.Layla.user.mention in message.content:
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

            prefix = self.Layla.command_prefix(self.Layla, message)
            await message.channel.send(f"El prefijo de este servidor es `{prefix}`")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.HTTPException):
            time = datetime.datetime.now()
            f_t = time.strftime("%d/%m/%Y - %H:%M:%S")
            print(f"    (!) [{f_t}] Error de comando (General)")

async def setup(Layla):
    await Layla.add_cog(Eventos(Layla))