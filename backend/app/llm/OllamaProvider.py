from langchain_community.chat_models import ChatOllama
from app.llm.LLMProvider import LLMProvider

class OllamaProvider(LLMProvider):

    def __init__(self):
        self._llm = None  # Holds the singleton instance
    
    def create_llm(self, model: str = "llama3:latest", **kwargs):
        """Create a new ChatOllama instance."""
        return ChatOllama(
            model=model,
            base_url="http://localhost:11434",
            **kwargs
        )

    def get_llm(self):
        """Return the singleton ChatOllama instance."""
        if self._llm is None:
            self._llm = ChatOllama(
                model="llama3:latest",
                base_url="http://localhost:11434"
            )
        return self._llm
