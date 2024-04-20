import discord, json, time
from openai import OpenAI
from discord.ext import commands
from data.config import AI_KEY, PROMPT

class AI(commands.Cog):
    def __init__(self, Lucy):
        self.Lucy = Lucy
        self.ia = OpenAI(api_key = AI_KEY)
        self.context = {"role": "system", "content": PROMPT.replace("\n", " ")}

    def answer(self, history):
        chat = [self.context]
        chat.extend(history)

        completion = self.ia.chat.completions.create(
            model = "gpt-3.5-turbo-0125",
            messages = chat,
            max_tokens = 75
        )

        role = completion.choices[0].message.role
        content = completion.choices[0].message.content

        return {"role": role, "content": content}

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if isinstance(message.channel, discord.DMChannel) and message.author != self.Lucy.user:
            async with message.channel.typing():
                try:
                    with open("./json/chatbot.json") as f:
                        data = json.load(f)
                except:
                    time.sleep(5)

                user_id = str(message.author.id)
                if not user_id in data:
                    data[user_id] = []
                    with open("./json/chatbot.json", "w", encoding = "utf-8") as f:
                        json.dump(data, f, indent = 4)

                data[user_id].append({"role": "user", "content": message.content})
                answer = self.answer(data[user_id])
                data[user_id].append(answer)

                if len(data[user_id]) > 20:
                    for i in range(2):
                        data[user_id].pop(0)

                with open("./json/chatbot.json", "w", encoding = "utf-8") as f:
                    json.dump(data, f, indent = 4)

                await message.channel.send(answer["content"])

async def setup(Lucy):
    await Lucy.add_cog(AI(Lucy))