import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla

    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx, amount:int):
        await ctx.channel.purge(limit = amount)

    @commands.command()
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member:discord.Member, reason = None):
        await ctx.guild.kick(member)
        await ctx.send(f"<@{member.id}> Fue explulsado")

    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, member:discord.Member, reason = None):
        await ctx.guild.ban(member)
        await ctx.send(f"<@{member.id}> Fue baneado")

    @commands.command(name = "unban")
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def unban(self, ctx, user_id):
        user = discord.Object(id = user_id)
        await ctx.guild.unban(user)

        await ctx.send(f"<@{user_id}> ya no esta baneado")

async def setup(Layla):
    await Layla.add_cog(Moderation(Layla))