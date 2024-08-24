import discord
import os
import asyncio
import datetime
import pytz
import re

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

async def load_cogs():
    DIR = "cogs"
    dunder_re = r"__.*__"
    folders = [f for f in os.listdir(DIR) if os.path.isdir(os.path.join(DIR, f)) and not re.match(dunder_re, f)]
    for folder in folders:
        print(f"---- {folder.upper()} ----")
        for file in os.listdir(f"{DIR}/{folder}"):
            if re.match(dunder_re + ".py", file):
                continue

            if file.endswith(".py"):
                try:
                    cog_name = file[:-3]
                    await Lucy.load_extension(f"{DIR}.{folder}.{cog_name}")

                except Exception as e:
                    print(f"\t(!) {cog_name} no se pudo cargar -> {e}")

                else:
                    print(f"{cog_name} cargado")
        print()

async def main():
    try:
        async with Lucy:
            await load_cogs()
            await Lucy.start(os.getenv("DISCORD_BOT_TOKEN"))
    
    except Exception as e:
        print(f"\t(!)Error al intentar conectar -> {e}")
        return

asyncio.run(main())