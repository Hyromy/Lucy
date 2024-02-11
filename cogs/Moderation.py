import discord
from discord.ext import commands
import json

class Moderation(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla

    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx, amount:int):
        """Borra una cantidad especifica de mensajes en el canal"""

        await ctx.channel.purge(limit = amount)
        await ctx.send(f"{amount} mensajes eliminados")
    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Gestionar Mensajes` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `clear <cantidad>`\n`<argumento>` Obligatorio")

    @commands.command()
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member:discord.Member, reason = None):
        """Expulsa a un miembro del servidor"""

        await ctx.guild.kick(member)
        await ctx.send(f"<@{member.id}> Fue explulsado")
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Expulsar Miembros` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `kick @<miembro> (motivo)`\n`<argumento>` Obligatorio\n`(argumento)` Opcional")

    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, member:discord.Member, reason = None):
        """Banea a un miembro del servidor"""

        await ctx.guild.ban(member)
        await ctx.send(f"<@{member.id}> Fue baneado")
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Banear Miembros` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `ban @<miembro> (motivo)`\n`<argumento>` Obligatorio\n`(argumento)` Opcional")

    @commands.command(name = "unban")
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def unban(self, ctx, user_id):
        """Retira el baneo de un usuario en el servidor"""

        user = discord.Object(id = user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"<@{user_id}> ya no esta baneado")
    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Banear Miembros` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `unban <id_miembro>`\n`<argumento>` Obligatorio")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open("./json/mute_roles.json", "r") as f:
            mute_role = json.load(f)

        try:
            mute_role.pop(str(guild.id))
        except KeyError:
            return

        with open("./json/mute_roles.json", "w") as f:
            mute_role = json.dump(mute_role, f, indent = 4)

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def setmuterole(self, ctx, role:discord.Role):
        """Establece un rol que se usara para mutear a un miembro"""

        with open("./json/mute_roles.json", "r") as f:
            mute_role = json.load(f)

        mute_role[str(ctx.guild.id)] = role.name

        with open("./json/mute_roles.json", "w") as f:
            mute_role = json.dump(mute_role, f, indent = 4)

        await ctx.send(f"Rol de muteo establecido para {role.mention}")
    @setmuterole.error
    async def setmuterole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `setmuterole @<rol>`\n`<argumento>` Obligatorio")

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def removemuterole(self, ctx):
        """Retira el rol asignado como mute"""

        with open("./json/mute_roles.json", "r") as f:
            mute_role = json.load(f)

        try:
            mute_role.pop(str(ctx.guild.id))
        except KeyError:
            await ctx.send("No hay ningun rol para eliminar")
            return

        with open("./json/mute_roles.json", "w") as f:
            mute_role = json.dump(mute_role, f, indent = 4)

        await ctx.send(f"Rol de muteo eliminado")
    @removemuterole.error
    async def setmuterole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

    @commands.command()
    @commands.has_permissions(manage_roles = True)
    async def mute(self, ctx, member:discord.Member):
        """Mutea a un miembro del servidor"""

        with open("./json/mute_roles.json", "r") as f:
            mute_roles = json.load(f)

        try:
            mute = discord.utils.get(ctx.guild.roles, name = mute_roles[str(ctx.guild.id)])
            await member.add_roles(mute, reason = None, atomic = True)
            await ctx.send(f"{member.mention} fue muteado.")
        
        except KeyError:
            await ctx.send("No hay un rol configurado.\nConfigura uno con `setmuterole @<rol>`")
        
        except discord.Forbidden:
            await ctx.send(f"No fue posible mutear a {member.mention}\nAsegurate que mi rol este por encima de {mute.mention}.")
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Gestionar Roles` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `mute @<miembro>`\n`<argumento>` Obligatorio")

    @commands.command()
    @commands.has_permissions(manage_roles = True)
    async def unmute(self, ctx, member:discord.Member):
        """Retira el mute de un miembro en el servidor"""

        with open("./json/mute_roles.json", "r") as f:
            mute_roles = json.load(f)

        try:
            mute = discord.utils.get(ctx.guild.roles, name = mute_roles[str(ctx.guild.id)])
            await member.remove_roles(mute, reason = None, atomic = True)
            await ctx.send(f"{member.mention} ya no esta muteado.")
        
        except KeyError:
            await ctx.send("No hay un rol configurado.\nConfigura uno con `setmuterole @<rol>`")
        
        except discord.Forbidden:
            await ctx.send(f"No quitar el mute a {member.mention}\nAsegurate que mi rol este por encima de {mute.mention}.")
    @unmute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Gestionar Roles` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `unmute @<miembro>`\n`<argumento>` Obligatorio")

async def setup(Layla):
    await Layla.add_cog(Moderation(Layla))