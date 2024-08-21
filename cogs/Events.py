import discord
import re

from discord.ext import commands

from common import activies

class Events(commands.Cog):
    def __init__(self, Lucy:commands.Bot):
        self.Lucy = Lucy
        self.description = "Eventos básicos"

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
    async def on_guild_join(self, guild:discord.Guild):
        r = r"DEFAULT\s*'([^']+)'"
        guild_data = {}

        path = f"dbcache/server"
        file = activies.read_json_file(path)
        for key, value in file["data"].items():
            if key.startswith("id"):
                continue

            default_value = re.search(r, value).group(1)
            if "int" in value.casefold():
                default_value = int(default_value)
            guild_data[key] = default_value

        file = activies.read_json_file(path)
        file[str(guild.id)] = guild_data
        activies.write_json_file(path, file)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild:discord.Guild):
        try:
            path = f"dbcache/server"
            data = activies.read_json_file(path)
            data.pop(str(guild.id))
            activies.write_json_file(path, data)
        except:
            pass

async def setup(Lucy:commands.Bot):
    await Lucy.add_cog(Events(Lucy))