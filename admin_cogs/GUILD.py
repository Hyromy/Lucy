import discord
import os

from discord.ext import commands

class GUILD(commands.Cog):
    def __init__(self, Lucy:commands.Bot):
        self.Lucy = Lucy
        self.description = "Gestión de servidores"
        self.emoji = "🏠"
        self.admin = True

    @commands.command(
        name = "guilds",
        help = "Muestra el nombre y id de los que se encuentra Lucy",
        aliases = ["servers"],
        usage = "guilds"
    )
    async def guilds(self, ctx:commands.Context):
        if ctx.author.id != int(os.getenv("OWNER_ID")):
            return

        guilds = self.Lucy.guilds
        mesaage = ""
        for guild in guilds:
            mesaage += f"{guild.name}: {guild.id}\n"

        await ctx.send(mesaage)

    @commands.command(
        name = "leaveguild",
        help = "Abandona un servidor",
        aliases = ["leaveserver"],
        usage = "leaveguild <id>"
    )
    async def leaveguild(self, ctx:commands.Context, guild_id:int):
        if ctx.author.id != int(os.getenv("OWNER_ID")):
            return

        guild = self.Lucy.get_guild(guild_id)
        if guild and guild.id != int(os.getenv("GUILD_HOME_ID")):
            await guild.leave()
            await ctx.message.add_reaction("✅")
        else:
            await ctx.message.add_reaction("❌")

async def setup(Lucy:commands.Bot):
    await Lucy.add_cog(GUILD(Lucy))