from abc import ABC, abstractmethod
from langchain_core.language_models.llms import LLM

class LLMProvider(ABC):
    """
    Abstract Base Class for all LLM providers.
    Any new LLM (Gemini, Ollama, OpenAI, etc.) must implement this interface.
    """
    
    @abstractmethod
    def create_llm(self, **kwargs) -> LLM:
        """
        Create a new LLM instance with optional configuration.
        """
        pass 
    
    @abstractmethod
    def get_llm(self) -> LLM:
        """
        Return a reusable LLM instance (singleton).
        """
        pass
