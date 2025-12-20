from typing import Optional

from discord import (
    app_commands,
    Interaction,
)
from discord.ext.commands import Cog

from components.help import (
    CommandHelpView,
    cog_help_embed,
    GeneralHelpView,
    general_help_embed,
)
from utils.Lucy import Lucy

class General(Cog):
    def __init__(self, lucy:Lucy):
        self.lucy = lucy

        self.show = True

    @app_commands.command(name = "ping", description = "Check the bot's latency.")
    async def ping(self, interaction:Interaction):
        await interaction.response.send_message(
            f"Pong! {self.lucy.latency * 1000:.2f}ms",
            ephemeral = True
        )

    @app_commands.command(description = "Show help information.")
    @app_commands.describe(category = "Choose a category to get help on.")
    async def help(self, interaction: Interaction,
        category: Optional[str] = None
    ):
        await interaction.response.defer()

        if not category:
            return await interaction.followup.send(
                embed = general_help_embed(self.lucy),
                view = GeneralHelpView(self.lucy)
            )

        await interaction.followup.send(
            embed = cog_help_embed(
                self.lucy.get_cog(category),
            ),
            view = CommandHelpView(self.lucy)
        )

    @help.autocomplete(name = "category")
    async def help_autocomplete(self, interaction:Interaction, current:str):
        return [
            app_commands.Choice(
                name = f"{getattr(cog, "icon", "")} {cog.__cog_name__}",
                value = cog.__cog_name__
            )
            for cog in self.lucy.cogs.values()
            if (
                getattr(cog, "show", False)
                and current.lower().strip() in cog.__cog_name__.lower()
            )
        ][:25]

async def setup(lucy:Lucy):
    await lucy.add_cog(General(lucy))
