import discord
from discord.ext import commands

import os
import asyncio

import json

from config import *

def get_prefix_server(Layla, message):
    with open("prefixes.json", "r") as f:
        prefix = json.load(f)

    return prefix[str(message.guild.id)]

Layla = commands.Bot(command_prefix = get_prefix_server, intents = discord.Intents.all())

@Layla.event
async def on_ready():
    print("Conectada")

@Layla.event
async def on_guild_join(guild):
    with open("prefixes.json", "r") as f:
        prefix = json.load(f)

    prefix[str(guild.id)] = ","

    with open("prefixes.json", "w") as f:
        json.dump(prefix, f, indent = 4)

@Layla.event
async def on_guild_remove(guild):
    with open("prefixes.json", "r") as f:
        prefix = json.load(f)

    prefix.pop(str(guild.id))

    with open("prefixes.json", "w") as f:
        json.dump(prefix, f, indent = 4)

@Layla.command
async def setprefix(ctx, *, newprefix:str):
    with open("prefixes.json", "r") as f:
        prefix = json.load(f)

    prefix[str(ctx.guild.id)] = newprefix

    with open("prefixes.json", "w") as f:
        json.dump(prefix, f, indent = 4)

    await ctx.send(f"Prefijo cambiado a {newprefix}")

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await Layla.load_extension(f"cogs.{filename[:-3]}")
            print(f"{filename[:-3]} Cargado")

async def main():
    async with Layla:
        await load()
        await Layla.start(TOKEN)

asyncio.run(main())