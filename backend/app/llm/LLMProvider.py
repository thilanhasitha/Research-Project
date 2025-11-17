from abc import ABC, abstractmethod
from langchain_core.language_models.llms import LLM

class LLMProvider(ABC):
    @abstractmethod
    def create_llm(self, **kwargs) -> LLM:
        pass
    
    @abstractmethod
    def get_llm(self) -> LLM:
        pass