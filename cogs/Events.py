import discord
import os

from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, Lucy):
        self.Lucy:commands.Bot = Lucy

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if (
            self.Lucy.user.mentioned_in(message) and
            "prefix" in message.content.casefold() and 
            not message.author.bot
        ):
            answer = f"Hola! Mi prefijo es `{self.Lucy.command_prefix}`"
            await message.channel.send(answer)

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if (
            message.content == ",.env" and
            message.author.id == int(os.getenv("OWNER_ID"))
        ):
            tokens = ""
            for key, value in os.environ.items():
                if key.endswith("_TOKEN"):
                    tokens += f"{key}: ||{value}||\n"

            await message.author.send(tokens)

async def setup(Lucy):
    await Lucy.add_cog(Events(Lucy))