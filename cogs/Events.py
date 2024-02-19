import discord
from discord.ext import commands
import json

class Events(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla

    @commands.Cog.listener()
    async def on_message(self, message):
        if "prefix" in message.content.lower() and self.Layla.user.mention in message.content:
            prefix = self.Layla.command_prefix(self.Layla, message)
            await message.channel.send(f"El prefijo de este servidor es {prefix}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open("./json/log_channels.json", "r") as f:
            log = json.load(f)

        channel_id = log.get(str(member.guild.id))
        if channel_id is not None:
            channel_out = self.Layla.get_channel(channel_id)
            await channel_out.send(f"{member.name} Se ha unido al servidor")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        with open("./json/log_channels.json", "r") as f:
            log = json.load(f)

        channel_id = log.get(str(member.guild.id))
        if channel_id is not None:
            channel_out = self.Layla.get_channel(channel_id)
            await channel_out.send(f"{member.name} Se ha ido al servidor")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.HTTPException):
            await ctx.send("Ocurrió un error al intentar conectarse a Discord. Inténtalo de nuevo más tarde.")

async def setup(Layla):
    await Layla.add_cog(Events(Layla))