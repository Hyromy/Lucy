from config import *
import discord
from discord.ext import commands
import os, asyncio, json

def get_prefix_server(Layla, message):
    with open("prefixes.json", "r") as f:
        prefix = json.load(f)

    return prefix[str(message.guild.id)]

Layla = commands.Bot(command_prefix = get_prefix_server, intents = discord.Intents.all())

@Layla.event
async def on_ready():
    sp = 16
    ready = f"{(" " * sp) + Layla.user.name} está lista{" " * sp}"
    line = "-" * len(ready)

    print()
    print(line)
    print(ready)
    print(line)

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await Layla.load_extension(f"cogs.{filename[:-3]}")
            print(f"Cargando: {filename[:-3]}...")

async def main():
    async with Layla:
        await load()
        await Layla.start(TOKEN)

asyncio.run(main())