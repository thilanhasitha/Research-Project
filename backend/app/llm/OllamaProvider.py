import json
from langchain_community.chat_models import ChatOllama
from langchain.schema import SystemMessage, HumanMessage
from app.llm.LLMProvider import LLMProvider


class OllamaProvider(LLMProvider):
    """
    Ollama LLM provider using LangChain's ChatOllama wrapper.
    Implements a consistent async generate() method for the project.
    """

    def __init__(self, model: str = "llama3:latest", temperature: float = 0.2):
        self.model = model
        self.temperature = temperature
        self._llm = None  # Singleton LLM instance

    # ------------------------------------
    # CREATE INSTANCE
    # ------------------------------------
    def create_llm(self):
        return ChatOllama(
            model=self.model,
            base_url="http://localhost:11434",
            temperature=self.temperature,
            # Optimize for speed
            num_predict=150,  # Limit response length for faster generation
            num_ctx=2048,     # Reduce context window for speed
            top_p=0.9,        # Faster sampling
            repeat_penalty=1.1
        )

    # ------------------------------------
    # GET SINGLETON
    # ------------------------------------
    def get_llm(self):
        if self._llm is None:
            self._llm = self.create_llm()
        return self._llm

    # ------------------------------------
    # MAIN GENERATION METHOD
    # Used by RSS summary & sentiment services
    # ------------------------------------
    async def generate(self, prompt: str):
        """
        Standardized async generate() method expected by services.
        Returns the final LLM string output only.
        """
        llm = self.get_llm()

        try:
            response = await llm.agenerate(
                messages=
                    [HumanMessage(content=prompt)]
                
            )

            # LangChain returns a list → extract text
            return response.generations[0].text.strip()

        except Exception as e:
            return f"LLM Error: {str(e)}"
