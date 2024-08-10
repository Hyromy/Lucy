import discord
import os

from utils.MySQL import MySQLHelper

from discord.ext import commands

class MySQL(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.command()
    async def mysqlexport(self, ctx:commands.Context):
        if ctx.author.id != int(os.getenv("OWNER_ID")):
            return
        
        mysql = MySQLHelper()
        mysql.export_db("db")
        mysql.close()
        del mysql

        await ctx.message.add_reaction("✅")

    @commands.command()
    async def mysqlimport(self, ctx:commands.Context):
        if ctx.author.id != int(os.getenv("OWNER_ID")):
            return

        mysql = MySQLHelper()
        mysql.import_db("db.sql")
        mysql.close()

        await ctx.message.add_reaction("✅")

    @commands.command()
    async def mysqlsend(self, ctx:commands.Context, db_name:str = "backup"):
        if ctx.author.id != int(os.getenv("OWNER_ID")):
            return

        mysql = MySQLHelper()
        mysql.export_db(db_name)
        mysql.close()

        await ctx.author.send(
            file = discord.File(f"{db_name}.sql"),
            delete_after = 60
        )
        await ctx.message.add_reaction("✅")

    @commands.command()
    async def mysqldrop(self, ctx:commands.Context):
        if ctx.author.id != int(os.getenv("OWNER_ID")):
            return

        mysql = MySQLHelper()
        mysql.drop_tables()
        mysql.close()

        await ctx.message.add_reaction("✅")

    @commands.command()
    async def mysqlreloadcache(self, ctx:commands.Context):
        if ctx.author.id != int(os.getenv("OWNER_ID")):
            return

        mysql = MySQLHelper()
        mysql.export_db("db")
        mysql.db_to_cache()
        mysql.close()

        await ctx.message.add_reaction("✅")

    @commands.command()
    async def mysqlthisserver(self, ctx:commands.Context):
        if ctx.author.id != int(os.getenv("OWNER_ID")):
            return

        mysql = MySQLHelper()
        try:
            atr = mysql.get_atributes("guilds")
            values = (ctx.guild.id, ",")
            mysql.insert("guilds", atr, values)
        except Exception as e:
            print(e)

        mysql.close()
        await ctx.message.add_reaction("✅")

async def setup(bot):
    await bot.add_cog(MySQL(bot))