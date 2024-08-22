import discord
import os

from discord.ext import commands

from common.activies import get_prefix

class Commands(commands.Cog):
    def __init__(self, Lucy:commands.Bot):
        self.Lucy = Lucy
        self.description = "Comandos básicos"
        self.emoji = "🤖"

    def cogs_to_dict(self, include_events = False) -> dict[str, list[str]]:
        cogs_dict = {}
        for cog_name, cog in self.Lucy.cogs.items():
            cmds = cog.get_commands()
            if not include_events and cmds == []:
                continue

            cmds.sort(key = lambda x:x.name)
            cogs_dict[cog_name] = [cmd.name for cmd in cmds]

        return cogs_dict

    async def send_help(self, is_admin = False) -> discord.Embed:
        embed = discord.Embed(
            title = f"Comandos de {self.Lucy.user.name}",
            description = f"Estos son los comandos que puedes usar con {self.Lucy.user.name}",
            color = 0x00bbff
        )
        embed.set_thumbnail(url = self.Lucy.user.avatar)

        for cog in self.Lucy.cogs.values():
            if cog.get_commands():
                is_admin_cog = hasattr(cog, "admin")
                if ((not is_admin and is_admin_cog) ^
                    (is_admin and not is_admin_cog)
                ):
                    continue

                emoji = f"{cog.emoji} " if hasattr(cog, "emoji") else ""
                embed.add_field(
                    name = f"{emoji}{cog.qualified_name}",
                    value = cog.description or "",
                    inline = False
                )
            
        return embed

    async def send_help_cog(self, cog_name:str, ctx:commands.Context) -> discord.Embed | None:
        cog = self.Lucy.get_cog(cog_name)
        is_admin = ctx.author.id == int(os.getenv("OWNER_ID"))
        is_admin_cog = hasattr(cog, "admin")
        if not is_admin and is_admin_cog:
            return None

        embed = discord.Embed(
            title = f"Categoría: {cog.qualified_name}",
            description = cog.description,
            color = 0x00bbff
        )

        cmds = cog.get_commands()
        for cmd in sorted(cmds, key = lambda x:x.name):
            embed.add_field(
                name = cmd.name,
                value = ""
            )

        return embed

    async def send_help_command(self, cmd:str, ctx:commands.Context) -> discord.Embed:
        command = self.Lucy.get_command(cmd)
        cog = self.Lucy.get_cog(command.cog_name)
        is_admin = ctx.author.id == int(os.getenv("OWNER_ID"))
        is_admin_cog = hasattr(cog, "admin")
        if not is_admin and is_admin_cog:
            return None

        embed = discord.Embed(
            title = f"{command.cog_name}: {command.name}",
            description = command.help,
            color = 0x00bbff
        )
        if command.aliases:
            embed.add_field(
                name = "Alias",
                value = ", ".join(command.aliases),
                inline = False
            )
        embed.add_field(
            name = "Ejemplo de uso",
            value = f"`{get_prefix(self.Lucy, ctx.message)}{command.usage}`",
            inline = False
        )

        return embed

    @commands.hybrid_command(
        name = "help",
        help = "Muestra los comandos disponibles",
        aliases = ["h"],
        usage = "help [categoría | comando]",
    )
    async def help(self, ctx:commands.Context, argumento:str = None):
        if not argumento:
            await ctx.reply(embed = await self.send_help())
            return
        
        elif argumento.casefold() == "admin":
            if ctx.author.id == int(os.getenv("OWNER_ID")):
                await ctx.reply(embed = await self.send_help(is_admin = True))
            return
                
        for cog, cmds in self.cogs_to_dict().items():
            if cog.casefold() == argumento.casefold():
                await ctx.reply(embed = await self.send_help_cog(cog, ctx))
                return

            else:
                for cmd in cmds:
                    if cmd.casefold() == argumento.casefold():
                        await ctx.reply(embed = await self.send_help_command(cmd, ctx))
                        return
        
        await ctx.message.add_reaction("❌")

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

async def setup(Lucy:commands.Bot):
    await Lucy.add_cog(Commands(Lucy))