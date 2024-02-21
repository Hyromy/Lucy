import discord
from discord import app_commands
from discord.ext import commands

class AllButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    #blurple
    @discord.ui.button(label="Primary", style=discord.ButtonStyle.primary)
    async def primary(self, interaction:discord.Interaction):
        await interaction.response.send_message(content="Boton primario presionado")

    #gray, gray
    @discord.ui.button(label="Secondary", style=discord.ButtonStyle.secondary)
    async def secondary(self, interaction:discord.Interaction):
        await interaction.response.send_message(content="Boton secundario presionado")

    #green
    @discord.ui.button(label="Success", style=discord.ButtonStyle.success)
    async def success(self, interaction:discord.Interaction):
        await interaction.response.send_message(content="Boton exito presionado")

    #red
    @discord.ui.button(label="Danger", style=discord.ButtonStyle.danger)
    async def danger(self, interaction:discord.Interaction):
        await interaction.response.send_message(content="Boton peligro presionado")

class Buttons_T(commands.Cog):
    def __init__(self, Layla):
        self.Layla = Layla
        Buttons_T.__doc__="Gog de prueba"

    @app_commands.command(name="botones", description="menu de botones")
    async def allbutton(self, interaction:discord.Interaction):
        await interaction.response.send_message(content="Presiona un boton1", view=AllButtons())

async def setup(Layla):
    await Layla.add_cog(Buttons_T(Layla))