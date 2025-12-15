import logging
from app.services.chat.agent.langchain_tools import build_tools
from app.services.chat.agent.schema_manager import DynamicSchemaManager
from app.llm.client.ollama_client import OllamaClient   # << UPDATED

logger = logging.getLogger(__name__)

try:
    # -----------------------------
    # Initialize Ollama LLM Client
    # -----------------------------
    llm_client = OllamaClient().get_llm()

    # -----------------------------
    # Build all LangChain tools
    # -----------------------------
    tools, tools_list = build_tools()

    # -----------------------------
    # Initialize Dynamic Schema Manager
    # -----------------------------
    schema_manager = DynamicSchemaManager()

    logger.info("Shared LLM client and tools initialized using Ollama.")
except Exception as e:
    logger.error(f"Failed to initialize shared resources: {e}")
    llm_client = None
    tools, tools_list = {}, []
