import discord
import os
import asyncio
import datetime
import pytz

from discord.ext import commands
from dotenv import load_dotenv

import common.activies as activies
import common.clock as clock

from utils.SQL import SQLHelper

load_dotenv("config.env")

class Help(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    # help
    async def send_bot_help(self, mapping:dict):
        embed = discord.Embed(
            title = "Comandos de Lucy",
            description = "Estos son los comandos que puedes usar con Lucy",
            color = 0x00bbff
        )
        embed.set_thumbnail(url = self.context.bot.user.avatar)

        for cog in mapping.keys():
            if cog is None or mapping[cog] == []:
                continue

            emoji = cog.emoji if hasattr(cog, "emoji") else ""
            embed.add_field(
                name = f"{cog.qualified_name} {emoji}",
                value = cog.description or "",
                inline = False
            )
            
        await self.context.send(embed = embed)

    # help <categoria>
    async def send_cog_help(self, cog):
        embed = discord.Embed(
            title = f"Categoría: {cog.qualified_name}",
            description = cog.description,
            color = 0x00bbff
        )

        cmds = cog.get_commands()
        cmds = sorted(cmds, key = lambda x:x.name)
        for command in cmds:
            embed.add_field(
                name = command.name,
                value = ""
            )

        await self.context.send(embed = embed)

    # help <comando>
    async def send_command_help(self, command:commands.Command):
        prefix = get_prefix(self.context.bot, self.context.message)
        
        embed = discord.Embed(
            title = f"{command.cog_name}: {command.name}",
            description = command.help,
            color = 0x00bbff
        )
        if command.aliases:
            embed.add_field(
                name = "Alias",
                value = ", ".join(command.aliases),
                inline = False
            )
        embed.add_field(
            name = "Ejemplo de uso",
            value = f"`{prefix}{command.usage}`",
            inline = False
        )

        await self.context.send(embed = embed)

    async def command_not_found(self, string):
        pass

print("Conectando a la base de datos...")
sql = SQLHelper()
sql.load_cache(True)
sql.close_conection()
del sql

def get_prefix(Lucy, message) -> str:
    prefix = activies.read_json_file("dbcache/server")
    return prefix[str(message.guild.id)]["prefix"]

intents = discord.Intents.all()

class LUCY(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = get_prefix,
            intents = intents,
            help_command = Help()
        )

    def get_cog(self, name:str):
        for cog_name, cog in self.cogs.items():
            if cog_name.lower() == name.lower():
                return cog
        return None

Lucy = LUCY()

def ready_msg():    
    activies.draw_spliter()
    print()

    lucy = f"{Lucy.user.name} está lista" 
    version = activies.get_version()
    print(lucy.center(activies.get_terminal_size()))
    print(version.center(activies.get_terminal_size()))

    current = datetime.datetime.now(pytz.timezone("America/Mexico_City"))
    f_time = current.strftime(" %d/%m/%Y %H:%M:%S ")
    print()
    print(f_time.center(activies.get_terminal_size(), "-"))
    print()

@Lucy.event
async def on_ready():
    ready_msg()
    clock.start_clock()

async def load_admin_cogs():
    print("COGS DE ADMINISTRACIÓN")
    for file in os.listdir("admin_cogs"):
        if file.endswith(".py"):
            try:
                cog_name = file[:-3]
                print(f"Cargando {cog_name}...")
                await Lucy.load_extension(f"admin_cogs.{cog_name}")

            except Exception as e:
                msg = f"(!) {cog_name} no se pudo cargar -> {e}"
                print(msg)
    print()

async def load_cogs():
    print("COGS")
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            try:
                cog_name = file[:-3]
                print(f"Cargando {cog_name}...")
                await Lucy.load_extension(f"cogs.{cog_name}")

            except Exception as e:
                msg = f"(!) {cog_name} no se pudo cargar -> {e}"
                print(msg)
    print()
    
async def main():
    async with Lucy:
        await load_admin_cogs()
        await load_cogs()
        await Lucy.start(os.getenv("DISCORD_BOT_TOKEN"))

try:
    asyncio.run(main())

except:
    print("Error al intentar conectar")