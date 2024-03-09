import discord
from discord.ext import commands
import os, asyncio, json

Layla_sleep = commands.Bot(command_prefix = ",,", intents = discord.Intents.all())
Layla_sleep.remove_command("help")

@Layla_sleep.event
async def on_ready():
    sp = 16
    ready = f"{' ' * sp}Sueño astral listo{' ' * sp}"
    line = "-" * len(ready)

    print()
    print(line)
    print(ready)
    print(line)

async def main():
    async with Layla_sleep:
        await Layla_sleep.start("TOKEN")

@Layla_sleep.command(aliases = ["json"])
async def write(ctx, id:str, value:str):
    # en caso de que no exista la ruta crearla
    if not os.path.exists("test/log"):
        os.makedirs("test/log")
        await ctx.send("ruta inexistente, creando ruta")

    # en caso de que no exista el archivo, crearlo y prepararlo
    if not os.path.exists("test/log/test.json"):
        with open("test/log/test.json", "w") as f:
            json.dump({}, f)
            await ctx.send("archivo inexistente, creando archivo")
    else:
        # en caso de que el archivo este vacio, prepararlo
        if os.path.getsize("test/log/test.json") == 0:
            with open("test/log/test.json", "w") as f:
                json.dump({}, f)
                await ctx.send("archivo corrupto, reparando archivo")

    # leyendo archivo
    with open("test/log/test.json", "r") as f:
        data = json.load(f)

    # insertar informacion
    data[id] = value

    # escribir archivo
    with open("test/log/test.json", "w") as f:
        json.dump(data, f, indent = 4)

    await ctx.send("registro realizado")

asyncio.run(main())