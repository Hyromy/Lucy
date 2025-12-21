from discord import (
    app_commands,
    Interaction,
)
from discord.ext.commands import Cog

from utils.funcs import get_supported_languages, get_linear_json_value
from utils.Lucy import Lucy

class Config(Cog):
    def __init__(self, lucy: Lucy):
        self.lucy = lucy

        self.show = True
        self.icon = "⚙️"
        self.description = "Configuration commands for server administrators."

    @app_commands.command(name = "lang", description = "Set the bot's language for this server.")
    @app_commands.describe(language = "The language to set the bot to.")
    @app_commands.choices(
        language = sorted([
            app_commands.Choice(name = f"({lang.upper()}) {data['label']}", value = lang)
            for lang, data in get_supported_languages().items()
        ], key = lambda x: x.value)
    )
    async def lang(self, interaction: Interaction,
        language: str
    ):
        await interaction.response.send_message(
            get_linear_json_value(
                "test",
                f"lang/{language}"
            ),
            ephemeral = True
        )

async def setup(lucy: Lucy):
    await lucy.add_cog(Config(lucy))
