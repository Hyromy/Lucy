import discord

from discord.ext import commands

class Mod(commands.Cog):
    def __init__(self, Lucy:commands.Bot):
        self.Lucy = Lucy
        self.description = "Comandos de moderación"
        self.emoji = "🛠️"

    async def generic_error(self, ctx:commands.Context, error:commands.CommandError, *, title:str = None, description:str = None):
        embed = discord.Embed(color = 0x00bbff)
        embed.title = title or "Error"
        embed.description = description or "Ocurrió un error al ejecutar el comando"
        if not (title and description):
            embed.add_field(name = error.__class__.__name__, value = error)
        
        await ctx.reply(
            embed = embed,
            ephemeral = True
        )

    @commands.hybrid_command(
        name = "purge",
        help = "Elimina mensajes del chat",
        aliases = ["clear", "cls"],
        usage = "clear <cantidad>"
    )
    @commands.has_permissions(
        manage_messages = True
    )
    async def clear(self, ctx:commands.Context, cantidad:int):
        if cantidad < 1:
            await ctx.reply(
                content = "La cantidad de mensajes a eliminar debe ser mayor a 0",
                ephemeral = True)
            return

        await ctx.channel.purge(
            limit = cantidad + 1,
            bulk = True
        )

    @clear.error
    async def clear_error(self, ctx:commands.Context, error:commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await self.generic_error(ctx, error,
                title = "Permisos insuficientes",
                description = "No tienes permisos para eliminar mensajes"
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await self.generic_error(ctx, error,
                title = "Argumentos faltantes",
                description = "Debes especificar la cantidad de mensajes a eliminar"
            )
        elif isinstance(error, commands.BadArgument):
            await self.generic_error(ctx, error,
                title = "Argumento inválido",
                description = "La cantidad de mensajes a eliminar debe ser un número"
            )
        else:
            await self.generic_error(ctx, error)

    @commands.hybrid_command(
        name = "kick",
        help = "Expulsa a un usuario del servidor",
        usage = "kick <usuario> [razón]"
    )
    @commands.has_permissions(
        kick_members = True
    )
    async def kick(self, ctx:commands.Context, usuario:discord.Member, *, reason:str = None):
        if usuario == ctx.author:
            await ctx.reply(
                content = "No puedes expulsarte a ti mismo",
                ephemeral = True
            )
            return

        if usuario == self.Lucy.user:
            await ctx.reply(
                content = "No puedo expulsarme a mí misma",
                ephemeral = True
            )
            return

        if usuario.top_role >= ctx.author.top_role:
            await ctx.reply(
                content = "No puedes expulsar a alguien con un rol igual o superior al tuyo",
                ephemeral = True
            )
            return

        await usuario.kick(reason = reason)
        embed = discord.Embed(
            title = f"Expulsión de {usuario}",
            description = f"Razón: {usuario}",
            color = 0x00bbff
        )
        await ctx.reply(embed = embed)

    @kick.error
    async def kick_error(self, ctx:commands.Context, error:commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await self.generic_error(ctx, error,
                title = "Permisos insuficientes",
                description = "No tienes permisos para expulsar a usuarios"
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await self.generic_error(ctx, error,
                title = "Argumentos faltantes",
                description = "Debes mencionar al usuario a expulsar"
            )
        elif isinstance(error, commands.BadArgument):
            await self.generic_error(ctx, error,
                title = "Argumento inválido",
                description = "El usuario a expulsar debe ser una mención"
            )
        else:
            await self.generic_error(ctx, error)

    @commands.hybrid_command(
        name = "ban",
        help = "Banea a un usuario del servidor",
        usage = "ban <usuario> [razón]"
    )
    @commands.has_permissions(
        ban_members = True
    )
    async def ban(self, ctx:commands.Context, usuario:discord.Member, *, reason:str = None):
        if usuario == ctx.author:
            await ctx.reply(
                content = "No puedes banearte a ti mismo",
                ephemeral = True
            )
            return

        if usuario == self.Lucy.user:
            await ctx.reply(
                content = "No puedo banearme a mí misma",
                ephemeral = True
            )
            return

        if usuario.top_role >= ctx.author.top_role:
            await ctx.reply(
                content = "No puedes banear a alguien con un rol igual o superior al tuyo",
                ephemeral = True
            )
            return

        await usuario.ban(reason = reason)
        embed = discord.Embed(
            title = f"Baneo de {usuario}",
            description = f"Razón: {usuario}",
            color = 0x00bbff
        )
        await ctx.reply(embed = embed)

    @ban.error
    async def ban_error(self, ctx:commands.Context, error:commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await self.generic_error(ctx, error,
                title = "Permisos insuficientes",
                description = "No tienes permisos para banear a usuarios"
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await self.generic_error(ctx, error,
                title = "Argumentos faltantes",
                description = "Debes mencionar al usuario a banear"
            )
        elif isinstance(error, commands.BadArgument):
            await self.generic_error(ctx, error,
                title = "Argumento inválido",
                description = "El usuario a banear debe ser una mención"
            )
        else:
            await self.generic_error(ctx, error)

async def setup(Lucy:commands.Bot):
    await Lucy.add_cog(Mod(Lucy))