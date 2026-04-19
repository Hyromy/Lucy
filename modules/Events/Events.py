
from discord import Guild
from discord.ext import commands

from classes.Lucy import Lucy
from utils.logger import logger

class Events(commands.Cog):
    def __init__(self, lucy: Lucy):
        self.lucy = lucy

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Events cog is ready. Listening for events.")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild):
        if self.lucy.api:
            try:
                await self.lucy.api.guild.new(guild.id)
            except Exception as e:
                logger.error(f"Failed to add guild info for guild {guild.name}, ID: {guild.id}", exc_info=e)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        if self.lucy.api:
            try:
                await self.lucy.api.guild.delete(guild.id)
            except Exception as e:
                logger.error(f"Failed to remove guild info for guild {guild.name}, ID: {guild.id}", exc_info=e)

async def setup(lucy: Lucy):
    await lucy.add_cog(Events(lucy))
