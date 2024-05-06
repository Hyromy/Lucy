import codecs, re

class IAModel:
    def __init__(self):
        from openai import OpenAI
        from data.config import AI_KEY
        
        self.ia = OpenAI(api_key = AI_KEY)

    def clear_utf(self, utf_sentence:str) -> str:
        def replace(match):
            return codecs.decode(match.group(0), "unicode-escape")

        utf_structure = r"\\u[0-9a-fA-F]{4}"
        return re.sub(utf_structure, replace, utf_sentence)


    def gpt(self, chat:list, premium = False) -> dict:
        if premium:
            model = "gpt-4"
            tokens = 500
        else:
            model = "gpt-3.5-turbo-0125"
            tokens = 100

        response = self.ia.chat.completions.create(
            model = model,
            messages = chat,
            max_tokens = tokens
        )

        role = response.choices[0].message.role
        content = response.choices[0].message.content

        print(content)

        return {"role":role, "content":content}

    def gpt_test(self, prompt:str, gpt4 = False):
        if gpt4:
            model = "gpt-4"
        else:
            model = "gpt-3.5-turbo-0125"

        response = self.ia.chat.completions.create(
            model = model,
            messages = [{"role":"user", "content":prompt}]
        )

        choices = []
        for i in range(len(response.choices)):
            choices.append({
                "finish_reason": response.choices[i].finish_reason,
                "index": i,
                "message": {
                    "content": response.choices[i].message.content,
                    "role": response.choices[i].message.role
                } 
            })

        data = {
            "choices": choices,
            "model": response.model,
            "object": response.object,
            "usage": {
                "completion_tokens": response.usage.completion_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }

        if gpt4:
            price = (response.usage.completion_tokens / 1000) * 0.06
            price += (response.usage.prompt_tokens / 1000) * 0.03
            
        else:
            price = (response.usage.completion_tokens / 1000) * 0.0015
            price += (response.usage.prompt_tokens / 1000) * 0.0005

        return data, price

    def dalle(self, prompt, format = "s", hd = False) -> str:
        if format == "s":
            size = "1024x1024"
        elif format == "v":
            size = "1024x1792"
        else:
            size = "1792x1024"

        if not hd:
            quality = "standard"
        else:
            quality = "hd"

        response = self.ia.images.generate(            
            model = "dall-e-3",
            prompt = prompt,
            size = size,
            quality = quality,
            n = 1
        )

        return response.data[0].url