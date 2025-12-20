from discord.ext import commands

from utils.Lucy import Lucy

class Events(commands.Cog):
    def __init__(self, lucy: Lucy):
        self.lucy = lucy

    @commands.Cog.listener()
    async def on_ready(self):
        await self.lucy.sync_commands()
        self.lucy._printer.ok("Bot is ready.")

async def setup(lucy: Lucy):
    await lucy.add_cog(Events(lucy))
