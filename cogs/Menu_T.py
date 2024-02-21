import discord
from discord.ext import commands

class SelectMenu(discord.ui.View):
    options = [
        discord.SelectOption(label="Rojo", value=1, description="Color rojo"),
        discord.SelectOption(label="Verde", value=2, description="Color verde"),
        discord.SelectOption(label="Azul", value=3, description="Color azul")
    ]

    @discord.ui.select(placeholder="Selecciona un color", options=options)
    async def menu_callback(self, interaction:discord.Interaction, select):
        select.disabled=True
        if select.values[0] == "1":
            await interaction.response.send_message(content="Escogiste el color rojo")
        elif select.values[0] == "2":
            await interaction.response.send_message(content="Escogiste el color verde")
        elif select.values[0] == "3":
            await interaction.response.send_message(content="Escogiste el color azul")

class Menu_T(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla
        Menu_T.__doc__="Cog de prueba"

    @commands.hybrid_command(name="setcolor", description="Establece un color de usuario")
    async def setcolor(self, ctx):
        await ctx.send("Selecciona un color", view=SelectMenu())
        await ctx.send("Por cierto esto no sirve de nada xd")

async def setup(Layla):
    await Layla.add_cog(Menu_T(Layla))