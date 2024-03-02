import discord
from discord.ext import commands
import json
from data.config import VERSION, HOME

class Eventos(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla
        Eventos.__doc__="Escucha de eventos"

    @commands.Cog.listener()
    async def on_guild_join(self, guild:discord.Guild):
        author:discord.Member = guild.owner
        home:discord.Guild = discord.utils.get(self.Layla.guilds, id = HOME)

        embed = discord.Embed(title = f"Gracias por invitarme a {guild.name}!", color = 0x00bbff)
        embed.set_thumbnail(url = self.Layla.user.avatar)
        embed.add_field(name = f"Soy {self.Layla.user.name}", value =
                        "Soy aspirante a ser una bot multifuncional en español para tu servidor. Aunque actualmente sigo en desarrollo y con muchas tareas pendietes, me esforzaré para ayudarlos en lo que pueda, y hacer de tu servidor más agradable y acogedor.",
                        inline = False)
        
        embed.add_field(name = f"Primeros pasos", value = 
                        f"Puedes configurar mi prefijo con `,setprefix <nuevo prefijo>`. Si alguna vez olvidas mi prefijo puedes escribir {self.Layla.user.mention} prefix.\n" + 
                        "Tambien puedes ver mi lista de comandos disponibles con el comando `help`. Estoy aqui para ayudarte en lo que necesites.",
                        inline = False)
        
        embed.add_field(name = "Contacto y ayuda adicional", value = 
                        f"Si hay algo en lo que no pueda ayudarte, tienes alguna sugerencia o has encontrado un bug, puedes unirte a [{home.name}](https://discord.gg/85hexN9TyM) o contactar con <@608870766586494976> para hablar sobre esa situación.",
                        inline = False)
        
        embed.set_footer(text = f"Versión: {VERSION}")

        await author.send(embed = embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if "prefix" in message.content.lower() and self.Layla.user.mention in message.content:
            prefix = self.Layla.command_prefix(self.Layla, message)
            await message.channel.send(f"El prefijo de este servidor es {prefix}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open("./json/log_channels.json", "r") as f:
            log = json.load(f)

        channel_id = log.get(str(member.guild.id))
        if channel_id is not None:
            channel_out = self.Layla.get_channel(channel_id)
            await channel_out.send(f"{member.name} Se ha unido al servidor")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        with open("./json/log_channels.json", "r") as f:
            log = json.load(f)

        channel_id = log.get(str(member.guild.id))
        if channel_id is not None:
            channel_out = self.Layla.get_channel(channel_id)
            await channel_out.send(f"{member.name} Se ha ido al servidor")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.HTTPException):
            await ctx.send("Ocurrió un error al intentar conectarse a Discord. Inténtalo de nuevo más tarde.")

async def setup(Layla):
    await Layla.add_cog(Eventos(Layla))