import discord
import os

from discord.ext import commands

class Commands(commands.Cog):
    def __init__(self, Lucy:commands.Bot):
        self.Lucy = Lucy

    @commands.command(name = "ping")
    async def ping(self, ctx:commands.Context):
        await ctx.send(f"Pong! {round(self.Lucy.latency * 1000)}ms")

    @commands.command(name = "guilds")
    async def guilds(self, ctx:commands.Context):
        if ctx.author.id != int(os.getenv("OWNER_ID")):
            return

        guilds = self.Lucy.guilds
        mesaage = ""
        for guild in guilds:
            mesaage += f"{guild.name}: {guild.id}\n"

        await ctx.send(mesaage)

    @commands.command(name = "leaveserver")
    async def leaveserver(self, ctx:commands.Context, guild_id:int):
        if ctx.author.id != int(os.getenv("OWNER_ID")):
            return

        guild = self.Lucy.get_guild(guild_id)
        if guild and guild.id != int(os.getenv("GUILD_HOME_ID")):
            await guild.leave()
            await ctx.message.add_reaction("✅")
        else:
            await ctx.message.add_reaction("❌")

async def setup(Lucy):
    await Lucy.add_cog(Commands(Lucy))