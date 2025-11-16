import requests
import os

# URL of Ollama microservice
OLLAMA_SERVICE_URL = os.getenv("OLLAMA_SERVICE_URL", "http://ollama_service:8000/ask")

def ask_ollama_via_service(prompt: str):
    try:
        r = requests.post(OLLAMA_SERVICE_URL, json={"prompt": prompt})
        r.raise_for_status()
        return r.json()["response"]
    except Exception as e:
        print(f"Error calling Ollama service: {e}")
        return "Ollama service error"
