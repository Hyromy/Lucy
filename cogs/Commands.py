import discord
from discord.ext import commands
import random, json
from data.config import VERSION, NEXT_LEVEL

class Commands(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla

    @commands.command()
    async def ping(self, ctx):
        """Mide la latencia del bot"""
        latencia = round(self.Layla.latency * 1000)
        await ctx.send(f"Pong! {latencia}ms")

    @commands.command(aliases = ["8", "8ball"])
    async def ball(self, ctx, *, question):
        """Haz una pregunta y sera respondida"""
        with open("./data/ball.txt", "r") as f:
            respuestas = f.readlines()
            respuesta = random.choice(respuestas)
            
        await ctx.send(respuesta)
    @ball.error
    async def ball_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `ball <pregunta>`\n`<argumento>` Obligatorio")

    @commands.command()
    async def tell(self, ctx, user:discord.Member, *, message):
        """Envia un mensaje secreto a un destinatario especificado"""
        embed = discord.Embed(title = None, description = message, color = 0x00bbff)

        author = f"{ctx.author.display_name} te ha dicho:"
        usuario_url = f"https://discord.com/users/{ctx.author.id}"
        embed.set_author(name = author, url = usuario_url, icon_url = ctx.author.avatar)
        embed.set_footer(text = f"Versión: {VERSION}")

        await ctx.message.delete()
        await user.send(embed = embed)
    @tell.error
    async def tell_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.delete()
            await ctx.author.send("Comando invalido, requiere argumentos adicionales. `tell @<miembro> <mensaje>`\n`<argumento>` Obligatorio")

    @commands.command()
    async def level(self, ctx, member:discord.Member = None):
        """Consulta tu nivel de usuario"""
        if member is None:
            member = ctx.author
        
        with open("./json/users.json", "r") as f:
            users_level = json.load(f)

        try:
            level = users_level[f"{member.id}"]["Lvl"]
            exp = users_level[f"{member.id}"]["Exp"]
            await ctx.send(f"{member.mention} Nv.{level}\n{exp} / {NEXT_LEVEL(level)}exp.")
        except KeyError:
            await ctx.send(f"No tengo registros de {member.mention}")

    @commands.command(aliases = ["h"])
    async def help(self, ctx, text:str = None):
        """Comando de informacion"""        
        categorias, comandos = 0, 0
        cog_name = []

        for cog in self.Layla.cogs.values():
            commands = cog.get_commands()
            if len(commands) == 0:
                continue
            cog_name.append(f"{cog.__class__.__name__}")
            categorias += 1
            comandos += len(commands)

        if text is None:
            embed = discord.Embed(color = 0x00bbff, title = f"{categorias} categorias disponibles con {comandos} comandos", description = "Escribe `help <categoria>`\npara conocer los comandos de esa categoria")
            embed.set_author(name = f"Commandos de {ctx.bot.user.name}", icon_url = ctx.bot.user.avatar)

            for i in cog_name:
                embed.add_field(name = i, value = "", inline = False)
        else:
            text = text.capitalize()
            if text not in cog_name:
                await ctx.send("Categoria no encontrada")
                return

            embed = discord.Embed(color = 0x00bbff, title = f"Commandos de {text}", description = "")
            embed.set_author(name = f"Commandos de {ctx.bot.user.name}", icon_url = ctx.bot.user.avatar)

            for cog in self.Layla.cogs.values():
                if cog.__class__.__name__ == text:
                    commands = cog.get_commands()
                    break
            for command in commands:
                embed.add_field(name=command.name, value=command.help, inline=False)

        await ctx.send(embed = embed)

async def setup(Layla):
    await Layla.add_cog(Commands(Layla))