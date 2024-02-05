import discord
from discord.ext import commands
import random
from data.config import VERSION

class Commands(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla

    @commands.command()
    async def ping(self, ctx):
        latencia = round(self.Layla.latency * 1000)
        await ctx.send(f"Pong! {latencia}ms")

    @commands.command(aliases = ["8", "8ball"])
    async def ball(self, ctx, *x):
        with open("./data/ball.txt", "r") as f:
            respuestas = f.readlines()
            respuesta = random.choice(respuestas)
            
        await ctx.send(respuesta)

    @commands.command()
    async def tell(self, ctx, user:discord.Member, *, message):
        embed = discord.Embed(title = None, description = message, color = 0x00bbff)

        author = f"{ctx.author.display_name} te ha dicho:"
        usuario_url = f"https://discord.com/users/{ctx.author.id}"
        embed.set_author(name = author, url = usuario_url, icon_url = ctx.author.avatar)
        embed.set_footer(text = f"Versión: {VERSION}")

        await ctx.message.delete()
        await user.send(embed = embed)

async def setup(Layla):
    await Layla.add_cog(Commands(Layla))