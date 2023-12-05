import discord
from discord.ext import commands
from config import *

intents = discord.Intents.all()
intents.members = True
intents.presences = True

client = commands.Bot(command_prefix = "l,", intents = intents)

@client.event
async def on_ready():
    print("-----------------------------------------")
    print("    LaylaBot no se ha quedado dormida    ")
    print("-----------------------------------------")
    
@client.event
async def on_member_join(member):
    channel = client.get_channel(LOG_CHANNEL)
    await channel.send(f"{member} se he unido :D")
    
@client.event
async def on_member_remove(member):
    channel = client.get_channel(LOG_CHANNEL)
    await channel.send(f"{member} se ha ido :c")
    
@client.command()
async def hola(ctx):
    await ctx.send("Hola!")
    
@client.command(pass_context = True)
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("Tienes que estar primero en un canal de voz para acompañarte")

@client.command(pass_context = True)
async def leave(ctx):
    if ctx.author.voice:
        await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("No he llegado y ya me estan corriendo :c")
    
client.run(TOKEN)