import discord, json
from discord.ext import commands

class Configuracion(commands.Cog):
    def __init__(self, Lucy):
        self.Lucy = Lucy
        Configuracion.__doc__="Configuración del bot"

    @commands.hybrid_command(name="setprefix", description="Establece un prefijo para el servidor")
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, prefijo:str):
        path = "json/prefix.json"
        with open(f"./{path}", "r") as f:
            data = json.load(f)

        data[str(ctx.guild.id)] = prefijo

        with open(f"./{path}", "w") as f:
            json.dump(data, f, indent = 4)

        await ctx.send(f"Prefijo cambiado a `{prefijo}`")  
    @setprefix.error
    async def prefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `setprefix <prefijo>`\n`<argumento>` Obligatorio")

    @commands.hybrid_command(name="setlog", description="Establece un canal de depuracion para el bot")
    @commands.has_permissions(administrator=True)
    async def setlog(self, ctx, canal:discord.TextChannel):
        path = "json/log_channel.json"
        with open(f"./{path}", "r") as f:
            data = json.load(f)
        
        data[str(ctx.guild.id)] = canal.id

        with open(f"./{path}", "w") as f:
            json.dump(data, f, indent = 4)

        await ctx.send(f"Canal de depuración establecido a {canal.mention}")
    @setlog.error
    async def log_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `setlog <id_canal>`\n`<argumento>` Obligatorio")

    @commands.hybrid_command(name="removelog", description="Retira el canal de depuracion para el bot")
    @commands.has_permissions(administrator=True)
    async def removelog(self, ctx):
        path = "json/log_channel.json"
        with open(f"./{path}", "r") as f:
            log = json.load(f)

        try:
            log.pop(str(ctx.guild.id))
        except KeyError:
            await ctx.send("No hay ningun canal de depuración por eliminar")
            return

        with open(f"./{path}", "w") as f:
            json.dump(log, f, indent = 4)

        await ctx.send("Canal de depuración eliminado")
    @removelog.error
    async def logremove_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

    @commands.hybrid_command(name = "log", description = "Muestra el canal de depuración establecido en el servidor")
    @commands.has_permissions(administrator=True)
    async def log(self, ctx):
        path = "json/log_channel.json"
        with open(f"./{path}", "r") as f:
            log = json.load(f)

        channel_id = log.get(str(ctx.guild.id))
        if channel_id is None:
            await ctx.send("Aun no hay un canal de depuración configurado.")
        else:
            await ctx.send(f"El canal de depuración es <#{channel_id}>")
    @log.error
    async def log_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

    @commands.hybrid_command(name="msglog", description="Envia un mensaje de prueba al canal de depuración establecido")
    @commands.has_permissions(administrator=True)
    async def msglog(self, ctx, *, mensaje):
        path = "json/log_channel.json"
        with open(f"./{path}", "r") as f:
            log = json.load(f)

        channel_id = log.get(str(ctx.guild.id))
        if channel_id is None:
            await ctx.send(f"Aun no hay un canal de depuración configurado.")
            return
        
        channel_out = self.Lucy.get_channel(channel_id)
        await channel_out.send(mensaje)
    @msglog.error
    async def msglog_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `setlog <id_canal>`\n`<argumento>` Obligatorio")

async def setup(Lucy):
    await Lucy.add_cog(Configuracion(Lucy))