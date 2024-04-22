class IAModel:
    def __init__(self):
        from openai import OpenAI
        from data.config import AI_KEY
        
        self.ia = OpenAI(api_key = AI_KEY)

    def gpt(self, chat:list, premium = False) -> dict:
        if premium:
            model = "gpt-4-turbo"
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

        return {"role":role, "content":content}
        
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