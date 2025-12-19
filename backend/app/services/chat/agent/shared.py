import logging
from app.services.chat.agent.langchain_tools import build_tools
from app.services.chat.agent.schema_manager import DynamicSchemaManager
from app.llm.client.ollama_client import OllamaClient   # << UPDATED

logger = logging.getLogger(__name__)

# Global variables
_llm_client = None
_tools = None
_tools_list = None
_schema_manager = None
_initialized = False

def _initialize():
    """Lazy initialization of shared resources."""
    global _llm_client, _tools, _tools_list, _schema_manager, _initialized
    
    if _initialized:
        return
    
    try:
        logger.info("Initializing shared resources...")
        
        # Initialize Ollama LLM Client
        _llm_client = OllamaClient().get_llm()
        
        # Build all LangChain tools
        _tools, _tools_list = build_tools()
        
        # Initialize Dynamic Schema Manager
        _schema_manager = DynamicSchemaManager()
        
        _initialized = True
        logger.info("Shared LLM client and tools initialized using Ollama.")
        
    except Exception as e:
        logger.error(f"Failed to initialize shared resources: {e}", exc_info=True)
        _llm_client = None
        _tools, _tools_list = {}, []
        _schema_manager = None
        raise

def get_llm_client():
    """Get LLM client, initializing if necessary."""
    if not _initialized:
        _initialize()
    return _llm_client

def get_tools():
    """Get tools dict, initializing if necessary."""
    if not _initialized:
        _initialize()
    return _tools

def get_tools_list():
    """Get tools list, initializing if necessary."""
    if not _initialized:
        _initialize()
    return _tools_list

def get_schema_manager():
    """Get schema manager, initializing if necessary."""
    if not _initialized:
        _initialize()
    return _schema_manager

# For backward compatibility, try to initialize immediately but don't fail
try:
    _initialize()
except Exception as e:
    logger.warning(f"Delayed initialization will occur on first use: {e}")

# Expose as module-level variables for backward compatibility
llm_client = get_llm_client() if _initialized else None
tools = get_tools() if _initialized else {}
tools_list = get_tools_list() if _initialized else []
schema_manager = get_schema_manager() if _initialized else None
