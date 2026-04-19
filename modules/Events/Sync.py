from aiohttp import ClientResponseError
from asyncio import sleep
from os import getenv

from discord import Object
from discord.ext import commands

from classes.Lucy import Lucy
from classes.Api import ApiServices
from utils.logger import logger
from utils.funcs import count_commands_in_files

class Sync(commands.Cog):
    def __init__(self, lucy: Lucy):
        self.lucy = lucy

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            await self.sync_api()
            await self.sync_commands()
            await self.sync_owner()

            await self.sync_slash_cmds_cache()
            await self.sync_tokens_cache()

        except Exception as e:
            logger.error(f"Critical error during Sync.on_ready setup for {self.lucy.user.name}", exc_info = e)
            await self.lucy.close()
        
        else:
            logger.info("Sync setup completed successfully.")
        
        if self.lucy.api:
            await self._refill_guild_info()
            await self._sync_guilds_data()

    async def sync_api(self):
        def not_available_msg():
            not_available = [
                "language features",
                "data syncing",
            ]
            logger.warning(f"API_REST not found in env; API functionality ({', '.join(not_available)}) will be unavailable.")

        rest_url = getenv("API_REST")
        if rest_url:
            try:
                self.lucy.api = ApiServices(rest_url)
                latency = await self.lucy.api.ping()
                
                if latency < 0:
                    raise ConnectionError("API is not responding (Ping returned -1)")
                
                logger.info(f"API connection verified. Latency: {latency:.2f}ms")
            
            except Exception as e:
                logger.error("Failed to initialize API", exc_info = e)
                if self.lucy.api:
                    await self.lucy.api.close()
                self.lucy.api = None

            else:
                logger.info(f"API initialized successfully with endpoint {self.lucy.api._client.path}")
        else:
            not_available_msg()

    async def sync_commands(self):
        def ok():
            logger.info("Commands synced successfully.")

        def error(error_msg: str, e: Exception):
            logger.error(f"Failed to sync commands: {error_msg}", exc_info=e)

        if self.lucy.CONFIG.PRODUCTION:
            try:
                await self.lucy.tree.sync()
            except Exception as e:
                error(str(e), e)            
            else:
                ok()
        else:
            if self.lucy.CONFIG.TESTING_GUILD_ID:
                try:
                    guild = Object(self.lucy.CONFIG.TESTING_GUILD_ID)
                    self.lucy.tree.copy_global_to(guild = guild)
                    await self.lucy.tree.sync(guild = guild)
                except Exception as e:
                    error(str(e), e)
                else:
                    ok()
            else:
                logger.warning("TESTING_GUILD_ID in env is not set. Cannot sync test commands.")

    async def sync_owner(self):
        try:
            self.lucy.OWNER = (await self.lucy.application_info()).owner
        except Exception as e:
            logger.error("Failed to set OWNER", exc_info = e)
        else:
            logger.info(f"OWNER set to {self.lucy.OWNER}.")

    async def sync_slash_cmds_cache(self):
        if self.lucy.CONFIG.PRODUCTION:
            cmds = await self.lucy.tree.fetch_commands()
            if len(cmds) == 0:
                logger.warning("No commands found yet. Retrying in 10 seconds...")
                await sleep(10)
                cmds = await self.lucy.tree.fetch_commands()
        else:
            if not self.lucy.CONFIG.TESTING_GUILD_ID:
                logger.warning("TESTING_GUILD_ID in env is not set. Cannot cache test commands.")
                return

            guild = Object(self.lucy.CONFIG.TESTING_GUILD_ID)
            cmds = await self.lucy.tree.fetch_commands(guild = guild)
        
        self.lucy.cache["slash_cmds"] = {cmd.name: cmd.id for cmd in cmds}
        logger.info(f"Cached ({len(cmds)}/{count_commands_in_files()}) commands.")

    async def sync_tokens_cache(self):
        if self.lucy.api is None:
            logger.warning("API not initialized. Cannot sync tokens.")
            return
        
        try:
            await self.lucy.api.tokens.get(
                self.lucy.CONFIG.API_REST_USERNAME,
                self.lucy.CONFIG.API_REST_PASSWORD
            )

        except Exception as e:
            logger.error("Failed to sync tokens", exc_info = e)
        
        else:
            logger.info("Tokens synced successfully.")

    async def _refill_guild_info(self):
        for guild in self.lucy.guilds:
            try:
                await self.lucy.api.guild.new(guild.id)
            except ClientResponseError as e:
                if e.status in (400, 409):
                    if not self.lucy.CONFIG.PRODUCTION:
                        logger.info(f"Guild already exists in API: {guild.name} ({guild.id})")
                    continue

                logger.error(
                    f"Error HTTP while refilling guild info for guild {guild.name} ({guild.id})",
                    exc_info=e
                )

            except Exception as e:
                logger.error(
                    f"Unexpected error while refilling guild info for guild {guild.name} ({guild.id})",
                    exc_info=e
                )

    async def _sync_guilds_data(self):
        try:
            guilds = await self.lucy.api.guild.get()
            self.lucy.cache["guilds"] = {guild["id"]: guild for guild in guilds}
        except Exception as e:
            logger.error("Failed to sync guilds data", exc_info=e)

async def setup(lucy: Lucy):
    await lucy.add_cog(Sync(lucy))
