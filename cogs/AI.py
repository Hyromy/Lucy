import discord, json, datetime, pytz
from discord import app_commands
from discord.ext import commands
from data.config import PROMPT
from common.ia_library import IAModel
from data.config import DAD

class AI(commands.Cog):
    def __init__(self, Lucy):
        self.Lucy = Lucy
        self.model = IAModel()
        self.context = {"role": "system", "content": PROMPT.replace("\n", " ")}

    def new_chatbot(self, id:str):
        with open("./json/chatbot.json") as f:
            data = json.load(f)

        data[id] = {
            "premium":{
                "gpt": False,
                "dalle": False
            },
            "chat":[],
            "images":[]
        }

        with open("./json/chatbot.json", "w") as f:
            json.dump(data, f, indent = 4)

    def is_premium(self, id:str, model:str) -> bool:
        with open("./json/chatbot.json") as f:
            data = json.load(f)

        return data[id]["premium"][model]
    
    def get_chat_log(self, id:str) -> dict:
        with open("./json/chatbot.json") as f:
            data = json.load(f)

        return data[id]["chat"]

    def write_chat(self, id:str, chat:list):
        with open("./json/chatbot.json") as f:
            data = json.load(f)

        data[id]["chat"] = chat

        with open("./json/chatbot.json", "w", encoding = "utf-8") as f:
            json.dump(data, f, indent = 4)

    def forgot_messages(self, chat:list, max_len:int) -> list:
        while len(chat) > max_len:
            chat.pop(0)

        return chat.copy()
    
    def add_image_url(self, id:str, image_url:str):
        with open("./json/chatbot.json") as f:
            data = json.load(f)

        data[id]["images"].append(image_url)

        with open("./json/chatbot.json", "w") as f:
            json.dump(data, f, indent = 4)

    def get_current_status(self) -> str:
        with open("./data/current_status.txt", encoding = "utf-8") as f:
            current_status = f.read()

        return current_status

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        premium_gpt_b = discord.utils.get(before.roles, id = 1206038019782615140)
        premium_gpt_a = discord.utils.get(after.roles, id = 1206038019782615140)

        with open("./json/chatbot.json") as f:
            data = json.load(f)

        if premium_gpt_b is None and premium_gpt_a is not None:
            print("gpt premium añadido")
            data[str(after.id)]["premium"]["gpt"] = True

        elif premium_gpt_b is not None and premium_gpt_a is None:
            print("gpt premium removido")
            data[str(after.id)]["premium"]["gpt"] = False

        with open("./json/chatbot.json", "w") as f:
            json.dump(data, f, indent = 4)

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        try:
            if isinstance(message.channel, discord.DMChannel) and message.author != self.Lucy.user:        
                async with message.channel.typing():
                    with open("./json/chatbot.json") as f:
                        data = json.load(f)

                    user_id = str(message.author.id)
                    if not user_id in data:
                        self.new_chatbot(user_id)

                    context = self.context
                    premium = self.is_premium(user_id, "gpt")
                    if not premium:
                        context["content"] + "TUS RESPUESTAS SON DE 100 PALABRAS O MENOS"

                    chat = [context]
                    current_status = "(TU ESTADO O ACTIVIDAD ACTUAL ES) " + self.get_current_status()
                    chat.extend([{"role":"system", "content":current_status}])
                    previus_chat = self.get_chat_log(user_id)
                    if len(previus_chat) > 0:
                        chat.extend(previus_chat)
                    chat.extend([{"role":"user", "content":message.content}])

                    answer = self.model.gpt(chat, premium)
                    chat.extend([answer])
                    chat.pop(0)
                    chat.pop(0)

                    chat = self.forgot_messages(chat, 10)
                    self.write_chat(user_id, chat)
                    await message.channel.send(chat[-1]["content"] + f"`Premium: {premium}`")

        except discord.HTTPException:
            embed = discord.Embed(color = 0x00bbff)
            embed.add_field(
                name = "Problemas con Discord",
                value = "La respuesta generada posee más de 2000 caracteres por lo que no fue posible enviar la respuesta"
            )

            await message.channel.send(embed = embed)

        except Exception as e:
            current = datetime.datetime.now(pytz.timezone('America/Mexico_City'))
            f_t = current.strftime("%H:%M:%S")
            print(f"    (!) [{f_t}] Problemas con IA -> {e.__class__.__name__}: {str(e)}")

            embed = discord.Embed(colour = 0x00bbff)
            embed.add_field(
                name = "Problemas con la IA",
                value = "Hubo un problema con la integración de Inteligencia Artificial, Intentalo más tarde"
            )
            
            await message.channel.send(embed = embed)

    @app_commands.command(name = "generate", description = "Genera una imagen con Inteligencia Artificial")
    async def generate(self, interaction:discord.Interaction, prompt:str, formato:str, hd:bool):
        premium = self.is_premium(str(interaction.user.id), "dalle")
        if interaction.user.id != DAD or premium:
            embed = discord.Embed(color = 0x00bbff, title = "Generación no disponible")
            embed.add_field(name = "", value = f"Desafortunadamente la IA generativa de imagen es costosa, por lo que <@{DAD}> ha limitado su uso.\nLamentamos las molestias")
        
        else:
            async with interaction.channel.typing():
                try:
                    image_url = self.model.dalle(prompt, formato, hd)
                    self.add_image_url(str(interaction.user.id), image_url)

                    embed = discord.Embed(color = 0x00bbff, title = "Imagen generada")
                    embed.set_image(url = image_url)

                except Exception as e:
                    embed = discord.Embed(color = 0x00bbff, title = "Hubo un problema")
                    embed.add_field(name = "Hubo un problema al general la imagen", value = e)
                
        await interaction.channel.send(embed = embed)

    @app_commands.command(name = "gptdata", description = "realiza una prueba con tu modelo de chatbot asignado")
    async def gptdata(self, interaction:discord.Interaction, prompt:str):
        try:
            premium = self.is_premium(str(interaction.user.id), "gpt")
        
        except KeyError:
            self.new_chatbot(str(interaction.user.id))
            premium = False

        except Exception as e:
            print(f"    (!) {e.__class__}")

        finally:
            async with interaction.channel.typing():
                data, price = self.model.gpt_test(prompt = prompt, gpt4 = premium)

                embed = discord.Embed(color = 0x00bbff, title = "ChatBot Data")
                embed.add_field(name = "", value = f"`{data}`", inline = False)
                embed.add_field(name = "Costo de la petición", value = f"${price}", inline = False)

                embed.set_footer(text = f"Pedido por {interaction.user.name}", icon_url = interaction.user.avatar.url)

                await interaction.channel.send(embed = embed)

async def setup(Lucy):
    await Lucy.add_cog(AI(Lucy))