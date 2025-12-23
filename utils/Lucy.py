from os import getenv, listdir
from re import match as re_match

from aiohttp import ClientSession
from discord import Intents, Object, User
from discord.ext.commands import Bot

from .Printer import Printer
from .Api import Api

class Lucy(Bot):
    def __init__(self):
        super().__init__(
            command_prefix = "!",
            intents = Intents.default()
        )

        self.PRODUCTION: bool = getenv("PRODUCTION", "False") == "True"
        self.TESTING_GUILD_ID: str = getenv("TESTING_GUILD_ID")
        self.OWNER: User = None
        self.VERSION: str = None

        self._printer = Printer()
        self._printer.info(f"Running in {'PRODUCTION' if self.PRODUCTION else 'DEBUG'} mode.")

        self.api = None

    async def load_cogs(self, dir: str = "modules"):
        loaded = 0
        failed = 0
        files = [i[:-3] for i in listdir(dir) if re_match(r"^(?!__)[A-Z][a-zA-Z0-9_]*\.py$", i)]
        len_files = len(files)
        self._printer.operation(f"Loading {len_files} cogs from {dir}")
        for filename in files:
            try:
                await self.load_extension(f"{dir}.{filename}")
            
            except Exception as e:
                self._printer.error(f"Failed to load cog {filename}: {e}", e)
                failed += 1
            
            else:
                self._printer.ok(f"Successfully loaded cog {filename}")
                loaded += 1
        
        self._printer.info(f"All cogs loaded. (t{len_files}/ l{loaded}/ f{failed}).")

    async def sync_api(self):
        def not_available_msg():
            not_available = [
                "language features",
            ]
            self._printer.warn(f"API_REST not found in env; API functionality ({', '.join(not_available)}) will be unavailable.")

        self._printer.operation("Initializing API connection")
        rest_url = getenv("API_REST")
        if rest_url:
            try:
                self.api = Api(rest_url)
                result = await self.api.test()
                if result["status"] != "ok":
                    raise ConnectionError(f"API test failed for endpoint {self.api._Api__url}/{self.api._Api__test_endpoint}")
            
            except Exception as e:
                self._printer.error(f"Failed to initialize API: {e}", e)
                if self.api:
                    await self.api.close()
                self.api = None

            else:
                self._printer.ok(f"API initialized successfully with endpoint {self.api._Api__url}")
        else:
            not_available_msg()

    async def sync_commands(self):
        def ok():
            self._printer.ok("Commands synced successfully.")

        def error(error_msg: str, e: Exception):
            self._printer.error(f"Failed to sync commands: {error_msg}", e)

        self._printer.operation("Syncing application commands")
        if self.PRODUCTION:
            try:
                await self.tree.sync()
            except Exception as e:
                error(str(e), e)            
            else:
                ok()
        else:
            if self.TESTING_GUILD_ID:
                try:
                    guild = Object(self.TESTING_GUILD_ID)
                    self.tree.copy_global_to(guild = guild)
                    await self.tree.sync(guild = guild)
                except Exception as e:
                    error(str(e), e)
                else:
                    ok()
            else:
                self._printer.warn("TESTING_GUILD_ID in env is not set. Cannot sync test commands.")

    async def sync_owner(self):
        self._printer.operation("Setting OWNER")
        try:
            self.OWNER = (await self.application_info()).owner
        except Exception as e:
            self._printer.error(f"Failed to set OWNER: {e}", e)
        else:
            self._printer.ok(f"OWNER set to {self.OWNER}.")

    async def sync_version(self):
        self._printer.operation("Setting VERSION")
        url = getenv("RELEASES_URL")
        if url:
            headers = {}
            github_token = getenv("GITHUB_TOKEN")
            if github_token:
                headers["Authorization"] = f"token {github_token}"
            else:
                self._printer.warn("GITHUB_TOKEN not found in env; proceeding unauthenticated may lead to rate limiting.")

            session = ClientSession()
            try:
                async with session.get(url, headers = headers) as response:
                    if response.status == 200:
                        self.VERSION = (await response.json())["tag_name"]
                        self._printer.ok(f"Version set to {self.VERSION}.")
                    else:
                        self._printer.error(f"Failed to fetch version info: HTTP {response.status}, {response.reason}.", Exception(f"HTTP {response.status}"))
            finally:
                await session.close()
        else:
            self._printer.warn("No RELEASES_URL found; version info will be unavailable.")

    async def start(self):
        await super().start(getenv(
            ("" if self.PRODUCTION else "TESTING_") + "DISCORD_BOT_TOKEN"
        ))

    async def close(self):
        await super().close()
        if self.api: await self.api.close()
