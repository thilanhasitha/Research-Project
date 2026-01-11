# FILE: app/services/chat/agent/schema.py
# (This is the full file content)

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.models.models import MessageModel


# Schema for tool input
class MongoFilterInput(BaseModel):
    filter_dict: Dict[str, Any] = Field(..., description="The MongoDB filter in dictionary format")
    limit: int = Field(100, description="Maximum number of items to return (default 100)")
    
class MongoIDInput(BaseModel):
    item_id: str = Field(..., description="The item_id to get item details")
    
class SemanticSearchInput(BaseModel):
    collection_name: str = Field(..., description="Weaviate collection name to search")
    query_vector: List[float] = Field(..., description="Embedding vector of the query")
    limit: int = Field(10, description="Number of results to return (default 10)")

class TextSearchInput(BaseModel):
    collection_name: str = Field(..., description="Weaviate collection name to search")
    query_text: str = Field(..., description="Natural language query")
    limit: int = Field(10, description="Number of results to return (default 10)")

class HybridSearchInput(BaseModel):
    collection_name: str = Field(..., description="Weaviate collection name to search")
    query_vector: List[float] = Field(..., description="Embedding vector of the query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional Mongo-style filters")
    limit: int = Field(10, description="Number of results to return (default 10)")

class HybridTextSearchInput(BaseModel):
    collection_name: str = Field(..., description="Weaviate collection name to search")
    query_text: str = Field(..., description="Natural language query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional Mongo-style filters")
    limit: int = Field(10, description="Number of results to return (default 10)")


class ChatRequest(BaseModel):
    message: str
    user_id: str
    conversation_id: Optional[str] = None 
    metadata: Optional[Dict[str, Any]] = None
    
class ProductDisplay(BaseModel):
    """Product information for visual display."""
    id: str
    name: str
    price: float
    image_url: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    in_stock: bool = True

class ChatResponse(BaseModel):
    reply: str
    conversation_id: Optional[str] = None
    user_id: str
    needs_more_info: bool = False
    products: Optional[List[ProductDisplay]] = None
    show_add_to_cart: bool = False
    show_variant_selector: bool = False
    variant_data: Optional[Dict[str, Any]] = None
    
class AgentState(BaseModel):
    input: str
    user_id: str
    conversation_history: Optional[List[MessageModel]] = Field(default_factory=list)
    
    current_intent: Optional[str] = None 
    last_intent: Optional[str] = None 
    
    tool_results: Optional[List[Dict[str, Any]]] = None
    output: Optional[str] = None
    has_tool_calls: bool = False
    
    needs_clarification: bool = False
    clarification_message: Optional[str] = None
    extracted_filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    pending_cart_action: Optional[Dict[str, Any]] = None
    
    focused_product_id: Optional[str] = None
    
    products: Optional[List[Dict[str, Any]]] = None
    cart_action_result : Optional[Dict[str, Any]] = None
    
    execution_errors: Optional[List[Dict[str, Any]]] = None


class AddToCartInput(BaseModel):
    """Schema for adding an item to the shopping cart."""
    
    user_id: str = Field(..., description="Unique identifier of the user adding the item to the cart")
    item_id: str = Field(..., description="Unique identifier of the item to be added to the cart")
    quantity: int = Field(1, gt=0, description="Quantity of the item to add (default is 1)")
    variety : str = Field(None, description="variety of the item to add (default is None)")
    color : str = Field(None, description="color of the item to add (default is None)")
    
    added_at: Optional[datetime] = Field(default_factory=datetime.now, description="Timestamp when the item was added")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="Timestamp when the item was last updated")
    
    @validator("user_id", "item_id")
    def non_empty_string(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v

AVAILABLE_FILTERS = {
    "name": "Product name (string)",
    "category": "Product category (string)",
    "subcategory": "Product subcategory (string)",
    "price": "Price value (number or range)",
    "variety": "variety (string)",
    "color": "Color (string)",
}