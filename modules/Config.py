from discord import (
    app_commands,
    Embed,
    Interaction,
)
from discord.ext.commands import Cog

from decorators import validations
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
    @validations.api_required(description = "cannot set server language.")
    async def lang(self, interaction: Interaction,
        language: str
    ):
        await interaction.response.defer()
        response = await self.lucy.api.guild.patch(interaction.guild.id, lang = language)
        if response["ok"]:
            await interaction.followup.send(
                get_linear_json_value("test", f"lang/{language}")
            )
        else:
            self.lucy._printer.warn(f"Failed to update language for guild {interaction.guild.id}: {response}")
            await interaction.followup.send(embed = Embed(
                title = "⚠️ Error",
                description = "An error occurred while trying to update the server's language setting.",
                color = 0xFF0000)
            )

async def setup(lucy: Lucy):
    await lucy.add_cog(Config(lucy))
