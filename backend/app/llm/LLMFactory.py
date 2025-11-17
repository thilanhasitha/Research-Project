from typing import Dict, Type
from langchain_core.language_models.llms import LLM
from app.llm.LLMProvider import LLMProvider

class LLMFactory:
    
    _providers : Dict[str : Type[LLMProvider]]
    _instances : Dict[str : LLMProvider]
    
    @classmethod
    def register_provider(cls, provider_name: str, provider_class: Type[LLMProvider]):
        provider_name = provider_name.lower()
        if provider_name in cls._providers:
            cls._providers[provider_name] = provider_class
        else:
            cls._providers[provider_name] = provider_class
            
    @classmethod
    def get_provider(cls, provider_name: str) -> LLMProvider:
        provider_name = provider_name.lower()
        
        if provider_name not in cls._providers:
            raise ValueError(f"Provider '{provider_name}' is not registered. "
                           f"Available providers: {list(cls._providers.keys())}")
        
        if provider_name not in cls._instances:
            cls._instances[provider_name] = cls._providers[provider_name]()
            
        return cls._instances[provider_name]
    
    def create_llm(cls, provider_name: str, **kwargs) -> LLM:
        provider = cls.get_provider(provider_name)
        return provider.create_llm(**kwargs)
    
    def get_llm(cls, provider_name: str) -> LLM:
        provider = cls.get_provider(provider_name)
        return provider.get_llm()