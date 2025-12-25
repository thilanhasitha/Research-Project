import os
from typing import Optional
from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel
from app.llm.LLMProvider import LLMProvider
import json
import logging

logger = logging.getLogger(__name__)


class OllamaClient(LLMProvider):

    _instance: Optional['OllamaClient'] = None
    _llm_instance: Optional[BaseChatModel] = None

    def __new__(cls) -> 'OllamaClient':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True

            # Read from environment with proper defaults for Docker
            self._default_model = os.getenv("OLLAMA_MODEL", "llama3.2")
            self._default_temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))
            self._ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
            
            logger.info(f"OllamaClient initialized: host={self._ollama_host}, model={self._default_model}")

    def create_llm(self, **kwargs) -> BaseChatModel:
        config = {
            "model": kwargs.get("model", self._default_model),
            "temperature": kwargs.get("temperature", self._default_temperature),
            "base_url": kwargs.get("base_url", self._ollama_host),
            "timeout": kwargs.get("timeout", 240),  # 4 minutes timeout for LLM calls
        }
        logger.info(f"Creating ChatOllama with config: {config}")
        return ChatOllama(**config)

    def get_llm(self) -> BaseChatModel:
        if self._llm_instance is None:
            self._llm_instance = self.create_llm()
        return self._llm_instance

    
    #  Add Unified Generate Method (Fix For RSSService)
    # ---------------------------------------------------------
    async def generate(self, prompt) -> str:
        """
        Unified async generate wrapper that accepts either:
         - a single string prompt, or
         - a list of string prompts

        It calls the underlying Ollama LLM and returns a string response.
        """
        import asyncio
        llm = self.get_llm()

        # Normalize input to single string
        if isinstance(prompt, list):
            prompt_str = prompt[0] if prompt else ""
        else:
            prompt_str = str(prompt)

        try:
            logger.info(f"Calling Ollama invoke with prompt length: {len(prompt_str)}")
            # Use asyncio.to_thread to run synchronous invoke in thread pool
            response = await asyncio.to_thread(llm.invoke, prompt_str)
            logger.info(f"Ollama response type: {type(response)}, length: {len(str(response)) if response else 0}")
            
            # invoke returns a string directly
            if isinstance(response, str):
                return response
            
            # Fallback: try to extract text from response object
            if hasattr(response, 'text'):
                return response.text
            if hasattr(response, 'content'):
                return response.content
            if isinstance(response, dict):
                return response.get("text") or response.get("content") or str(response)
            
            # Last resort
            return str(response)
            
        except Exception as e:
            logger.error(f"Ollama generate error: {type(e).__name__}: {e}")
            raise RuntimeError(f"Ollama generate() failed: {e}")

    @property
    def current_config(self):
        return {
            "model": self._default_model,
            "temperature": self._default_temperature,
            "ollama_host": self._ollama_host
        }
