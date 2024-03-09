import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Select
import json, random, numexpr
from numpy import *
from data.config import *

class HelpSelect(Select):
    def __init__(self, Layla:commands.Bot):
        super().__init__(
            placeholder = "Escoje una categoria",
            options = [
                discord.SelectOption(
                    label = cog_name, description = cog.__doc__
                ) for cog_name, cog in Layla.cogs.items() if cog.__cog_commands__ and cog_name not in ["Jishaku"]
            ]
        )

        self.Layla = Layla

    async def callback(self, interaction: discord.Interaction) -> None:
        cog = self.Layla.get_cog(self.values[0])
        assert cog

        commands_mixer = []
        for i in cog.walk_commands():
            commands_mixer.append(i)

        for i in cog.walk_app_commands():
            commands_mixer.append(i)

        embed = discord.Embed(
            color = 0x00bbff,
            title = f"{cog.__cog_name__}",
            description = "\n".join(
                f"**{command.name}**: {command.description}"
                for command in commands_mixer
            )
        )

        await interaction.response.send_message(
            embed = embed,
            ephemeral = True
        )

class BugReport(discord.ui.Modal, title = "Reportar bug"):
    titulo = discord.ui.TextInput(label = "Titulo", placeholder = "Asunto del reporte",required = True, max_length = 50, style = discord.TextStyle.short)
    descripcion = discord.ui.TextInput(label = "Descripción", placeholder = "Describe lo ocurrido (en la medida de lo posible da detalles)", required = True, max_length = 1000, style = discord.TextStyle.paragraph)

    async def on_submit(self:commands.Bot, interaction:discord.Interaction):
        channel_bug = interaction.guild.get_channel(BUG_CHANNEL)
        
        embed = discord.Embed(title = self.titulo, color = 0x00bbff)
        embed.add_field(name = "Descripción del bug", value = self.descripcion)
        embed.set_footer(text = f"Reportado por {interaction.user.name}", icon_url = interaction.user.avatar)
        await channel_bug.send(embed = embed)

        await interaction.response.send_message(f"{interaction.user.mention} Gracias por reportar el bug. Este será corregido en futuras versiones", ephemeral = True)

class Comandos(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla
        Comandos.__doc__ = "Comandos varios"

    @commands.hybrid_command(name="help", aliases=["h", "H"],description="Muestra la lista de comandos disponibles")
    async def help(self, ctx):
        embed = discord.Embed(title="Help", color=0x00bbff)
        for cog_name, cog in self.Layla.cogs.items():
            if len(cog.get_commands()) >= 1:
                embed.add_field(name = cog_name, value = cog.__doc__, inline = False)
        embed.set_footer(text = f"{self.Layla.user.name} {VERSION}", icon_url = self.Layla.user.avatar)

        view = View().add_item(HelpSelect(self.Layla))
        await ctx.send(embed = embed, view = view)

    @commands.hybrid_command(name="ping", description="Mide la latencia del bot en milisegundos")
    async def ping(self, ctx):
        lat = round(self.Layla.latency * 1000)
        await ctx.send(f"Pong! {lat}ms")

    @commands.hybrid_command(name="echo", description="Repite lo que digas")
    async def echo(self, ctx, *, mensaje):
        await ctx.send(mensaje)

    @commands.hybrid_command(name="8ball", aliases=["8", "ball"], description="Haz una pregunta y será respondida")
    async def ball(self, ctx, *, pregunta):
        with open("./data/ball.txt", "r", encoding="utf-8") as f:
            respuestas = f.readlines()
            respuesta = random.choice(respuestas)
            
        await ctx.send(respuesta)
    @ball.error
    async def ball_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Comando invalido, requiere argumentos adicionales. `ball <pregunta>`\n`<argumento>` Obligatorio")
 
    @commands.command(name="tell", description="Envia un mensaje secreto a un destinatario especificado")
    async def tell(self, ctx, usuario:discord.Member, *, mensaje):
        embed = discord.Embed(title = None, description = mensaje, color = 0x00bbff)

        author = f"{ctx.author.display_name} te ha dicho:"
        usuario_url = f"https://discord.com/users/{ctx.author.id}"
        embed.set_author(name = author, url = usuario_url, icon_url = ctx.author.avatar)
        embed.set_footer(text = f"Versión: {VERSION}")

        await ctx.message.delete()
        await usuario.send(embed = embed)
    @tell.error
    async def tell_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.delete()
            await ctx.author.send("Comando invalido, requiere argumentos adicionales. `tell @<miembro> <mensaje>`\n`<argumento>` Obligatorio")

    @commands.hybrid_command(name="avatar", description="Envia el avatar de un usuario (en caso de no especificar el usuario devolverá tu avatar)")
    async def avatar(self, ctx, usuario:discord.Member=None):
        if usuario is None:
            usuario = ctx.author

        embed = discord.Embed(title=f"Avatar de {usuario.display_name}", color = 0x00bbff)
        embed.set_image(url=usuario.avatar.url)
        embed.set_footer(text=f"Pedido por {ctx.author.name}", icon_url=ctx.author.avatar)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="userinfo", description="Información detallada de usuario")
    async def userinfo(self, ctx, usuario:discord.Member=None):
        if usuario is None:
            usuario = ctx.author

        if usuario.status == discord.Status.online:
            status = "Conectado"
        elif usuario.status == discord.Status.idle:
            status = "Ausente"
        elif usuario.status == discord.Status.dnd:
            status = "No molestar"
        else:
            status = "Desconectado"

        creado = usuario.created_at.strftime("%d/%m/%Y")
        unido = usuario.joined_at.strftime("%d/%m/%Y")

        embed = discord.Embed(title = f"Información de {usuario.name}", color = 0x00bbff)
        embed.set_thumbnail(url = usuario.avatar)
        embed.add_field(name="", value=f"**Nombre**: {usuario.name}", inline=False)
        embed.add_field(name="", value=f"**Nickname**: {usuario.display_name}", inline=False)
        embed.add_field(name="", value=f"**Discriminador**: {usuario.discriminator}", inline=False)
        embed.add_field(name="", value=f"**ID**: {usuario.id}", inline=False)
        embed.add_field(name="", value=f"**Estado**: {str(status)}", inline=False)
        embed.add_field(name="", value=f"**Fecha de creación**: {creado}", inline=False)
        embed.add_field(name="", value=f"**Se unió en**: {unido}", inline=False)
        embed.set_footer(text=f"Pedido por {ctx.author.display_name}", icon_url=ctx.author.avatar)
        
        await ctx.send(embed = embed)

    @commands.hybrid_command(name="serverinfo", description="Información detallada del servidor")
    async def serverinfo(self, ctx:commands.Context):        
        creado = ctx.guild.created_at.strftime("%d/%m/%Y")
        
        embed = discord.Embed(title = f"Informacion de {ctx.guild.name}", color = 0x00bbff)
        
        try:
            embed.set_thumbnail(url = ctx.guild.icon.url)
        except Exception:
            pass
        embed.add_field(name="", value=f"**ID**: {ctx.guild.id}", inline=False)
        embed.add_field(name="", value=f"**Propietario**: {ctx.guild.owner.name}", inline=False)
        embed.add_field(name="", value=f"**Miembros**: {len(ctx.guild.members)}", inline=False)
        embed.add_field(name="", value=f"**Región**: {ctx.guild.preferred_locale}", inline=False)
        embed.add_field(name="", value=f"**Roles**: {len(ctx.guild.roles)}", inline=False)
        embed.add_field(name="", value=f"**Canales de Texto**: {len(ctx.guild.text_channels)}", inline=False)
        embed.add_field(name="", value=f"**Canales de voz**: {len(ctx.guild.voice_channels)}", inline=False)
        embed.add_field(name="", value=f"**Fecha de creación**: {creado}", inline=False)
        embed.set_footer(text=f"Pedido por {ctx.author.display_name}", icon_url=ctx.author.avatar)

        await ctx.send(embed = embed)

    @commands.hybrid_command(name="level", aliases=["lv"], description="Consulta el nivel de un usuario (en caso de no especificar el usuario devolverá tu nivel)")
    async def level(self, ctx, usuario:discord.Member = None):        
        if usuario is None:
            usuario = ctx.author
        
        with open("./json/user.json", "r") as f:
            users = json.load(f)

        try:
            level = users[f"{usuario.id}"]["Lvl"]
            exp = users[f"{usuario.id}"]["Exp"]

            await ctx.send(f"{usuario.mention} Nv.{level}\n{exp} / {NEXT_LEVEL(level)}exp.")
        except KeyError:
            await ctx.send(f"No tengo registros de **{usuario.display_name}**")

    @commands.command(name = "calculate", aliases = ["calc", "math"], description = "Resuelve una expresion algebráica")
    async def calculate(self, ctx, *, expresion):
        try:
            respuesta = numexpr.evaluate(expresion)
            await ctx.send(f"{expresion} = {respuesta}")
        except:
            await ctx.send("Expresión no valida")

    @app_commands.command(name = "bug", description = "Reportar un bug o inconsistencia del bot")
    async def bug(self, interaction:discord.Interaction):
        if (interaction.guild_id != HOME):
            await interaction.response.send_message(content = f"Desafortunadamente, solo se pueden reportar bugs desde el servidor donde fui creada. Por favor, dirígete al servidor de desarrollo o contacta con <@608870766586494976> para reportar el bug. Disculpa las molestias." +
                                                    "https://discord.gg/85hexN9TyM",
                                                    ephemeral = True)
        else:
            await interaction.response.send_modal(BugReport())

    @commands.command(name="current", description="Tarea de desarrollo en proceso")
    async def current(self, ctx):
        await ctx.send("**Tarea actual**\nReestructurar")

async def setup(Layla):
    await Layla.add_cog(Comandos(Layla))