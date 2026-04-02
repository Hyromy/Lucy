from os import listdir
from re import match as re_match
from discord import (
    Intents,
    Interaction,
)
from discord.ext.commands import Bot

from classes.Api import ApiServices
from classes.Config import Config
from utils.logger import logger

class Lucy(Bot):
    def __init__(self, intents: Intents = Intents.default(), *,
        config: Config,
        apiServices: ApiServices = None,
        cache: dict = None,

        **kwargs
    ):
        self.CONFIG = config
        self.api = apiServices
        self.cache = cache or {}

        super().__init__(
            command_prefix = config.PREFIX,
            intents = intents,
            **kwargs
        )
		
    async def setup(self):
        self.remove_command("help")
        await self._load_cogs()

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
        files = [i[:-3] for i in listdir(dir) if re_match(r"^(?!__)[A-Z][a-zA-Z0-9_]*\.py$", i)]
        len_files = len(files)
        logger.info(f"Loading {len_files} cogs from {dir}")
        for filename in files:
            try:
                await self.load_extension(f"{dir}.{filename}")
            
            except Exception as e:
                logger.error(f"Failed to load cog {filename}: {e}", exc_info=e)
                failed += 1
            
            else:
                logger.info(f"Successfully loaded cog {filename}")
                loaded += 1
        
        logger.info(f"Cogs loaded. (t{len_files}/ l{loaded}/ f{failed}).")
