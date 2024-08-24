import discord
import os

from discord.ext import commands

from common.activies import get_prefix

class Info(commands.Cog):
    def __init__(self, Lucy:commands.Bot):
        self.Lucy = Lucy
        self.description = "Información y utilidades"
        self.emoji = "💡"

    def cogs_to_dict(self, include_events = False) -> dict[str, list[str]]:
        cogs_dict = {}
        for cog_name, cog in self.Lucy.cogs.items():
            cmds = cog.get_commands()
            if not include_events and cmds == []:
                continue

            cmds.sort(key = lambda x:x.name)
            cogs_dict[cog_name] = [cmd.name for cmd in cmds]

        return cogs_dict

    async def send_help(self, is_admin = False) -> discord.Embed:
        embed = discord.Embed(
            title = f"Comandos de {self.Lucy.user.name}",
            description = f"Estos son los comandos que puedes usar con {self.Lucy.user.name}",
            color = 0x00bbff
        )
        embed.set_thumbnail(url = self.Lucy.user.avatar)

        for cog in self.Lucy.cogs.values():
            if cog.get_commands():
                is_admin_cog = hasattr(cog, "admin")
                if ((not is_admin and is_admin_cog) ^
                    (is_admin and not is_admin_cog)
                ):
                    continue

                emoji = f"{cog.emoji} " if hasattr(cog, "emoji") else ""
                embed.add_field(
                    name = f"{emoji}{cog.qualified_name}",
                    value = cog.description or "",
                    inline = False
                )
            
        return embed

    async def send_help_cog(self, cog_name:str, ctx:commands.Context) -> discord.Embed | None:
        cog = self.Lucy.get_cog(cog_name)
        is_admin = ctx.author.id == int(os.getenv("OWNER_ID"))
        is_admin_cog = hasattr(cog, "admin")
        if not is_admin and is_admin_cog:
            return None

        embed = discord.Embed(
            title = f"Categoría: {cog.qualified_name}",
            description = cog.description,
            color = 0x00bbff
        )

        cmds = cog.get_commands()
        for cmd in sorted(cmds, key = lambda x:x.name):
            embed.add_field(
                name = cmd.name,
                value = ""
            )

        return embed

    async def send_help_command(self, cmd:str, ctx:commands.Context) -> discord.Embed:
        command = self.Lucy.get_command(cmd)
        cog = self.Lucy.get_cog(command.cog_name)
        is_admin = ctx.author.id == int(os.getenv("OWNER_ID"))
        is_admin_cog = hasattr(cog, "admin")
        if not is_admin and is_admin_cog:
            return None

        embed = discord.Embed(
            title = f"{command.cog_name}: {command.name}",
            description = command.help,
            color = 0x00bbff
        )
        if command.aliases:
            embed.add_field(
                name = "Alias",
                value = ", ".join(command.aliases),
                inline = False
            )
        embed.add_field(
            name = "Ejemplo de uso",
            value = f"`{get_prefix(self.Lucy, ctx.message)}{command.usage}`",
            inline = False
        )

        permissions = command.checks
        if permissions != []:
            for check in permissions:    
                if hasattr(check, '__name__') and check.__name__ == 'predicate':
                    perms = check.__closure__[0].cell_contents
                    if isinstance(perms, dict):
                        required_permissions = perms.keys()

            embed.add_field(name = "Permisos requeridos", value = "\n".join(sorted(required_permissions)))

        embed.set_footer(text = "Parametros: <Requerido>, [Opcional]")

        return embed

    @commands.hybrid_command(
        name = "help",
        help = "Muestra los comandos disponibles",
        aliases = ["h"],
        usage = "help [categoría | comando]",
    )
    async def help(self, ctx:commands.Context, argumento:str = None):
        if not argumento:
            await ctx.reply(embed = await self.send_help())
            return
        
        elif argumento.casefold() == "admin":
            if ctx.author.id == int(os.getenv("OWNER_ID")):
                await ctx.reply(embed = await self.send_help(is_admin = True))
            return
                
        for cog, cmds in self.cogs_to_dict().items():
            if cog.casefold() == argumento.casefold():
                await ctx.reply(embed = await self.send_help_cog(cog, ctx))
                return

            else:
                for cmd in cmds:
                    if cmd.casefold() == argumento.casefold():
                        await ctx.reply(embed = await self.send_help_command(cmd, ctx))
                        return
        
        await ctx.message.add_reaction("❌")

    @commands.hybrid_command(
        name = "serverinfo",
        help = "Muestra información del servidor",
        aliases = ["server", "guildinfo", "guild"],
        usage = "serverinfo"
    )
    async def serverinfo(self, ctx:commands.Context):
        embed = discord.Embed(
            title = f"Información de: {ctx.guild.name}",
            description = ctx.guild.description or "",
            color = 0x00bbff
        )
        embed.set_thumbnail(url = ctx.guild.icon.url or None)
        if ctx.guild.banner:
            embed.set_image(url = ctx.guild.banner.url)
        
        embed.add_field(name = "ID", value = ctx.guild.id)
        embed.add_field(name = "Dueño", value = ctx.guild.owner.mention)
        embed.add_field(name = "Miembros", value = ctx.guild.member_count)
        embed.add_field(name = "Roles", value = len(ctx.guild.roles))
        embed.add_field(name = "Categorías", value = len(ctx.guild.categories))
        embed.add_field(name = "Canales de texto", value = len(ctx.guild.text_channels))
        embed.add_field(name = "Canales de voz", value = len(ctx.guild.voice_channels))
        embed.add_field(name = "Emojis", value = len(ctx.guild.emojis))
        embed.add_field(name = "Stickers", value = len(ctx.guild.stickers))
        
        total_days = (ctx.message.created_at - ctx.guild.created_at).days
        years = total_days // 365
        months = (total_days % 365) // 30
        days = (total_days % 365) % 30
        embed.add_field(name = "Fecha de creación", value = ctx.guild.created_at.strftime("%Y/%m/%d %H:%M:%S"))
        embed.add_field(name = "Días del servidor", value = f"{total_days} *(A:{years} M:{months} D:{days})*")

        await ctx.reply(embed = embed)

    @commands.hybrid_command(
        name = "userinfo",
        help = "Muestra información de un usuario",
        aliases = ["user", "memberinfo", "member"],
        usage = "userinfo [@usuario]"
    )
    async def userinfo(self, ctx:commands.Context, usuario:discord.Member = None):
        usuario = usuario or ctx.author
        embed = discord.Embed(
            title = f"Información de: {usuario.display_name}",
            color = 0x00bbff
        )
        embed.set_thumbnail(url = usuario.avatar.url if usuario.avatar else usuario.default_avatar.url)

        embed.add_field(name = "ID", value = usuario.id)
        embed.add_field(name = "Nombre", value = usuario.name)
        if int(usuario.discriminator) != 0:
            embed.add_field(name = "Discriminador", value = f"#{usuario.discriminator}")        

        total_days = (ctx.message.created_at - usuario.created_at).days
        years = total_days // 365
        months = (total_days % 365) // 30
        days = (total_days % 365) % 30
        embed.add_field(name = "Fecha de creación", value = usuario.created_at.strftime("%Y/%m/%d %H:%M:%S"))
        embed.add_field(name = "Fecha de ingreso", value = usuario.joined_at.strftime("%Y/%m/%d %H:%M:%S"))
        embed.add_field(name = "Días en el servidor", value = f"{total_days} *(A:{years} M:{months} D:{days})*")
            
        if usuario.premium_since:
            boost_total_days = (ctx.message.created_at - usuario.premium_since).days
            boost_years = boost_total_days // 365
            boost_months = (boost_total_days % 365) // 30
            boost_days = (boost_total_days % 365) % 30
            embed.add_field(name = "Boost", value = usuario.premium_since.strftime("%Y/%m/%d %H:%M:%S"))
            embed.add_field(name = "Días de boost", value = f"{boost_total_days} *(A:{boost_years} M:{boost_months} D:{boost_days})*")

        embed.add_field(name = "Roles", value = len(usuario.roles) - 1)

        embed.add_field(name = "Permisos", value = sum(perm[1] for perm in usuario.guild_permissions if perm[1]))
        
        await ctx.reply(embed = embed)

async def setup(Lucy:commands.Bot):
    await Lucy.add_cog(Info(Lucy))