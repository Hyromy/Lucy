from os import getenv, listdir
from re import match as re_match

from discord import (
    Intents,
    Interaction,
    User
)
from discord.ext.commands import Bot

from utils.funcs import get_lang_package
from utils.logger import logger

class Lucy(Bot):
    def __init__(self):
        intents = Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix = ",",
            intents = intents
        )

        self.remove_command("help")

        self.PRODUCTION: bool = getenv("PRODUCTION", "False") == "True"
        self.TESTING_GUILD_ID: str = getenv("TESTING_GUILD_ID")
        self.OWNER: User = None
        self.VERSION: str = None

        from utils.logger import logger
        logger.info(f"Running in {'PRODUCTION' if self.PRODUCTION else 'DEBUG'} mode.")

        self.api = None
        self.cache = dict()
        self.lang = get_lang_package()

    async def load_cogs(self, dir: str = "modules"):
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
        
        logger.info(f"All cogs loaded. (t{len_files}/ l{loaded}/ f{failed}).")

    async def cmd_err(self, cmd_name: str = "unknown", *, interaction: Interaction, error: Exception):
        assert interaction is not None, "Interaction must be provided."
        assert error is not None, "Error must be provided."

        logger.error(f"Error in {cmd_name} command", exc_info=error)
        content = "An error occurred while processing the command."
        if interaction.response.is_done():
            await interaction.followup.send(content, ephemeral = True)
        else:
            await interaction.response.send_message(content, ephemeral = True)

    async def start(self):
        await super().start(getenv(
            ("" if self.PRODUCTION else "TESTING_") + "DISCORD_BOT_TOKEN"
        ))

    async def close(self):
        await super().close()
        if self.api: await self.api.close()
