import os
from typing import Optional
from langchain_community.llms import Ollama
from langchain_core.language_models.llms import LLM
from app.llm.LLMProvider import LLMProvider


class OllamaClient(LLMProvider):

    _instance: Optional['OllamaClient'] = None
    _llm_instance: Optional[LLM] = None

    def __new__(cls) -> 'OllamaClient':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True

            # Load environment variables
            self._default_model = os.getenv("OLLAMA_MODEL", "llama3")
            self._default_temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))

            # URL of Ollama server (default: localhost)
            self._ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    def create_llm(self, **kwargs) -> LLM:
        config = {
            "model": kwargs.get("model", self._default_model),
            "temperature": kwargs.get("temperature", self._default_temperature),
            "base_url": kwargs.get("base_url", self._ollama_host),
        }

        return Ollama(**config)

    def get_llm(self) -> LLM:
        if self._llm_instance is None:
            self._llm_instance = self.create_llm()
        return self._llm_instance

    @property
    def current_config(self):
        return {
            "model": self._default_model,
            "temperature": self._default_temperature,
            "ollama_host": self._ollama_host
        }
