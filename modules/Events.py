from os import getenv

from aiohttp import ClientSession
from asyncio import sleep
from discord import Object, Guild
from discord.ext import commands

from classes.Api import ApiServices
from classes.Lucy import Lucy
from utils.logger import logger

class Events(commands.Cog):
    def __init__(self, lucy: Lucy):
        self.lucy = lucy

    async def __refill_guild_info(self):
        for guild in self.lucy.guilds:
            try:
                await self.lucy.api.guild.post(guild.id, guild.name)
            except Exception as e:
                if not self.lucy.PRODUCTION:
                    logger.error(f"Failed to refill guild info for guild ID {guild.name}", exc_info=e)

    async def sync_api(self):
        def not_available_msg():
            not_available = [
                "language features",
            ]
            logger.warning(f"API_REST not found in env; API functionality ({', '.join(not_available)}) will be unavailable.")

        logger.info("Initializing API connection")
        rest_url = getenv("API_REST")
        if rest_url:
            try:
                self.lucy.api = ApiServices(rest_url)
                result = await self.lucy.api.test()
                if result["status"] != "ok":
                    raise ConnectionError(f"API test failed for endpoint {self.lucy.api._Api__url}/{self.lucy.api._Api__test_endpoint}")
            
            except Exception as e:
                logger.error(f"Failed to initialize API: {e}", exc_info=e)
                if self.lucy.api:
                    await self.lucy.api.close()
                self.lucy.api = None

            else:
                logger.info(f"API initialized successfully with endpoint {self.lucy.api._Api__url}")
        else:
            not_available_msg()

    async def sync_commands(self):
        def ok():
            logger.info("Commands synced successfully.")

        def error(error_msg: str, e: Exception):
            logger.error(f"Failed to sync commands: {error_msg}", exc_info=e)

        logger.info("Syncing application commands")
        if self.lucy.PRODUCTION:
            try:
                await self.lucy.tree.sync()
            except Exception as e:
                error(str(e), e)            
            else:
                ok()
        else:
            if self.lucy.TESTING_GUILD_ID:
                try:
                    guild = Object(self.lucy.TESTING_GUILD_ID)
                    self.lucy.tree.copy_global_to(guild = guild)
                    await self.lucy.tree.sync(guild = guild)
                except Exception as e:
                    error(str(e), e)
                else:
                    ok()
            else:
                logger.warning("TESTING_GUILD_ID in env is not set. Cannot sync test commands.")
    
    async def sync_owner(self):
        logger.info("Setting OWNER")
        try:
            self.lucy.OWNER = (await self.lucy.application_info()).owner
        except Exception as e:
            logger.error(f"Failed to set OWNER", exc_info=e)
        else:
            logger.info(f"OWNER set to {self.lucy.OWNER}.")

    async def sync_version(self):
        logger.info("Setting VERSION")
        url = getenv("RELEASES_URL")
        if url:
            headers = {}
            github_token = getenv("GITHUB_TOKEN")
            if github_token:
                headers["Authorization"] = f"token {github_token}"
            else:
                logger.warning("GITHUB_TOKEN not found in env; proceeding unauthenticated may lead to rate limiting.")

            session = ClientSession()
            try:
                async with session.get(url, headers = headers) as response:
                    if response.status == 200:
                        self.lucy.VERSION = (await response.json())["tag_name"]
                        logger.info(f"Version set to {self.lucy.VERSION}.")
                    else:
                        logger.error(f"Failed to fetch version info: HTTP {response.status}, {response.reason}.", exc_info=Exception(f"HTTP {response.status}"))
            finally:
                await session.close()
        else:
            logger.warning("No RELEASES_URL found; version info will be unavailable.")

    async def sync_cache(self):        
        logger.info("Syncing cache")
        
        if self.lucy.PRODUCTION:
            cmds = await self.lucy.tree.fetch_commands()
            if len(cmds) == 0:
                logger.warning("No commands found yet. Retrying in 10 seconds...")
                await sleep(10)
                cmds = await self.lucy.tree.fetch_commands()
        else:
            if not self.lucy.TESTING_GUILD_ID:
                logger.warning("TESTING_GUILD_ID in env is not set. Cannot cache test commands.")
                self.lucy.cache["slash_cmds"] = {}
                return

            guild = Object(self.lucy.TESTING_GUILD_ID)
            cmds = await self.lucy.tree.fetch_commands(guild = guild)
        
        self.lucy.cache["slash_cmds"] = {cmd.name: cmd.id for cmd in cmds}
        logger.info(f"{len(cmds)} commands cached.")

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            await self.sync_api()
            await self.sync_commands()
            await self.sync_owner()
            await self.sync_version()
            #await self.sync_cache()

        except Exception as e:
            logger.error(f"Error during on_ready setup. Shutting down {self.lucy.user.name}", exc_info=e)
            await self.lucy.close()
        
        else:
            print()
            logger.info(f"{self.lucy.user.name} is ready.")
        
        if self.lucy.api: await self.__refill_guild_info()

    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild):
        if self.lucy.api:
            try:
                await self.lucy.api.guild.post(guild.id, guild.name)
            except Exception as e:
                logger.error(f"Failed to add guild info for guild ID {guild.name}", exc_info=e)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        if self.lucy.api:
            try:
                await self.lucy.api.guild.delete(guild.id)
            except Exception as e:
                logger.error(f"Failed to remove guild info for guild ID {guild.name}", exc_info=e)

async def setup(lucy: Lucy):
    await lucy.add_cog(Events(lucy))
