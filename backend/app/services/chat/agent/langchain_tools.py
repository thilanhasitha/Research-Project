from langchain_core.tools import StructuredTool
from app.Database.repositories.rss_repository import RSSRepository
# from app.Database.repositories.search import BaseWeaviateSearchRepository
# from app.Database.repositories.cart import CartRepository
# from app.Database.repositories.policy import PolicyRepository
from app.services.chat.agent.schema import *
from typing import Optional, List, Dict, Any


def build_mongo_tools(mongo_service: Optional[RSSRepository] = None) -> List[StructuredTool]:
    if mongo_service is None:
        mongo_service = RSSRepository()
        
    async def _get_product_by_id(item_id: str):
        """Fetch a single product by its ID."""
        return await mongo_service.get_by_id(item_id)
    
    
    async def _find_by_filter(filter_dict: dict, limit: int = 100):
        """Query MongoDB with a custom filter."""
        return await mongo_service.find_by_filter(filter_dict, limit)

    return [
        StructuredTool.from_function(
            coroutine=_find_by_filter,
            name="mongo_find_by_filter",
            description="Find rss_news in MongoDB collection using a filter dictionary",
            args_schema=MongoFilterInput,
        ),
        StructuredTool.from_function(
            coroutine=_get_product_by_id,
            name="get_product_by_id",
            description="Fetch a single product by its item_id. Use this when you have an exact product ID.",
            args_schema=MongoIDInput,
        ),
    ]
    

def build_weaviate_tools(weaviate_repo: Optional[BaseWeaviateSearchRepository] = None) -> List[StructuredTool]:
    if weaviate_repo is None:
        weaviate_repo = BaseWeaviateSearchRepository()
    
    async def _semantic_text_search(collection_name: str, query_text: str, limit: int = 10):
        return weaviate_repo.semantic_text_search(collection_name, query_text, limit)

    async def _hybrid_text_search(collection_name: str, query_text: str, filters: Optional[Dict[str, Any]] = None, limit: int = 10):
        return weaviate_repo.hybrid_text_search(collection_name, query_text, filters, limit)

    return [
        StructuredTool.from_function(
            coroutine=_semantic_text_search,
            name="weaviate_semantic_text_search",
            description="Perform semantic text search in Weaviate using raw query text",
            args_schema=TextSearchInput,
        ),
        StructuredTool.from_function(
            coroutine=_hybrid_text_search,
            name="weaviate_hybrid_text_search",
            description="Perform hybrid semantic text + filter search in Weaviate",
            args_schema=HybridTextSearchInput,
        ),
    ]
    



def build_tools():
    """Returns a dict of tools keyed by name, and a list for LLM binding."""
    mongo_tools = build_mongo_tools()
    weaviate_tools = build_weaviate_tools()
    cart_tools = build_cart_tool()
    all_tools = mongo_tools + weaviate_tools + cart_tools
    tools_dict = {tool.name: tool for tool in all_tools}
    return tools_dict, all_tools

