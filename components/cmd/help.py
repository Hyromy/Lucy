from random import choice
from discord import (
    Color,
    Embed,
    Interaction,
    User,
    SelectOption,
    ButtonStyle,
)
from discord.ext.commands import Cog
from classes.Lucy import Lucy
from components.elements import (
    BaseView,
    BaseButton,
    BaseSelect
)
from lang import l

def footer_embed(embed: Embed, lucy: Lucy, dev_by: str):
    embed.set_footer(
        text = f"{dev_by} {lucy.OWNER.name} | {lucy.user.name} {lucy.VERSION or ''}",
        icon_url = lucy.OWNER.display_avatar.url
    )

def general_help_embed(lucy: Lucy, lang: str = "en") -> Embed:
    _help = l.k.cmds.general.help
    dev_by = l.t(lang, _help.footer.text)
    lang_data = _help.not_category.embed
    visible_cogs = [cog for cog in lucy.cogs.values() if getattr(cog, "show", False)]
    
    if not visible_cogs:
        embed = Embed(
            color = Color.blurple(),
            title = l.t(lang, lang_data.title),
            description = "No categories are available yet."
        )
        embed.set_thumbnail(url = lucy.user.display_avatar.url)
        footer_embed(embed, lucy, dev_by)
        return embed
        
    cogs_with_commands = [cog for cog in visible_cogs if list(cog.get_app_commands())]
    if not cogs_with_commands:
        embed = Embed(
            color = Color.blurple(),
            title = l.t(lang, lang_data.title),
            description = "No commands are available yet."
        )
        embed.set_thumbnail(url = lucy.user.display_avatar.url)
        footer_embed(embed, lucy, dev_by)
        return embed
        
    random_cog = choice(cogs_with_commands)
    random_cmd = choice(list(random_cog.get_app_commands()))
    embed = Embed(
        color = Color.blurple(),
        title = l.t(lang, lang_data.title),
        description = l.t(lang, lang_data.description)
    )
    embed.set_thumbnail(url = lucy.user.display_avatar.url)
    embed.add_field(
        name = l.t(lang, lang_data.field._0.name),
        value = f"{l.t(lang, lang_data.field._0.value._0)} </help:{lucy.cache['slash_cmds'].get('help', 0)}> `{random_cog.__cog_name__} {random_cmd.name}` {l.t(lang, lang_data.field._0.value._1)}",
        inline = False
    )
    footer_embed(embed, lucy, dev_by)
    return embed

def cog_help_embed(cog: Cog, lucy: Lucy, lang="en") -> Embed:
    _help = l.k.cmds.general.help
    dev_by = l.t(lang, _help.footer.text)
    lang_data = _help.category.embed

    embed = Embed(
        color = Color.blurple(),
        title = l.t(lang, lang_data.title).format((cog.icon + " " if getattr(cog, "icon", None) else ""), cog.__cog_name__),
        description = l.t(lang, lang_data.description, key = cog.__cog_name__.lower()) or l.t(lang, lang_data.description.n_a)
    )
    embed.set_thumbnail(url = lucy.user.display_avatar.url)
    embed.add_field(
        name = l.t(lang, lang_data.field._0.name),
        value = f"`()` {l.t(lang, lang_data.field._0.value._0)} `<>` {l.t(lang, lang_data.field._0.value._1)}",
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
            value = l.t(lang, lang_data.field._1, key = cmd.name) or l.t(lang, lang_data.description.n_a),
            inline = False
        )
        
    footer_embed(embed, lucy, dev_by)
    return embed

class GeneralHelpView(BaseView):
    def __init__(self, lucy: Lucy, user: User, lang: str = "en"):
        super().__init__(
            shared = False,
            author = user,
            delete_on_timeout = True
        )
        _help = l.k.cmds.general.help
        lang_data = _help.not_category.view
        
        visible_cogs = [cog for cog in lucy.cogs.values() if getattr(cog, "show", False)]
        if visible_cogs:
            self.append(self.CogSelect(lucy, user, l.t(lang, lang_data.select.placeholder), lang = lang))
        self.append(BaseButton(l.t(lang, _help.view.close_button),
            is_close = True
        ))

    class CogSelect(BaseSelect):
        def __init__(self, lucy: Lucy, user: User, placeholder: str, lang: str = "en"):
            self.lucy = lucy
            self.user = user
            self.lang = lang
            options = [
                SelectOption(
                    label = (cog.icon + " " if getattr(cog, "icon", None) else "") + cog.__cog_name__,
                    value = cog.__cog_name__,
                ) for cog in self.lucy.cogs.values()
                if getattr(cog, "show", False)
            ]
            
            super().__init__(placeholder,
                options = options,
                on_select = self.on_select
            )

        async def on_select(self, interaction: Interaction, values: list[str]):
            view = CommandHelpView(self.lucy, self.user, lang = self.lang)
            view.associate_message(interaction.message)
            
            await interaction.response.edit_message(
                view = view,
                embed = cog_help_embed(
                    self.lucy.get_cog(values[0]),
                    self.lucy,
                    self.lang
                ),
            )

class CommandHelpView(BaseView):
    def __init__(self, lucy: Lucy, user: User, lang: str = "en"):
        super().__init__(
            shared = False,
            author = user,
            delete_on_timeout = True
        )
        _help = l.k.cmds.general.help
        lang_data = _help.category.view
        
        self.append(BackBtn(lucy, user, l.t(lang, lang_data.button.label), lang = lang))
        self.append(BaseButton(l.t(lang, _help.view.close_button),
            is_close = True
        ))

class BackBtn(BaseButton):
    def __init__(self, lucy: Lucy, user: User, label: str, lang: str = "en"):
        super().__init__(label or "Back",
            style = ButtonStyle.secondary, 
            on_click = self.on_click
        )
        self.lucy = lucy
        self.user = user
        self.lang = lang

    async def on_click(self, interaction: Interaction):
        embed = general_help_embed(self.lucy, self.lang)
        view = GeneralHelpView(self.lucy, self.user, self.lang)
        view.associate_message(interaction.message)
        await interaction.response.edit_message(embed=embed, view=view)
