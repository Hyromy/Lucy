import discord
from discord.ext import commands, tasks

import os
import asyncio

Layla = commands.Bot(command_prefix = ",", intents = discord.Intents.all())

@Layla.event
async def on_ready():
    print("conectada")

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await Layla.load_extension(f"cogs.{filename[:-3]}")
            print(f"{filename[:-3]} Cargado")

async def main():
    async with Layla:
        await load()
        await Layla.start("MTE4MTA1NDYzMjc0MzY4NjE5NQ.GQCicc.GSOoKCSV0633-BGLzjd4oHWS6CdMNeskfvNG7I")

asyncio.run(main())