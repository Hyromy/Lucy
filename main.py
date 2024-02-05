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

@Layla.tree.command(name = "ping", description = "Mide la latencia del bot en milisegundos")
async def ping(interaction: discord.Interaction):
    latencia = round(Layla.latency * 1000)
    await interaction.response.send_message(f"Pong! {latencia}ms")

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