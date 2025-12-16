import os
from typing import Optional
from langchain_ollama import OllamaLLM
from langchain_core.language_models.llms import LLM
from app.llm.LLMProvider import LLMProvider
import json
import logging

logger = logging.getLogger(__name__)


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

            # Read from environment with proper defaults for Docker
            self._default_model = os.getenv("OLLAMA_MODEL", "llama3.2")
            self._default_temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))
            self._ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
            
            logger.info(f"OllamaClient initialized: host={self._ollama_host}, model={self._default_model}")

    def create_llm(self, **kwargs) -> LLM:
        config = {
            "model": kwargs.get("model", self._default_model),
            "temperature": kwargs.get("temperature", self._default_temperature),
            "base_url": kwargs.get("base_url", self._ollama_host),
        }
        logger.info(f"Creating OllamaLLM with config: {config}")
        return OllamaLLM(**config)

    def get_llm(self) -> LLM:
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

        It calls the underlying Ollama LLM using the interface it accepts,
        and returns a single string (the first generation).
        """
        llm = self.get_llm()

        # Ensure we send a list[str] if the underlying LLM expects that.
        prompts: list[str]
        if isinstance(prompt, str):
            prompts = [prompt]
        elif isinstance(prompt, list):
            prompts = prompt
        else:
            raise TypeError("prompt must be str or list[str]")

        try:
            # Try calling the async interface that accepts a list of prompts.
            # Many LangChain community LLM wrappers expect a list[str] called "prompts".
            response = await llm.ainvoke(prompts)  # try list-based async call
        except TypeError:
            # If the method signature expects a single string, try calling with the first prompt.
            try:
                response = await llm.ainvoke(prompts[0])
            except Exception as e:
                raise RuntimeError(f"Ollama generate() failed on second attempt: {e}")
        except Exception as e:
            # Some wrappers return a structured object; rethrow for higher-level code to handle.
            raise RuntimeError(f"Ollama generate() failed: {e}")

        # Normalize the response to a single string:
        # - If it's already a string => return it
        # - If it's a list => take the first element (and its text if nested)
        # - If it's an object with 'text' or 'content' => extract
        if isinstance(response, str):
            return response
        # handle list-like responses
        if isinstance(response, (list, tuple)):
            first = response[0] if len(response) > 0 else ""
            if isinstance(first, str):
                return first
            # try common nested fields
            if isinstance(first, dict):
                return first.get("text") or first.get("content") or json.dumps(first)
            try:
                return str(first)
            except Exception:
                return ""
        # handle dict-like responses
        if isinstance(response, dict):
            return response.get("text") or response.get("content") or json.dumps(response)

        # fallback
        return str(response)

    @property
    def current_config(self):
        return {
            "model": self._default_model,
            "temperature": self._default_temperature,
            "ollama_host": self._ollama_host
        }
