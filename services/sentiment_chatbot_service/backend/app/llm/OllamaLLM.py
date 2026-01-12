# app/llm/OllamaLLM.py

import aiohttp

class OllamaLLM:
    def __init__(self, model="llama3"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    async def generate(self, prompt: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json={"model": self.model, "prompt": prompt}) as resp:
                raw = await resp.json()
                return raw.get("response", "")
            
            
