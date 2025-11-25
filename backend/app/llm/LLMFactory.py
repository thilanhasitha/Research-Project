from typing import Dict, Type
from langchain_core.language_models.llms import LLM
from app.llm.LLMProvider import LLMProvider

class LLMFactory:
    
    _providers: Dict[str, Type[LLMProvider]] = {}
    _instances: Dict[str, LLMProvider] = {}
    
    @classmethod
    def register_provider(cls, provider_name: str, provider_class: Type[LLMProvider]):
        """
        Register a new LLM provider (Gemini, Ollama, OpenAI, etc.)
        """
        provider_name = provider_name.lower()
        cls._providers[provider_name] = provider_class
    
    @classmethod
    def get_provider(cls, provider_name: str) -> LLMProvider:
        """
        Get a provider instance (singleton). Create if not exists.
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls._providers:
            raise ValueError(f"Provider '{provider_name}' is not registered. "
                             f"Available providers: {list(cls._providers.keys())}")
        
        if provider_name not in cls._instances:
            cls._instances[provider_name] = cls._providers[provider_name]()
        
        return cls._instances[provider_name]
    
    @classmethod
    def create_llm(cls, provider_name: str, **kwargs) -> LLM:
        """
        Create a new LLM instance from the provider with optional configuration.
        """
        provider = cls.get_provider(provider_name)
        return provider.create_llm(**kwargs)
    
    @classmethod
    def get_llm(cls, provider_name: str) -> LLM:
        """
        Get the default LLM instance from the provider (singleton).
        """
        provider = cls.get_provider(provider_name)
        return provider.get_llm()
