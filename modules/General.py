from typing import Optional

from discord import (
    app_commands,
    Interaction,
    Embed,
)
from discord.ext.commands import Cog

from components.cmd.help import (
    cog_help_embed,
    GeneralHelpView,
    general_help_embed,
)
from classes.Lucy import Lucy
from utils.funcs import (
    get_cogs_dict,
    get_bot_info
)
from lang import l

class General(Cog):
    def __init__(self, lucy: Lucy):
        self.lucy = lucy

        self.show = True
        self.icon = "🌐"

    @app_commands.command(name = "ping", description = "Check the bot's latency.")
    async def ping(self, interaction: Interaction):
        lang = self.lucy.cache["guilds"][str(interaction.guild.id)]["lang"]["code"]

        api_latency = "Offline"
        latency = await self.lucy.api.ping() if self.lucy.api else -1
        if latency > 0:
            api_latency = f"{latency:.0f}ms"

        embed = Embed(title = "🏓 Pong!")
        embed.add_field(name = l.t(lang, l.k.cmds.general.ping.bot), value = f"{interaction.client.latency * 1000:.0f}ms")
        embed.add_field(name = l.t(lang, l.k.cmds.general.ping.api), value = api_latency)

        await interaction.response.send_message(embed = embed)

    @ping.error
    async def ping_error(self, interaction: Interaction, error: Exception):
        await self.lucy._cmd_err("ping", interaction = interaction, error = error)

    @app_commands.command(description = "Show help information.")
    @app_commands.describe(category = "Choose a category to get help on.")
    async def help(self, interaction: Interaction, category: Optional[str] = None):
        await interaction.response.defer()
        
        lang = self.lucy.cache["guilds"][str(interaction.guild.id)]["lang"]["code"]

        cogs_dict = get_cogs_dict(self.lucy)
        bot_info = get_bot_info(self.lucy)

        if not category:
            view = GeneralHelpView(bot_info, cogs_dict, interaction.user, lang)
            view.associate_message(
                await interaction.followup.send(
                    embed = general_help_embed(
                        lang, 
                        bot_info["bot_name"],
                        bot_info["bot_avatar_url"],
                        bot_info["owner_name"],
                        bot_info["owner_avatar_url"],
                        bot_info["version"],
                        bot_info["slash_cmds_cache"].get('help', 0),
                        cogs_dict
                    ),
                    view = view
                )
            )
            return

        cog_info = cogs_dict.get(category.capitalize())
        if cog_info is None:
            await interaction.followup.send(
                f"Category '{category}' not found.",
                ephemeral = True
            )
            return

        embed = cog_help_embed(cog_info, lang, **bot_info)
        view = GeneralHelpView(bot_info, cogs_dict, interaction.user, lang, category = category)

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
