from fastapi import FastAPI
from ollama import Client
import os
from pydantic import BaseModel

app = FastAPI()

client = Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2")

class PromptRequest(BaseModel):
    prompt: str

@app.post("/ask")
def ask(prompt_request: PromptRequest):
    prompt = prompt_request.prompt
    response = client.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )
    return {"response": response.get("message", {}).get("content", "")}
