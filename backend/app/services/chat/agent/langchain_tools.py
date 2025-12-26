from langchain_core.tools import StructuredTool
from app.Database.repositories.rss_repository import RSSRepository
# from app.Database.repositories.policy import PolicyRepository
from app.services.chat.agent.schema import *
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def build_mongo_tools(mongo_service: Optional[RSSRepository] = None) -> List[StructuredTool]:
    if mongo_service is None:
        mongo_service = RSSRepository()
        
    async def _get_news_by_id(item_id: str):
        """Fetch a single RSS news article by its ID."""
        return await mongo_service.get_by_id(item_id)
    
    
    async def _find_news_by_filter(filter_dict: dict, limit: int = 20):
        """Query MongoDB with a custom filter."""
        return await mongo_service.find_by_filter(filter_dict, limit)
    
    async def _get_latest_sri_lankan_news(limit: int = 10):
        """Get the latest Sri Lankan stock market and economic news from economynext."""
        return await mongo_service.get_latest_news(limit)

    return [
        StructuredTool.from_function(
            coroutine=_find_news_by_filter,
            name="search_sri_lankan_news",
            description="""Search Sri Lankan stock market and economic news from economynext. 
            Use this tool when user asks about Sri Lankan stocks, economy, market trends, or any financial news about Sri Lanka.
            Filter by title or content using regex patterns. Example: {"title": "stock"} or {"content": "market"}""",
            args_schema=MongoFilterInput,
        ),
        StructuredTool.from_function(
            coroutine=_get_latest_sri_lankan_news,
            name="get_latest_news",
            description="""Get the latest Sri Lankan stock market and economic news articles from economynext.
            Use this when user asks for recent news, latest updates, or what's happening in Sri Lankan markets.""",
            args_schema=MongoIDInput,
        ),
        StructuredTool.from_function(
            coroutine=_get_news_by_id,
            name="get_news_by_id",
            description="Fetch a specific news article by its MongoDB ID.",
            args_schema=MongoIDInput,
        ),
    ]
    

def build_weaviate_tools() -> List[StructuredTool]:
    """
    Build Weaviate tools for semantic search.
    Note: These tools are placeholders until Weaviate search methods are implemented.
    """
    
    async def _semantic_text_search(collection_name: str, query_text: str, limit: int = 10):
        """Perform semantic text search in Weaviate."""
        logger.warning("Weaviate semantic search not yet implemented. Returning empty results.")
        return {"status": "not_implemented", "message": "Weaviate semantic search coming soon", "results": []}

    async def _hybrid_text_search(collection_name: str, query_text: str, filters: Optional[Dict[str, Any]] = None, limit: int = 10):
        """Perform hybrid semantic + filter search in Weaviate."""
        logger.warning("Weaviate hybrid search not yet implemented. Returning empty results.")
        return {"status": "not_implemented", "message": "Weaviate hybrid search coming soon", "results": []}

    return [
        StructuredTool.from_function(
            coroutine=_semantic_text_search,
            name="weaviate_semantic_text_search",
            description="Perform semantic text search in Weaviate using raw query text (NOT YET IMPLEMENTED)",
            args_schema=TextSearchInput,
        ),
        StructuredTool.from_function(
            coroutine=_hybrid_text_search,
            name="weaviate_hybrid_text_search",
            description="Perform hybrid semantic text + filter search in Weaviate (NOT YET IMPLEMENTED)",
            args_schema=HybridTextSearchInput,
        ),
    ]
    



def build_tools():
    """Returns a dict of tools keyed by name, and a list for LLM binding."""
    mongo_tools = build_mongo_tools()
    weaviate_tools = build_weaviate_tools()
    all_tools = mongo_tools + weaviate_tools 
    tools_dict = {tool.name: tool for tool in all_tools}
    return tools_dict, all_tools

