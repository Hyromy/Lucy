from random import choice
from discord import (
    Color,
    Embed,
    Interaction,
    User,
    SelectOption,
    ButtonStyle,
)
from components.elements import (
    BaseView,
    BaseButton,
    BaseSelect
)
from lang import l

def footer_embed(embed: Embed, owner_name: str, owner_avatar_url: str, bot_name: str, version: str, lang: str = "en"):
    embed.set_footer(
        text = f"{l.t(lang, l.k.cmds.general.help.footer.text)} {owner_name} | {bot_name} {version or ''}",
        icon_url = owner_avatar_url
    )

def general_help_embed(
    lang: str,
    bot_name: str,
    bot_avatar_url: str,
    owner_name: str,
    owner_avatar_url: str,
    version: str,
    slash_help_id: int,
    cogs_dict: dict
) -> Embed:
    _help = l.k.cmds.general.help
    lang_data = _help.not_category.embed
    
    visible_cogs = [cog for cog in cogs_dict.values() if cog['show']]
    
    if not visible_cogs:
        embed = Embed(
            color = Color.blurple(),
            title = l.t(lang, lang_data.title),
            description = "No categories are available yet."
        )
        embed.set_thumbnail(url = bot_avatar_url)
        footer_embed(embed, owner_name, owner_avatar_url, bot_name, version, lang)
        return embed
        
    cogs_with_commands = [cog for cog in visible_cogs if cog['app_commands']]
    if not cogs_with_commands:
        embed = Embed(
            color = Color.blurple(),
            title = l.t(lang, lang_data.title),
            description = "No commands are available yet."
        )
        embed.set_thumbnail(url = bot_avatar_url)
        footer_embed(embed, owner_name, owner_avatar_url, bot_name, version, lang)
        return embed
        
    random_cog = choice(cogs_with_commands)
    random_cmd_name = choice(random_cog['app_commands'])
    
    embed = Embed(
        color = Color.blurple(),
        title = l.t(lang, lang_data.title),
        description = l.t(lang, lang_data.description)
    )
    embed.set_thumbnail(url = bot_avatar_url)
    embed.add_field(
        name = l.t(lang, lang_data.field._0.name),
        value = f"{l.t(lang, lang_data.field._0.value._0)} </help:{slash_help_id}> `{random_cog['name']} {random_cmd_name}` {l.t(lang, lang_data.field._0.value._1)}",
        inline = False
    )
    footer_embed(embed, owner_name, owner_avatar_url, bot_name, version, lang)
    return embed

def cog_help_embed(
    cog_info: dict,
    lang: str,
    bot_name: str,
    bot_avatar_url: str,
    owner_name: str,
    owner_avatar_url: str,
    version: str,
    slash_cmds_cache: dict
) -> Embed:
    _help = l.k.cmds.general.help
    lang_data = _help.category.embed

    cog_name = cog_info['name'].capitalize()
    icon = (cog_info['icon'] + " ") if cog_info['icon'] else ""

    embed = Embed(
        color = Color.blurple(),
        title = l.t(lang, lang_data.title).format(icon, cog_name),
        description = l.t(lang, lang_data.description, key = cog_info['name']) or l.t(lang, lang_data.description.n_a)
    )
    embed.set_thumbnail(url = bot_avatar_url)
    embed.add_field(
        name = l.t(lang, lang_data.field._0.name),
        value = f"`()` {l.t(lang, lang_data.field._0.value._0)} `<>` {l.t(lang, lang_data.field._0.value._1)}",
        inline = False
    )
    
    for cmd_name in sorted(cog_info['app_commands']):
        slash_id = slash_cmds_cache.get(cmd_name, 0)
        embed.add_field(
            name = f"</{cmd_name}:{slash_id}>",
            value = l.t(lang, lang_data.field._1, key = cmd_name) or l.t(lang, lang_data.description.n_a),
            inline = False
        )
        
    footer_embed(embed, owner_name, owner_avatar_url, bot_name, version, lang)
    return embed

class GeneralHelpView(BaseView):
    def __init__(self, bot_info: dict, cogs_dict: dict, user: User, lang: str = "en", category: str = None):
        self.bot_info = bot_info
        self.cogs_dict = cogs_dict
        self.lang = lang

        _help = l.k.cmds.general.help
        lang_data = _help.not_category.view

        super().__init__(
            BaseSelect(l.t(lang, lang_data.select.placeholder),
                options = [
                    SelectOption(
                        label = f"{(cog['icon'] + ' ') if cog['icon'] else ''}{l.t(lang, l.k.cmds, key = f"{cog['name']}._category_name")}",
                        value = cog['name'].capitalize(),
                        default = (category and category.capitalize() == cog['name'].capitalize())
                    ) 
                    for cog in sorted(cogs_dict.values(), key = lambda c: c['name']) if cog['show']
                ],
                on_select = self.on_select
            ),
            BaseButton(l.t(lang, _help.view.close_button),
                is_close = True
            ),
            shared = False,
            author = user,
            delete_on_timeout = True
        )

        if category:
            self._add_back_button()

    def _add_back_button(self):
        """ Ayudante interno para añadir el botón de retroceso si no existe. """
        if not any(isinstance(child, BaseButton) and getattr(child, "is_back", False) for child in self.children):
            back_btn = BaseButton(
                l.t(self.lang, l.k.cmds.general.help.category.view.button.label),
                style = ButtonStyle.secondary,
                on_click = self.on_back_click
            )
            back_btn.is_back = True
            self.add_item(back_btn)

    async def on_select(self, interaction: Interaction, values: list[str]):
        selected_value = values[0]
        cog_info = self.cogs_dict.get(selected_value)

        select_menu: BaseSelect = self.children[0]
        for opt in select_menu.options:
            opt.default = (opt.value == selected_value)

        self._add_back_button()

        if cog_info:
            embed = cog_help_embed(
                cog_info,
                self.lang,
                **self.bot_info
            )
        else:
            return

        await interaction.response.edit_message(
            embed = embed,
            view = self,
        )

    async def on_back_click(self, interaction: Interaction):
        select_menu: BaseSelect = self.children[0]
        for opt in select_menu.options:
            opt.default = False
        
        for child in self.children:
            if isinstance(child, BaseButton) and getattr(child, "is_back", False):
                self.remove_item(child)
                break

        embed = general_help_embed(
            self.lang,
            self.bot_info["bot_name"],
            self.bot_info["bot_avatar_url"],
            self.bot_info["owner_name"],
            self.bot_info["owner_avatar_url"],
            self.bot_info["version"],
            self.bot_info["slash_cmds_cache"].get('help', 0),
            self.cogs_dict
        )

        await interaction.response.edit_message(
            embed = embed,
            view = self
        )
