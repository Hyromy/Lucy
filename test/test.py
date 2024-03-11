import discord
from discord.ext import commands
import asyncio, psycopg2

DAD = 608870766586494976
DB = {
    "db": "layla",
    "user": "postgres",
    "password": "hyromy",
    "host": "localhost",
    "port": "5432"
}

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
        await Layla_sleep.start("MTE4MTA1NDYzMjc0MzY4NjE5NQ.GsxcMg.jqYojq-KPd9bFARqHocT1xqR0lFkSYIacLH9C4")

@Layla_sleep.event
async def on_message(message):
    if message.content == ",connect" and message.author.id == DAD:
        try:
            connection = psycopg2.connect(
                dbname = DB["db"],
                user = DB["user"],
                password = DB["password"],
                host = DB["host"],
                port = DB["port"])
            
            print("Conexion exitosa")

            cursor = connection.cursor()
            cursor.execute("select * from test;")
            rows = cursor.fetchall()

            await message.channel.send("(id, value)")

            for row in rows:
                await message.channel.send(row)

            cursor.close()
            connection.close()
        except Exception as e:
            print(f"    (!) {e}")

asyncio.run(main())