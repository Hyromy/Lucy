from random import choice

from discord import (
    ButtonStyle,
    Color,
    Embed,
    SelectOption,
    Interaction,
)
from discord.ui import (
    Button,
    Select,
    View,
)
from discord.ext.commands import Cog

from utils.Lucy import Lucy

try:
    from utils.vars import CMDS_ID
except ImportError:
    CMDS_ID = dict()

def cog_help_embed(cog: Cog) -> Embed:
    embed = Embed(
        color = Color.blurple(),
        title = f"Ayuda de {getattr(cog, "icon", "")} {cog.__cog_name__}",
        description = getattr(cog, "description", "No hay descripción disponible.")
    )
    embed.add_field(
        name = "Parámetros",
        value = f"`()` Opcional `<>` Obligatorio",
        inline = False
    )

    embed.add_field(name = "", value = "", inline = False)
    for cmd in sorted(cog.get_app_commands(), key = lambda c: c.name):
        args = []
        for name, param in cmd.callback.__annotations__.items():
            if name == "interaction":
                continue

            is_optional = "Optional" in str(param)
            arg_str = "`" + (f"({name})" if is_optional else f"<{name}>") + "`"
            args.append(arg_str)

        embed.add_field(
            name = f"</{cmd.name}:{CMDS_ID.get(cog.__class__.__name__.lower(), dict()).get(cmd.name, 0)}> {' '.join(args) if args else ''}",
            value = cmd.description or "No hay descripción disponible.",
            inline = False
        )

    return embed

def general_help_embed(lucy: Lucy) -> Embed:
    cog = choice(list([
        cog for cog in lucy.cogs.values()
        if getattr(cog, "show", False)
    ]))
    cmd = choice(list(cog.get_app_commands()))

    embed = Embed(
        color = Color.blurple(),
        title = f"Ayuda de {lucy.user.name}",
        description = "Ayuda general del bot, así como las categorías y comandos disponibles."
    )
    embed.add_field(
        name = "Comandos",
        value = f"Usa el menú desplegable o escribe </help:{CMDS_ID.get('commands', dict()).get('help', 0)}> `{cog.__cog_name__} {cmd.name}` para más información",
        inline = False
    )
            
    return embed

class GeneralHelpView(View):
    def __init__(self, lucy: Lucy):
        super().__init__(timeout = 60)

        self.add_item(self.CogSelect(lucy))
        self.add_item(CloseBtn())

    class CogSelect(Select):
        def __init__(self, lucy: Lucy):
            self.lucy = lucy

            super().__init__(
                placeholder = "Choose a category...",
                min_values = 1,
                max_values = 1,
                options = [
                    SelectOption(
                        label = cog.__cog_name__,
                        value = cog.__cog_name__,
                        description = None,
                        emoji = None
                    ) for cog in self.lucy.cogs.values()
                    if getattr(cog, "show", False)
                ]
            )

        async def callback(self, interaction: Interaction):
            await interaction.response.edit_message(
                view = CommandHelpView(self.lucy),
                embed = cog_help_embed(
                    self.lucy.get_cog(self.values[0])
                ),
            )

class CommandHelpView(View):
    def __init__(self, lucy: Lucy):
        super().__init__(timeout = 60)

        self.add_item(self.BackBtn(lucy))
        self.add_item(CloseBtn())

    async def on_timeout(self):
        self.stop()
        for item in self.children:
            item.disabled = True

    class BackBtn(Button):
        def __init__(self, lucy: Lucy):
            super().__init__(
                label = "Back",
                style = ButtonStyle.gray
            )
            self.lucy = lucy

        async def callback(self, interaction: Interaction):
            await interaction.response.edit_message(
                embed = general_help_embed(self.lucy),
                view = GeneralHelpView(self.lucy)
            )

class CloseBtn(Button):
    def __init__(self):
        super().__init__(
            label = "Close",
            style = ButtonStyle.red
        )

    async def callback(self, interaction: Interaction):
        self.view.stop()
        await interaction.message.delete()
