from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime

class OperationType(str, Enum):
    """MongoDB operation types from Kafka CDC."""
    INSERT = "insert"
    UPDATE = "update"  
    DELETE = "delete"
    REPLACE = "replace"

class RSSNews(BaseModel):
    title: str
    link: str
    content: str
    clean_text: str
    published: datetime = Field(default_factory=datetime.utcnow)
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    score: Optional[float] = None

    
# class Policy(BaseModel):
#     policytype: str
#     policy: str
#     createdBy: Optional[str] = None
#     createdAt: datetime = Field(default_factory=datetime.utcnow)
    

class KafkaMessage(BaseModel):
    """Structure of Kafka CDC message from MongoDB."""
    operationType: OperationType
    documentKey: dict 
    fullDocument: Optional[dict] = None 
    fullDocumentBeforeChange: Optional[dict] = None
    
    def get_mongo_id(self) -> str:
        """
        Extract and normalize MongoDB ID from document key.
        
        Returns:
            Clean MongoDB ObjectId string
        """
        doc_key = self.documentKey.get("_id", "")
        
        if isinstance(doc_key, dict):
            if "$oid" in doc_key:
                return str(doc_key["$oid"])
            return str(doc_key)
        elif isinstance(doc_key, str):
            return doc_key
        else:
            return str(doc_key)
    
    def get_data(self) -> Optional[dict]:
        """Get item data from fullDocument."""
        if self.operationType == OperationType.DELETE:
            return None
        return self.fullDocument