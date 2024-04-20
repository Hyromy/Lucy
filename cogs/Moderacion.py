import discord
from discord.ext import commands
import json

class Moderacion(commands.Cog):
    def __init__(self, Lucy):
        self.Lucy = Lucy
        Moderacion.__doc__="Moderación y control"

    @commands.hybrid_command(name="clear", description="Borra una cantidad especifica de mensajes en el canal")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx:commands.Context, cantidad:int):
        target = cantidad
        await ctx.channel.purge(limit = cantidad)
        await ctx.send(f"{target} mensajes eliminados")
    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Gestionar Mensajes` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `clear <cantidad>`\n`<argumento>` Obligatorio")

    @commands.hybrid_command(name="kick", description="Expulsa a un miembro del servidor")
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, usuario:discord.Member, motivo=None):
        await ctx.guild.kick(usuario)
        await ctx.send(f"<@{usuario.id}> Fue explulsado")
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Expulsar Miembros` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `kick @<miembro> (motivo)`\n`<argumento>` Obligatorio\n`(argumento)` Opcional")

    @commands.hybrid_command(name="ban", description="Banea a un miembro del servidor (Opcionalmente se puede dar un motivo)")
    async def ban(self, ctx, usuario:discord.Member, motivo=None):
        await ctx.guild.ban(usuario)
        await ctx.send(f"<@{usuario.id}> Fue baneado")
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Banear Miembros` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `ban @<miembro> (motivo)`\n`<argumento>` Obligatorio\n`(argumento)` Opcional")

    @commands.hybrid_command(name="unban", description="Retira el baneo de un usuario en el servidor")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, id_usuario):
        user = discord.Object(id=id_usuario)
        await ctx.guild.unban(user)
        await ctx.send(f"<@{id_usuario}> ya no esta baneado")
    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Banear Miembros` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `unban <id_miembro>`\n`<argumento>` Obligatorio")

    @commands.hybrid_command(name="setmute", description="Establece un rol (debe configurarse) que se usara para mutear a un miembro")
    @commands.has_permissions(administrator=True)
    async def setmute(self, ctx, rol:discord.Role):
        path = "json/mute_rol.json"
        with open(f"./{path}", "r") as f:
            mute_role = json.load(f)

        mute_role[str(ctx.guild.id)] = rol.name

        with open(f"./{path}", "w") as f:
            mute_role = json.dump(mute_role, f, indent = 4)

        await ctx.send(f"Rol de muteo establecido para {rol.mention}")
    @setmute.error
    async def setmute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `setmuterole @<rol>`\n`<argumento>` Obligatorio")

    @commands.hybrid_command(name = "muterole", description = "Muestra el rol de mute establecido del servidor")
    @commands.has_permissions(administrator=True)
    async def muterole(self, ctx:commands.Context):
        path = "json/mute_rol.json"
        with open (f"./{path}", "r") as f:
            data = json.load(f)

        rol_name = data.get(str(ctx.guild.id))
        if rol_name is None:
            await ctx.send("Aun no hay un rol de mute configurado.\nConfigura uno con `setmute <rol>`")
        else:
            rol = discord.utils.get(ctx.guild.roles, name = rol_name)
            await ctx.send(f"El rol mute es {rol.mention}")
    @muterole.error
    async def muterole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

    @commands.hybrid_command(name="removemute", description="Retira el rol asignado como mute")
    @commands.has_permissions(administrator=True)
    async def removemute(self, ctx):
        path = "json/mute_rol.json"
        with open(f"./{path}", "r") as f:
            mute_role = json.load(f)

        try:
            mute_role.pop(str(ctx.guild.id))
        except KeyError:
            await ctx.send("No hay ningun rol para eliminar")
            return

        with open(f"./{path}", "w") as f:
            mute_role = json.dump(mute_role, f, indent = 4)

        await ctx.send(f"Rol de muteo eliminado")
    @removemute.error
    async def removemute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

    @commands.hybrid_command(name="mute", description="Mutea a un miembro del servidor (requiere un rol establecido para ello)")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, usuario:discord.Member):
        path = "json/mute_rol.json"
        with open(f"./{path}", "r") as f:
            mute_roles = json.load(f)

        try:
            mute = discord.utils.get(ctx.guild.roles, name = mute_roles[str(ctx.guild.id)])
            await usuario.add_roles(mute, reason = None, atomic = True)
            await ctx.send(f"{usuario.mention} fue muteado.")
        
        except KeyError:
            await ctx.send("No hay un rol configurado.\nConfigura uno con `setmute @<rol>`")
        
        except discord.Forbidden:
            await ctx.send(f"No fue posible mutear a {usuario.mention}\nAsegurate que mi rol este por encima de {mute.mention}.")
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Gestionar Roles` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `mute @<miembro>`\n`<argumento>` Obligatorio")

    @commands.hybrid_command(name="unmute", description="Retira el mute de un miembro en el servidor")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, usuario:discord.Member):
        path = "json/mute_rol.json"
        with open(f"./{path}", "r") as f:
            mute_roles = json.load(f)

        try:
            mute = discord.utils.get(ctx.guild.roles, name = mute_roles[str(ctx.guild.id)])
            await usuario.remove_roles(mute, reason = None, atomic = True)
            await ctx.send(f"{usuario.mention} ya no esta muteado.")
        
        except KeyError:
            await ctx.send("No hay un rol configurado.\nConfigura uno con `setmuterole @<rol>`")
        
        except discord.Forbidden:
            await ctx.send(f"No pude quitar el mute a {usuario.mention}\nAsegurate que mi rol este por encima de {mute.mention}.")
    @unmute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Gestionar Roles` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `unmute @<miembro>`\n`<argumento>` Obligatorio")

async def setup(Lucy):
    await Lucy.add_cog(Moderacion(Lucy))