import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from config import *

intents = discord.Intents.all()
intents.members = True
intents.presences = True

queues = {}

def check_queue(ctx, id):
    if queues[id] != []:
        voice = ctx.guild.voice_client
        source = queues[id].pop(0)
        player = voice.play(source)

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
        voice = await channel.connect()
        source = FFmpegPCMAudio("audio/layla.wav")
        player = voice.play(source)
        
    else:
        await ctx.send("Tienes que estar primero en un canal de voz para acompañarte")

@client.command(pass_context = True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    
    if voice.is_playing():
        voice.pause()
        
    else:
        await ctx.send("Por el momento no hay contenido que se este reproduciendo")

@client.command(pass_context = True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    
    if voice.is_paused():
        voice.resume()
        
    else:
        await ctx.send("No hay nada que este pausado")

@client.command(pass_context = True)
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    voice.stop()
    
@client.command(pass_context = True)
async def play(ctx, arg):
    voice = ctx.guild.voice_client
    source = FFmpegPCMAudio(f"audio/{arg}.wav")
    player = voice.play(source, after = lambda x = None: check_queue(ctx, ctx.message.guild.id))

@client.command(pass_context = True)
async def queue(ctx, arg):
    voice = ctx.guild.voice_client
    source = FFmpegPCMAudio(f"audio/{arg}.wav")
    guild_id = ctx.message.guild.id
    
    if guild_id in queues:
        queues[guild_id].append(source)
        
    else:
        queues[guild_id] = [source]
        
    await ctx.send("Añadido a la lista de reproducción")

@client.command(pass_context = True)
async def leave(ctx):
    if ctx.author.voice:
        await ctx.guild.voice_client.disconnect()
        
    else:
        await ctx.send("No he llegado y ya me estan corriendo :c")
    
client.run(TOKEN)