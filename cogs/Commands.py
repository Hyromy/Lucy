import discord
from discord.ext import commands
import random

class Commands(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla

    @commands.command()
    async def ping(self, ctx):
        latencia = round(self.Layla.latency * 1000)
        await ctx.send(f"Pong! {latencia}ms")

    @commands.command(aliases = ["8", "8ball"])
    async def ball(self, ctx, *x):
        with open("cogs/ball.txt", "r") as f:
            respuestas = f.readlines()
            respuesta = random.choice(respuestas)
            
        await ctx.send(respuesta)

async def setup(Layla):
    await Layla.add_cog(Commands(Layla))