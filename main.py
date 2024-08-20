import discord
import os
import asyncio
import datetime
import pytz
import common

from discord.ext import commands
from dotenv import load_dotenv

from utils.SQL import SQLHelper

load_dotenv("config.env")

print("Conectando a la base de datos...")
sql = SQLHelper()
sql.load_cache(True)
sql.close_conection()
del sql

def get_prefix(Lucy, message) -> str:
    prefix = common.activies.read_json_file("dbcache/server")
    return prefix[str(message.guild.id)]["prefix"]

intents = discord.Intents.all()
Lucy = commands.Bot(
    command_prefix = get_prefix,
    intents = intents
)

def ready_msg():    
    common.activies.draw_spliter(text = "")
    print()

    lucy = f"{Lucy.user.name} está lista" 
    version = common.activies.get_version()
    print(lucy.center(common.activies.get_terminal_size()))
    print(version.center(common.activies.get_terminal_size()))

    current = datetime.datetime.now(pytz.timezone("America/Mexico_City"))
    f_time = current.strftime(" %d/%m/%Y %H:%M:%S ")
    print()
    print(f_time.center(common.activies.get_terminal_size(), "-"))
    print()

@Lucy.event
async def on_ready():
    ready_msg()
    common.clock.start_clock()

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