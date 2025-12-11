import asyncio
from app.llm.client.ollama_client import OllamaClient
from app.llm.LLMFactory import LLMFactory

# IMPORTANT: Register Ollama provider first
LLMFactory.register_provider("ollama", OllamaClient)


async def test_ollama():
    print(" Initializing Ollama client through LLMFactory...")

    try:
        provider = LLMFactory.get_provider("ollama")
        llm_instance = provider.get_llm()

        print("✔ Provider loaded:", provider.current_config)
        print("✔ LLM instance created:", llm_instance)

        print("\n📨 Sending test prompt to Ollama...\n")

        response = await provider.generate("Hello from test_ollama! Are you working correctly?")
        
        print(" Response from Ollama:")
        print(response)

        print("\n Ollama integration is WORKING correctly!\n")

    except Exception as e:
        print("\n Ollama integration FAILED!")
        print("Error:", e)


if __name__ == "__main__":
    asyncio.run(test_ollama())
