import discord

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
            answer = f"Hola! Mi prefijo es {self.Lucy.command_prefix}"
            await message.channel.send(answer)

async def setup(Lucy):
    await Lucy.add_cog(Events(Lucy))