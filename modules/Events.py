from os import getenv

from aiohttp import ClientSession
from discord import Object, Guild
from discord.ext import commands

from utils.Api import Api
from utils.Lucy import Lucy

class Events(commands.Cog):
    def __init__(self, lucy: Lucy):
        self.lucy = lucy

    async def __refill_guild_info(self):
        for guild in self.lucy.guilds:
            try:
                await self.lucy.api.guild.post(guild.id, guild.name)
            except Exception as e:
                if not self.lucy.PRODUCTION:
                    self.lucy._printer.error(f"Failed to refill guild info for guild ID {guild.name}", e)

    async def sync_api(self):
        def not_available_msg():
            not_available = [
                "language features",
            ]
            self.lucy._printer.warn(f"API_REST not found in env; API functionality ({', '.join(not_available)}) will be unavailable.")

        self.lucy._printer.operation("Initializing API connection")
        rest_url = getenv("API_REST")
        if rest_url:
            try:
                self.lucy.api = Api(rest_url)
                result = await self.lucy.api.test()
                if result["status"] != "ok":
                    raise ConnectionError(f"API test failed for endpoint {self.lucy.api._Api__url}/{self.lucy.api._Api__test_endpoint}")
            
            except Exception as e:
                self.lucy._printer.error(f"Failed to initialize API: {e}", e)
                if self.lucy.api:
                    await self.lucy.api.close()
                self.lucy.api = None

            else:
                self.lucy._printer.ok(f"API initialized successfully with endpoint {self.lucy.api._Api__url}")
        else:
            not_available_msg()

    async def sync_commands(self):
        def ok():
            self.lucy._printer.ok("Commands synced successfully.")

        def error(error_msg: str, e: Exception):
            self.lucy._printer.error(f"Failed to sync commands: {error_msg}", e)

        self.lucy._printer.operation("Syncing application commands")
        if self.lucy.PRODUCTION:
            try:
                self.lucy.tree.clear_commands(guild = None)
                await self.lucy.tree.sync()
            except Exception as e:
                error(str(e), e)            
            else:
                ok()
        else:
            if self.lucy.TESTING_GUILD_ID:
                try:
                    guild = Object(self.lucy.TESTING_GUILD_ID)
                    self.lucy.tree.clear_commands(guild = guild)
                    self.lucy.tree.copy_global_to(guild = guild)
                    await self.lucy.tree.sync(guild = guild)
                except Exception as e:
                    error(str(e), e)
                else:
                    ok()
            else:
                self.lucy._printer.warn("TESTING_GUILD_ID in env is not set. Cannot sync test commands.")
    
    async def sync_owner(self):
        self.lucy._printer.operation("Setting OWNER")
        try:
            self.lucy.OWNER = (await self.lucy.application_info()).owner
        except Exception as e:
            self.lucy._printer.error(f"Failed to set OWNER", e)
        else:
            self.lucy._printer.ok(f"OWNER set to {self.lucy.OWNER}.")

    async def sync_version(self):
        self.lucy._printer.operation("Setting VERSION")
        url = getenv("RELEASES_URL")
        if url:
            headers = {}
            github_token = getenv("GITHUB_TOKEN")
            if github_token:
                headers["Authorization"] = f"token {github_token}"
            else:
                self.lucy._printer.warn("GITHUB_TOKEN not found in env; proceeding unauthenticated may lead to rate limiting.")

            session = ClientSession()
            try:
                async with session.get(url, headers = headers) as response:
                    if response.status == 200:
                        self.lucy.VERSION = (await response.json())["tag_name"]
                        self.lucy._printer.ok(f"Version set to {self.lucy.VERSION}.")
                    else:
                        self.lucy._printer.error(f"Failed to fetch version info: HTTP {response.status}, {response.reason}.", Exception(f"HTTP {response.status}"))
            finally:
                await session.close()
        else:
            self.lucy._printer.warn("No RELEASES_URL found; version info will be unavailable.")

    async def sync_cache(self):
        self.lucy._printer.operation("Syncing cache")
        cmds = await self.lucy.tree.fetch_commands()
        self.lucy.cache["slash_cmds"] = {cmd.name: cmd.id for cmd in cmds}

        self.lucy._printer.ok(f"{len(cmds)} commands cached.")

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            await self.sync_api()
            await self.sync_commands()
            await self.sync_owner()
            await self.sync_version()
            await self.sync_cache()

        except Exception as e:
            self.lucy._printer.error(f"Error during on_ready setup. Shutting down {self.lucy.user.name}", e)
            await self.lucy.close()
        
        else:
            print()
            self.lucy._printer.ok(f"{self.lucy.user.name} is ready.")
        
        if self.lucy.api: await self.__refill_guild_info()

    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild):
        if self.lucy.api:
            try:
                await self.lucy.api.guild.post(guild.id, guild.name)
            except Exception as e:
                self.lucy._printer.error(f"Failed to add guild info for guild ID {guild.name}", e)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        if self.lucy.api:
            try:
                await self.lucy.api.guild.delete(guild.id)
            except Exception as e:
                self.lucy._printer.error(f"Failed to remove guild info for guild ID {guild.name}", e)

async def setup(lucy: Lucy):
    await lucy.add_cog(Events(lucy))
