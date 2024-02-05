import discord
from discord.ext import commands
import json

class Configuration(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open("prefixes.json", "r") as f:
            prefix = json.load(f)

        prefix[str(guild.id)] = ","

        with open("prefixes.json", "w") as f:
            json.dump(prefix, f, indent = 4)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open("prefixes.json", "r") as f:
            prefix = json.load(f)

        prefix.pop(str(guild.id))

        with open("prefixes.json", "w") as f:
            json.dump(prefix, f, indent = 4)

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def prefix(self, ctx, new_prefix:str):
        with open("prefixes.json", "r") as f:
            prefix = json.load(f)

        prefix[str(ctx.guild.id)] = new_prefix

        with open("prefixes.json", "w") as f:
            json.dump(prefix, f, indent = 4)

        await ctx.send(f"Prefijo cambiado a {new_prefix}")  

    @prefix.error
    async def prefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("No tienes permisos para hacer eso")

async def setup(Layla):
    await Layla.add_cog(Configuration(Layla))