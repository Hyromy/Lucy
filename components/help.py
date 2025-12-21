from random import choice

from discord import (
    ButtonStyle,
    Color,
    Embed,
    Interaction,
    NotFound,
    SelectOption,
    User,
)
from discord.ext.commands import Cog
from discord.ui import (
    Button,
    Select,
    View,
)

from utils.funcs import possessive, get_linear_json_value
from utils.Lucy import Lucy
from utils.Printer import Printer

def footer_embed(embed: Embed, lucy: Lucy):
    embed.set_footer(
        text = f"Developed by {lucy.OWNER.name} | {lucy.user.name} v{lucy.VERSION}",
        icon_url = lucy.OWNER.display_avatar.url
    )

def general_help_embed(lucy: Lucy) -> Embed:
    random_cog = choice(list([
        cog for cog in lucy.cogs.values()
        if getattr(cog, "show", False)
    ]))
    random_cmd = choice(list(random_cog.get_app_commands()))
    cmd_id = get_linear_json_value(f"general.help.{'prod' if lucy.PRODUCTION else 'test'}") or 0

    embed = Embed(
        color = Color.blurple(),
        title = f"{possessive(lucy.user.name)} help",
        description = "General bot help, as well as available categories and commands."
    )
    embed.set_thumbnail(url = lucy.user.display_avatar.url)
    embed.add_field(
        name = "Commands",
        value = f"Use the dropdown menu or type </help:{cmd_id}> `{random_cog.__cog_name__} {random_cmd.name}` for more information",
        inline = False
    )
    footer_embed(embed, lucy)

    return embed

def cog_help_embed(cog: Cog, lucy: Lucy) -> Embed:
    embed = Embed(
        color = Color.blurple(),
        title = (cog.icon + " " if getattr(cog, "icon") else "") + cog.__cog_name__ + " commands",
        description = getattr(cog, "description", "No description available.")
    )
    embed.set_thumbnail(url = lucy.user.display_avatar.url)
    embed.add_field(
        name = "Parameters",
        value = f"`()` Optional `<>` Required",
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

        cmd_id = get_linear_json_value(f"{cog.__cog_name__.lower()}.{cmd.name}.{'prod' if lucy.PRODUCTION else 'test'}") or 0
        embed.add_field(
            name = f"</{cmd.name}:{cmd_id}> {' '.join(args) if args else ''}",
            value = cmd.description or "No hay descripción disponible.",
            inline = False
        )
    footer_embed(embed, lucy)

    return embed

async def time_out(view: View):
    view.stop()
    if hasattr(view, "msg") and view.msg:
        try:
            await view.msg.delete()
        except NotFound:
            pass
        except Exception as e:
            Printer().error(f"Failed to delete help message on timeout: {e}")

async def invasor_interaction(interaction: Interaction):
    await interaction.response.send_message(
        "You cannot interact with this menu.",
        ephemeral = True
    )

class GeneralHelpView(View):
    def __init__(self, lucy: Lucy, user: User):
        super().__init__(timeout = 300)

        self.add_item(self.CogSelect(lucy, user))
        self.add_item(CloseBtn(user))

    async def on_timeout(self):
        await time_out(self)

    class CogSelect(Select):
        def __init__(self, lucy: Lucy, user: User):
            self.lucy = lucy
            self.user = user

            super().__init__(
                placeholder = "Choose a category...",
                min_values = 1,
                max_values = 1,
                options = [
                    SelectOption(
                        label = (cog.icon + " " if getattr(cog, "icon") else "") + cog.__cog_name__,
                        value = cog.__cog_name__,
                        description = None,
                        emoji = None
                    ) for cog in self.lucy.cogs.values()
                    if getattr(cog, "show", False)
                ]
            )

        async def callback(self, interaction: Interaction):
            if interaction.user != self.user:
                return await invasor_interaction(interaction)

            await interaction.response.edit_message(
                view = CommandHelpView(self.lucy, self.user),
                embed = cog_help_embed(
                    self.lucy.get_cog(self.values[0]),
                    self.lucy
                ),
            )

class CommandHelpView(View):
    def __init__(self, lucy: Lucy, user: User):
        super().__init__(timeout = 300)

        self.add_item(self.BackBtn(lucy, user))
        self.add_item(CloseBtn(user))

    async def on_timeout(self):
        await time_out(self)

    class BackBtn(Button):
        def __init__(self, lucy: Lucy, user: User):
            super().__init__(
                label = "Back",
                style = ButtonStyle.gray
            )
            self.lucy = lucy
            self.user = user

        async def callback(self, interaction: Interaction):
            if interaction.user != self.user:
                return await invasor_interaction(interaction)

            embed = general_help_embed(self.lucy)
            view = GeneralHelpView(self.lucy, self.user)
            view.msg = await interaction.response.edit_message(embed = embed, view = view)

class CloseBtn(Button):
    def __init__(self, user: User):
        super().__init__(
            label = "Close",
            style = ButtonStyle.red
        )
        self.user = user

    async def callback(self, interaction: Interaction):
        if interaction.user != self.user:
            return await invasor_interaction(interaction)

        self.view.stop()
        await interaction.message.delete()
