from os import getenv, listdir
from re import match as re_match

from discord import Intents, Object
from discord.ext.commands import Bot

from .Printer import Printer

class Lucy(Bot):
    def __init__(self):
        self._printer = Printer()

        self.PRODUCTION = getenv("PRODUCTION", "False") == "True"
        self.TESTING_GUILD_ID = getenv("TESTING_GUILD_ID")

        super().__init__(
            command_prefix = "!",
            intents = Intents.default()
        )

        self._printer.info(f"Running in {'PRODUCTION' if self.PRODUCTION else 'DEBUG'} mode.")        

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
                self._printer.error(f"Failed to load cog {filename}: {e}")
                failed += 1
            
            else:
                self._printer.ok(f"Successfully loaded cog {filename}")
                loaded += 1
        
        self._printer.info(f"All cogs loaded. (t{len_files}/ l{loaded}/ f{failed}).")

    async def sync_commands(self):
        def ok():
            self._printer.ok("Commands synced successfully.")

        def error(error_msg: str):
            self._printer.error(f"Failed to sync commands: {error_msg}")

        self._printer.operation("Syncing application commands")
        if self.PRODUCTION:
            try:
                await self.tree.sync()
            except Exception as e:
                error(e)            
            else:
                ok()
        else:
            if self.TESTING_GUILD_ID:
                try:
                    guild = Object(self.TESTING_GUILD_ID)
                    self.tree.copy_global_to(guild = guild)
                    await self.tree.sync(guild = guild)
                except Exception as e:
                    error(e)
                else:
                    ok()
            else:
                self._printer.warn("TESTING_GUILD_ID in env is not set. Cannot sync test commands.")
        self._printer.info("Command sync completed.")

    async def start(self):
        await super().start(getenv("DISCORD_BOT_TOKEN"))
