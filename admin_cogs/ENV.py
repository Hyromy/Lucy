import discord
import os

from discord.ext import commands

class ENV(commands.Cog):
    def __init__(self, Lucy:commands.Bot):
        self.Lucy = Lucy

    @commands.command()
    async def env(self, ctx:commands.Context):
        if ctx.author.id != int(os.getenv("OWNER_ID")):
            return
        
        embed = discord.Embed(
            title = "Tokens",
            description = "Tokens y claves de configuración de `config.env`",
            color = 0x00bbff
        )

        with open("config.env") as f:
            env = f.readlines()

        for tokens in env:
            key, value = tokens.split("=")

            if value.endswith("\n"):
                value = value[:-1]

            embed.add_field(
                name = key,
                value = f"||{value}||",
                inline = False
            )

        await ctx.message.add_reaction("✅")
        await ctx.author.send(
            embed = embed,
            delete_after = 60
        )

async def setup(Lucy:commands.Bot):
    await Lucy.add_cog(ENV(Lucy))