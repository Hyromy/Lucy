import discord
from discord.ext import commands
import json

class Configuration(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla
        Configuration.__doc__="Configuración del bot"

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open("./json/prefixes.json", "r") as f:
            prefix = json.load(f)

        prefix[str(guild.id)] = ","

        with open("./json/prefixes.json", "w") as f:
            json.dump(prefix, f, indent = 4)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open("./json/prefixes.json", "r") as f:
            prefix = json.load(f)

        prefix.pop(str(guild.id))

        with open("./json/prefixes.json", "w") as f:
            json.dump(prefix, f, indent = 4)

    @commands.hybrid_command(name="setprefix", description="Establece un prefijo para el servidor")
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, prefijo:str):
        with open("./json/prefixes.json", "r") as f:
            prefix = json.load(f)

        prefix[str(ctx.guild.id)] = prefijo

        with open("./json/prefixes.json", "w") as f:
            json.dump(prefix, f, indent = 4)

        await ctx.send(f"Prefijo cambiado a {prefijo}")  
    @setprefix.error
    async def prefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `setprefix <prefijo>`\n`<argumento>` Obligatorio")

    @commands.hybrid_command(name="setlog", description="Establece un canal de depuracion para el bot")
    @commands.has_permissions(administrator=True)
    async def setlog(self, ctx, id_canal:int):
        with open("./json/log_channels.json", "r") as f:
            log = json.load(f)
        
        log[str(ctx.guild.id)] = id_canal

        with open("./json/log_channels.json", "w") as f:
            json.dump(log, f, indent = 4)

        await ctx.send(f"Canal de depuración establecido a <#{id_canal}>")
        await ctx.send(f"{log[str(ctx.guil.id)]}: {log[str(ctx.channel.id)]}")
    @setlog.error
    async def log_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `setlog <id_canal>`\n`<argumento>` Obligatorio")

    @commands.hybrid_command(name="removelog", description="Retira el canal de depuracion para el bot")
    @commands.has_permissions(administrator=True)
    async def removelog(self, ctx):
        with open("./json/log_channels.json", "r") as f:
            log = json.load(f)

        try:
            log.pop(str(ctx.guild.id))
        except KeyError:
            await ctx.send("No hay ningun canal de depuración por eliminar")
            return

        with open("./json/log_channels.json", "w") as f:
            json.dump(log, f, indent = 4)

        await ctx.send("Canal de depuración eliminado")
    @removelog.error
    async def logremove_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

    @commands.hybrid_command(name="msglog", description="Envia un mensaje de prueba al canal de depuración establecido")
    @commands.has_permissions(administrator=True)
    async def msglog(self, ctx, *, mensaje):
        with open("./json/log_channels.json", "r") as f:
            log = json.load(f)

        channel_id = log.get(str(ctx.guild.id))
        if channel_id is None:
            await ctx.send(f"Aun no hay un canal de depuración configurado.\nConfigura uno con `log <id canal>`")
            return
        
        channel_out = self.Layla.get_channel(channel_id)
        await channel_out.send(mensaje)
    @msglog.error
    async def msglog_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `setlog <id_canal>`\n`<argumento>` Obligatorio")

async def setup(Layla):
    await Layla.add_cog(Configuration(Layla))