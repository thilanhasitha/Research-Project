from fastapi import APIRouter
from app.services.ollama_client import ask_ollama_via_service

router = APIRouter(prefix="/llm")

@router.post("/ask")
def ask_model(data: dict):
    prompt = data.get("prompt", "")
    result = ask_ollama_via_service(prompt)
    return {"response": result}
