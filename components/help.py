from random import choice

from discord import (
    ButtonStyle,
    Color,
    Embed,
    Forbidden,
    HTTPException,
    Interaction,
    Message,
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

from classes.Lucy import Lucy
from utils.logger import logger


def bind_view_message(view: View, message: Message | None):
    if message is not None:
        view.msg = message

def footer_embed(embed: Embed, lucy: Lucy, dev_by: str):
    embed.set_footer(
        text = f"{dev_by} {lucy.OWNER.name} | {lucy.user.name} {lucy.VERSION or ""}",
        icon_url = lucy.OWNER.display_avatar.url
    )

def general_help_embed(lucy: Lucy, lang: str = "en") -> Embed:
    n_a = lucy.lang[lang]["__not_available"] or "Unknown translation"
    _help = lucy.lang[lang]["cmds"]["general"]["help"]
    dev_by = _help["__footer"]["text"] or n_a
    lang = _help["not_category"]["embed"]

    visible_cogs = [
        cog for cog in lucy.cogs.values()
        if getattr(cog, "show", False)
    ]

    if not visible_cogs:
        embed = Embed(
            color = Color.blurple(),
            title = lang["title"] or n_a,
            description = "No categories are available yet."
        )
        embed.set_thumbnail(url = lucy.user.display_avatar.url)
        footer_embed(embed, lucy, dev_by)
        return embed

    cogs_with_commands = [cog for cog in visible_cogs if list(cog.get_app_commands())]
    if not cogs_with_commands:
        embed = Embed(
            color = Color.blurple(),
            title = lang["title"] or n_a,
            description = "No commands are available yet."
        )
        embed.set_thumbnail(url = lucy.user.display_avatar.url)
        footer_embed(embed, lucy, dev_by)
        return embed

    random_cog = choice(cogs_with_commands)
    random_cmd = choice(list(random_cog.get_app_commands()))

    embed = Embed(
        color = Color.blurple(),
        title = lang["title"] or n_a,
        description = lang["description"] or n_a
    )
    embed.set_thumbnail(url = lucy.user.display_avatar.url)
    embed.add_field(
        name = lang["field"][0]["name"] or n_a,
        value = f"{lang["field"][0]["value"][0] or n_a} </help:{lucy.cache['slash_cmds'].get('help', 0)}> `{random_cog.__cog_name__} {random_cmd.name}` {lang["field"][0]["value"][1] or n_a}",
        inline = False
    )
    footer_embed(embed, lucy, dev_by)

    return embed

def cog_help_embed(cog: Cog, lucy: Lucy, lang = "en") -> Embed:
    n_a = lucy.lang[lang]["__not_available"] or "Unknown translation"
    _help = lucy.lang[lang]["cmds"]["general"]["help"]
    dev_by = _help["__footer"]["text"] or n_a
    lang = _help["category"]["embed"]

    embed = Embed(
        color = Color.blurple(),
        title = lang["title"].format((cog.icon + " " if getattr(cog, "icon") else ""), cog.__cog_name__) or n_a,
        description = (lang["description"][cog.__cog_name__.lower()] or lang["description"]["__n_a"]) or n_a
    )
    embed.set_thumbnail(url = lucy.user.display_avatar.url)
    embed.add_field(
        name = lang["field"][0]["name"] or n_a,
        value = f"`()` {lang["field"][0]["value"][0] or n_a} `<>` {lang["field"][0]["value"][1] or n_a}",
        inline = False
    )

    embed.add_field(name = "", value = "", inline = False)
    for cmd in sorted(cog.get_app_commands(), key = lambda c: c.name):
        args = []
        for name, param in cmd.callback.__annotations__.items():
            if name != "interaction":
                is_optional = "Optional" in str(param)
                arg_str = "`" + (f"({name})" if is_optional else f"<{name}>") + "`"
                args.append(arg_str)

        embed.add_field(
            name = f"</{cmd.name}:{lucy.cache['slash_cmds'].get(cmd.name, 0)}> {' '.join(args) if args else ''}",
            value = (lang["field"][1][cmd.name] or lang["description"]["__n_a"]) or n_a,
            inline = False
        )
    footer_embed(embed, lucy, dev_by)

    return embed

async def time_out(view: View):
    view.stop()
    if hasattr(view, "msg") and view.msg:
        try:
            await view.msg.delete()
        except (NotFound, Forbidden):
            pass
        except HTTPException as e:
            logger.error("Failed to delete help message on timeout.", exc_info=e)
        finally:
            view.msg = None

async def invasor_interaction(interaction: Interaction):
    await interaction.response.send_message(
        "You cannot interact with this menu.",
        ephemeral = True
    )

class GeneralHelpView(View):
    def __init__(self, lucy: Lucy, user: User, lang: str = "en"):
        super().__init__(timeout = 300)

        _lang = lang
        n_a = lucy.lang[lang]["__not_available"] or "Unknown translation"
        _help = lucy.lang[lang]["cmds"]["general"]["help"]
        lang = _help["not_category"]["view"]

        visible_cogs = [
            cog for cog in lucy.cogs.values()
            if getattr(cog, "show", False)
        ]
        if visible_cogs:
            self.add_item(self.CogSelect(lucy, user, lang["select"]["placeholder"] or n_a, lang = _lang))
        self.add_item(CloseBtn(user, _help["__view"]["close_button"] or n_a))

    async def on_timeout(self):
        await time_out(self)

    class CogSelect(Select):
        def __init__(self, lucy: Lucy, user: User, placeholder: str, lang: str = "en"):
            self.lucy = lucy
            self.user = user
            self.lang = lang

            super().__init__(
                placeholder = placeholder,
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

            view = CommandHelpView(self.lucy, self.user, lang = self.lang)
            bind_view_message(view, interaction.message)

            await interaction.response.edit_message(
                view = view,
                embed = cog_help_embed(
                    self.lucy.get_cog(self.values[0]),
                    self.lucy,
                    lang = self.lang
                ),
            )

class CommandHelpView(View):
    def __init__(self, lucy: Lucy, user: User, lang: str = "en"):
        super().__init__(timeout = 300)

        _lang = lang
        n_a = lucy.lang[lang]["__not_available"] or "Unknown translation"
        _help = lucy.lang[lang]["cmds"]["general"]["help"]
        lang = _help["category"]["view"]

        self.add_item(self.BackBtn(lucy, user, lang["button"]["label"] or n_a, lang = _lang))
        self.add_item(CloseBtn(user, _help["__view"]["close_button"] or n_a))

    async def on_timeout(self):
        await time_out(self)

    class BackBtn(Button):
        def __init__(self, lucy: Lucy, user: User, label: str, lang: str = "en"):
            super().__init__(
                label = label or "Back",
                style = ButtonStyle.gray
            )
            self.lucy = lucy
            self.user = user
            self.lang = lang

        async def callback(self, interaction: Interaction):
            if interaction.user != self.user:
                return await invasor_interaction(interaction)

            embed = general_help_embed(self.lucy, self.lang)
            view = GeneralHelpView(self.lucy, self.user, self.lang)
            bind_view_message(view, interaction.message)
            await interaction.response.edit_message(embed = embed, view = view)

class CloseBtn(Button):
    def __init__(self, user: User, label: str):
        super().__init__(
            label = label or "Close",
            style = ButtonStyle.red
        )
        self.user = user

    async def callback(self, interaction: Interaction):
        if interaction.user != self.user:
            return await invasor_interaction(interaction)

        self.view.stop()
        try:
            await interaction.message.delete()
        except (NotFound, Forbidden):
            return
        except HTTPException as e:
            logger.error("Failed to delete help message on close.", exc_info=e)
