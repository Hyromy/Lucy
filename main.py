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

sql = SQLHelper()
sql.load_cache(True)
sql.close_conection()
del sql

intents = discord.Intents.all()

Lucy = commands.Bot(
    command_prefix = activies.get_prefix,
    intents = intents,
    help_command = None
)

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
    await Lucy.tree.sync()
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