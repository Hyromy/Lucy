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

            await message.add_reaction("✅")
            await message.author.send(
                embed = embed,
                delete_after = 10
            )

async def setup(Lucy):
    await Lucy.add_cog(Events(Lucy))