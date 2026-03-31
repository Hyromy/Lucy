from typing import Optional

from discord import (
    app_commands,
    Interaction,
)
from discord.ext.commands import Cog

from components.cmd.help import (
    CommandHelpView,
    cog_help_embed,
    GeneralHelpView,
    general_help_embed,
)
from classes.Lucy import Lucy

class General(Cog):
    def __init__(self, lucy: Lucy):
        self.lucy = lucy

        self.show = True
        self.icon = "🌐"
        self.description = "General commands for all users."

    @app_commands.command(name = "ping", description = "Check the bot's latency.")
    async def ping(self, interaction: Interaction):
        await interaction.response.send_message(
            f"Pong! {self.lucy.latency * 1000:.2f}ms",
            ephemeral = True
        )

    @ping.error
    async def ping_error(self, interaction: Interaction, error: Exception):
        await self.lucy._cmd_err("ping", interaction = interaction, error = error)

    @app_commands.command(description = "Show help information.")
    @app_commands.describe(category = "Choose a category to get help on.")
    async def help(self, interaction: Interaction, category: Optional[str] = None):
        await interaction.response.defer()
        
        lang = "en"
        if self.lucy.api:
            lang = (await self.lucy.api.guild.get(interaction.guild_id))["lang"]

        if not category:
            embed = general_help_embed(self.lucy, lang)
            view = GeneralHelpView(self.lucy, interaction.user, lang)
            view.associate_message(
                await interaction.followup.send(embed = embed, view = view)
            )
            return

        cog = self.lucy.get_cog(category)
        if cog is None:
            return await interaction.followup.send(
                f"Category '{category}' not found.",
                ephemeral = True
            )

        embed = cog_help_embed(cog, self.lucy, lang)
        view = CommandHelpView(self.lucy, interaction.user, lang)
        view.associate_message(
            await interaction.followup.send(embed = embed, view = view)
        )

    @help.autocomplete(name = "category")
    async def help_autocomplete(self, interaction: Interaction, current: str):
        return [
            app_commands.Choice(
                name = f"{getattr(cog, 'icon', '')} {cog.__cog_name__}",
                value = cog.__cog_name__
            )
            for cog in self.lucy.cogs.values()
            if (
                getattr(cog, "show", False)
                and current.lower().strip() in cog.__cog_name__.lower()
            )
        ][:25]

    @help.error
    async def help_error(self, interaction: Interaction, error: Exception):
        await self.lucy._cmd_err("help", interaction = interaction, error = error)

async def setup(lucy: Lucy):
    await lucy.add_cog(General(lucy))
