import discord
import os
import datetime
import pytz

from utils.SQL import SQLHelper

from discord.ext import commands

class MySQL(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    async def generic_error(self, ctx:commands.Context, error:commands.CommandError):
        current = datetime.datetime.now(pytz.timezone("America/Mexico_City"))
        f_time = current.strftime("%H:%M:%S")
        command_error = f"{ctx.command.name}:{error.__class__.__name__}"
        print(f"\t(!) [{f_time}] <{command_error}> -> {error.__cause__}")
        
        await ctx.message.add_reaction("❌")

    @commands.command()
    async def sqlexport(self, ctx:commands.Context, out_file = "backup"):
        if ctx.author.id != int(os.getenv("OWNER_ID")):
            return
        
        await ctx.message.add_reaction("🔄")

        sql = SQLHelper()
        sql.export_db(out_file)
        sql.close_conection()

        await ctx.author.send(
            file = discord.File(f"{out_file}.sql"),
            delete_after = 60)
        os.remove(f"{out_file}.sql")
        await ctx.message.add_reaction("✅")

    @sqlexport.error
    async def sqlexport_error(self, ctx:commands.Context, error:commands.CommandError):
        await self.generic_error(ctx, error)

    @commands.command()
    async def sqlimport(self, ctx:commands.Context):
        if ctx.author.id != int(os.getenv("OWNER_ID")):
            return

        await ctx.message.add_reaction("🔄")
        
        sql = SQLHelper()
        sql.import_db("backup.sql")
        sql.close_conection()
        
        await ctx.message.add_reaction("✅")

    @sqlimport.error
    async def sqlimport_error(self, ctx:commands.Context, error:commands.CommandError):
        await self.generic_error(ctx, error)

    @commands.command()
    async def sqlcache(self, ctx:commands.Context):
        if ctx.author.id != int(os.getenv("OWNER_ID")):
            return
        
        await ctx.message.add_reaction("🔄")
        
        sql = SQLHelper()
        sql.load_cache()
        sql.close_conection()
        
        await ctx.message.add_reaction("✅")

    @sqlcache.error
    async def sqlcache_error(self, ctx:commands.Context, error:commands.CommandError):
        await self.generic_error(ctx, error)

    @commands.command()
    async def sqlbuildfromcache(self, ctx:commands.Context):
        if ctx.author.id != int(os.getenv("OWNER_ID")):
            return
        
        await ctx.message.add_reaction("🔄")
        
        sql = SQLHelper()
        sql.build_from_cache()
        sql.close_conection()
        
        await ctx.message.add_reaction("✅")

    @sqlbuildfromcache.error
    async def sqlbuildfromcache_error(self, ctx:commands.Context, error:commands.CommandError):
        await self.generic_error(ctx, error)

async def setup(bot:commands.Bot):
    await bot.add_cog(MySQL(bot))