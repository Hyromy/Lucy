import os
from discord import (
    Intents,
    Interaction,
)
from discord.ext.commands import Bot

from classes.Api import ApiServices
from classes.Config import Config
from utils.logger import logger
from utils.funcs import is_valid_cog_filename

class Lucy(Bot):
    def __init__(self, intents: Intents = Intents.default(), *,
        config: Config,
        apiServices: ApiServices = None,
        cache: dict = None,

        **kwargs
    ):
        self.CONFIG = config
        self.api = apiServices
        self.cache = cache or {
            "tokens": {},
            "slash_cmds": {},
            "guilds": {},
        }

        super().__init__(
            command_prefix = config.PREFIX,
            intents = intents,
            **kwargs
        )
		
    async def setup(self):
        self.remove_command("help")
        await self._load_cogs()

        logger.info("Setup complete.")

    async def start(self, token: str):
        await super().start(token)

    async def close(self):
        await super().close()
        if self.api:
            await self.api.close()
        
    async def _cmd_err(self, cmd_name = "unknown", *,
        interaction: Interaction,
        error: Exception
    ):
        assert interaction is not None, "Interaction must be provided."
        assert error is not None, "Error must be provided."
        
        logger.error(f"Error in {cmd_name} command", exc_info = error)
        
        content = "An error occurred while processing the command."
        if interaction.response.is_done():
            await interaction.followup.send(content, ephemeral = True)
        
        else:
            await interaction.response.send_message(content, ephemeral = True)

    async def _load_cogs(self, dir: str = "modules"):
        loaded = 0
        failed = 0
        all_extension_paths = []

        for root, _, files in os.walk(dir):
            for filename in files:
                if is_valid_cog_filename(filename):
                    relative_path = os.path.relpath(os.path.join(root, filename[:-3]), os.getcwd())
                    extension_path = relative_path.replace(os.sep, ".")
                    all_extension_paths.append(extension_path)

        len_files = len(all_extension_paths)
        logger.info(f"Loading {len_files} cogs from {dir} (recursively)")

        for extension in all_extension_paths:
            try:
                await self.load_extension(extension)
                logger.info(f"Successfully loaded extension {extension}")
                loaded += 1
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}", exc_info=e)
                failed += 1
        
        logger.info(f"Cogs loaded. (t{len_files}/ l{loaded}/ f{failed}).")
