from discord.ext import commands

from utils.Lucy import Lucy

class Events(commands.Cog):
    def __init__(self, lucy: Lucy):
        self.lucy = lucy

    async def __refill_guild_info(self):
        for guild in self.lucy.guilds:
            try:
                await self.lucy.api.guild.post(guild.id, guild.name)
            except:
                pass

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            await self.lucy.sync_api()
            await self.lucy.sync_commands()
            await self.lucy.sync_owner()
            await self.lucy.sync_version()

        except Exception as e:
            self.lucy._printer.error(f"Error during on_ready setup: {e}", e)
            self.lucy._printer.error(f"Shutting down {self.lucy.user.name} due to setup failure.", e)
            await self.lucy.close()
        
        else:
            print()
            self.lucy._printer.ok(f"{self.lucy.user.name} is ready.")
        
        if self.lucy.api: await self.__refill_guild_info()

async def setup(lucy: Lucy):
    await lucy.add_cog(Events(lucy))
