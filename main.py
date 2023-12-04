import discord
from discord.ext import commands

intents = discord.Intents.all()
intents.members = True
intents.presences = True

client = commands.Bot(command_prefix = "l,", intents = intents)

@client.event
async def on_ready():
    print("-----------------------------------------")
    print("    LaylaBot no se ha quedado dormida    ")
    print("-----------------------------------------")
    
@client.command()
async def hola(ctx):
    await ctx.send("Hola!")
    
client.run("MTE4MTA1NDYzMjc0MzY4NjE5NQ.Gpsls_.CXv0OSen-XWeevmiWgRE3SWmZtZLKW3FaVv0YU")