from discord import (
    app_commands,
    Embed,
    Interaction,
)
from discord.ext.commands import Cog

from decorators import validations
from lang import l
from classes.Lucy import Lucy
from utils.logger import logger

class Config(Cog):
    def __init__(self, lucy: Lucy):
        self.lucy = lucy

        self.show = True
        self.icon = "⚙️"

    @app_commands.command(name = "lang", description = "Set the bot's language for this server.")
    @app_commands.describe(language = "The language to set the bot to.")
    @app_commands.choices(
        language = sorted([
            app_commands.Choice(name = f"({lang.upper()}) {data['__label']}", value = lang)
            for lang, data in l._data.items()
        ], key = lambda x: x.value)
    )
    @validations.api_required(description = "cannot set server language.")
    async def lang(self, interaction: Interaction,
        language: str
    ):
        await interaction.response.defer()
        
        pre_lang = self.lucy.cache["guilds"][str(interaction.guild.id)]["lang"]["code"]
        try:
            response = await self.lucy.api.guild.update(interaction.guild.id, lang = language)
        except Exception as e:
            logger.error("Failed to update guild language", exc_info=e)

            err = l.k.cmds.config.lang.err
            await interaction.followup.send(embed = Embed(
                title = f"⚠️ {l.t(pre_lang, err.title)}",
                description = l.t(pre_lang, err.msg),
                color = 0xFF0000
            ))
        else:
            self.lucy.cache["guilds"][str(interaction.guild.id)] = response

            ok = l.k.cmds.config.lang.ok
            await interaction.followup.send(embed = Embed(
                title = f"✅ {l.t(language, ok.title)}",
                description = l.t(language, ok.msg),
            ))

    @lang.error
    async def lang_error(self, interaction: Interaction, error: Exception):
        await self.lucy._cmd_err("lang", interaction = interaction, error = error)

async def setup(lucy: Lucy):
    await lucy.add_cog(Config(lucy))
