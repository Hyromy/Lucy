import discord
import random
import re
import emoji as pymoji

from discord.ext import commands

class Commands(commands.Cog):
    def __init__(self, Lucy:commands.Bot):
        self.Lucy = Lucy
        self.description = "Comandos básicos"
        self.emoji = "🤖"

    @commands.hybrid_command(
        name = "ping",
        help = "Muestra el ping del bot en milisegundos",
        usage = "ping"
    )
    async def ping(self, ctx:commands.Context):
        latency = round(self.Lucy.latency * 1000)

        embed = discord.Embed(
            title = "Pong!",
            description = f"{latency}ms",
            color = 0x00bbff
        )
        await ctx.reply(embed = embed)

    @commands.hybrid_command(
        name = "avatar",
        help = "Muestra el avatar de un usuario",
        usage = "avatar [@usuario]"
    )
    async def avatar(self, ctx:commands.Context, usuario:discord.User = None):
        usuario = usuario or ctx.author
        embed = discord.Embed(
            title = f"Avatar de {usuario.name}",
            color = 0x00bbff
        )
        if usuario.avatar:
            embed.set_image(url = usuario.avatar.url)
        else:
            embed.set_image(url = usuario.default_avatar.url)

        await ctx.reply(embed = embed)

    @commands.hybrid_command(
        name = "ball",
        help = "Responde a una pregunta con una respuesta aleatoria",
        aliases = ["8", "8ball"],
        usage = "ball [pregunta]"
    )
    async def ball(self, ctx:commands.Context, *, pregunta:str = None):
        answers = [
            "Sí",
            "No",
            "Tal vez",
            "Probablemente",
            "No lo sé",
            "¡Claro!",
            "¡Por supuesto!",
            "¡Obvio!",
            "¡No!",
            "¡Por supuesto que no!",
            "¡Nunca!",
            "¡Jamás!"
        ]
        
        embed = discord.Embed(
            title = f"🎱 {random.choice(answers)}",
            description = f"Pregunta: {pregunta}" if pregunta else "",
            color = 0x00bbff
        )
        await ctx.reply(embed = embed)

    @commands.hybrid_command(
        name = "emoji",
        help = "Muestra la URL de un emoji",
        usage = "emoji <:emoji:>"
    )
    async def emoji(self, ctx:commands.Context, emoji:discord.Emoji):
        embed = discord.Embed(
            title = f":{emoji.name}:",
            color = 0x00bbff
        )
        embed.set_image(url = emoji.url)
        embed.set_footer(text = f"ID emoji: {emoji.id}")

        await ctx.reply(embed = embed)
    
    @emoji.error
    async def emoji_error(self, ctx:commands.Context, error:commands.CommandError):                
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title = "Falta el emoji",
                description = "Debes mencionar un emoji",
                color = 0x00bbff
            )
        else:
            embed = discord.Embed(color = 0x00bbff)

            emoji_re = r"\".+\""
            emoji_catch = re.search(emoji_re, str(error)).group(0)[1:-1]
            if pymoji.is_emoji(emoji_catch):
                embed.title = "El emoji debe ser personalizado"
                embed.description = "No puedo obtener la URL de emojis predeterminados"
            else:
                name_re = r":.+:"
                emoji_name = re.search(name_re, emoji_catch).group(0)[1:-1]
                if emoji_name.count(":") > 0:
                    return

                embed.title = "Emoji no encontrado 😔"
                embed.description = f"Puedes invitarme al servidor que tenga el emoji :{emoji_name}: y usar el comando `emoji` para obtener la URL"

        await ctx.reply(
            embed = embed,
            ephemeral = True
        )

async def setup(Lucy:commands.Bot):
    await Lucy.add_cog(Commands(Lucy))