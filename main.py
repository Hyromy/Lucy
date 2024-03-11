from data.config import TOKEN, VERSION
import discord
from discord.ext import commands
import os, asyncio, json

def get_prefix_server(Layla, message):
    with open("json/prefix.json", "r") as f:
        prefix = json.load(f)

    return prefix.get(str(message.guild.id))

Layla = commands.Bot(command_prefix = get_prefix_server, intents = discord.Intents.all())
Layla.remove_command("help")

@Layla.event
async def on_ready():
    await Layla.tree.sync()

    sp = 16
    ready = f"{' ' * sp}{Layla.user.name} está lista{' ' * sp}"
    line = "-" * len(ready)

    print()
    print(line)
    print(ready)
    print(f"Versión: {VERSION}".center(len(line)))
    print(line)

async def load():
    if not os.path.exists("json"):
        os.makedirs("json")

    prefix = "json/prefix.json"
    if not os.path.exists(prefix) or os.path.getsize(prefix) == 0:
        data = {}
        with open(prefix, "w") as f:
            for guild in Layla.guilds:
                data[str(guild.id)] = ","
            json.dump(data, f, indent = 4)

    log = "json/log_channel.json"
    if not os.path.exists(log) or os.path.getsize(log) == 0:
        with open(log, "w") as f:
            json.dump({}, f, indent = 4)

    mute = "json/mute_rol.json"
    if not os.path.exists(mute) or os.path.getsize(mute) == 0:
        with open(mute, "w") as f:
            json.dump({}, f, indent = 4)

    user = "json/user.json"
    if not os.path.exists(user) or os.path.getsize(user) == 0:
        with open(user, "w") as f:
            json.dump({}, f, indent = 4)

    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await Layla.load_extension(f"cogs.{filename[:-3]}")
            print(f"Cargando: {filename[:-3]}...")

async def main():
    async with Layla:
        await load()
        await Layla.start(TOKEN)

asyncio.run(main())