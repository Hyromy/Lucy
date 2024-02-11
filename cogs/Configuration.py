import discord
from discord.ext import commands
import json

class Configuration(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla

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

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def setprefix(self, ctx, new_prefix:str):
        """Establece un prefijo para el servidor"""

        with open("./json/prefixes.json", "r") as f:
            prefix = json.load(f)

        prefix[str(ctx.guild.id)] = new_prefix

        with open("./json/prefixes.json", "w") as f:
            json.dump(prefix, f, indent = 4)

        await ctx.send(f"Prefijo cambiado a {new_prefix}")  
    @setprefix.error
    async def prefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `setprefix <prefijo>`\n`<argumento>` Obligatorio")

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def setlog(self, ctx, set_log:int):
        """Establece un canal de depuracion para el bot"""

        with open("./json/log_channels.json", "r") as f:
            log = json.load(f)
        
        log[str(ctx.guild.id)] = set_log

        with open("./json/log_channels.json", "w") as f:
            json.dump(log, f, indent = 4)

        await ctx.send(f"Canal de depuración establecido a <#{set_log}>")
        await ctx.send(f"{log[str(ctx.guil.id)]}: {log[str(ctx.channel.id)]}")
    @setlog.error
    async def log_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `setlog <id_canal>`\n`<argumento>` Obligatorio")

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def removelog(self, ctx):
        """Retira el canal de depuracion para el bot"""

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

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def logtest(self, ctx, *, message):
        """Envia un mensaje de prueba al canal de depuración establecido"""

        with open("./json/log_channels.json", "r") as f:
            log = json.load(f)

        channel_id = log.get(str(ctx.guild.id))
        if channel_id is None:
            await ctx.send(f"Aun no hay un canal de depuración configurado.\nConfigura uno con `log <id canal>`")
            return
        
        channel_out = self.Layla.get_channel(channel_id)
        await channel_out.send(message)
    @logtest.error
    async def logtest_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Necesitas permisos de `Administrador` para hacer eso.")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `setlog <id_canal>`\n`<argumento>` Obligatorio")

async def setup(Layla):
    await Layla.add_cog(Configuration(Layla))