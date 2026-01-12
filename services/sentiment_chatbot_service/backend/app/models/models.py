from pydantic import BaseModel, Field, ConfigDict, field_serializer, validator
from typing import List, Optional, Dict, Any
from datetime import datetime


# ---------- RSSNews MODEL ----------
class RSSNews(BaseModel):
    title: str
    link: str
    content: str
    clean_text: str
    published: datetime = Field(default_factory=datetime.utcnow)

    # AI-Generated Fields (optional during initial creation)
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    score: Optional[float] = None


# # ---------- POLICY MODEL ----------
# class Policy(BaseModel):
#     policytype: str
#     policy: str
#     createdBy: Optional[str] = None
#     createdAt: datetime = Field(default_factory=datetime.utcnow)


# ---------- MESSAGE MODEL ----------
class MessageModel(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    # Serialize datetime in ISO format
    @field_serializer("timestamp")
    def serialize_timestamp(self, value: datetime):
        return value.isoformat()


# ---------- CONVERSATION MODEL ----------
class ConversationModel(BaseModel):
    chat_id: str
    user_id: str
    title: str = "New Conversation"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    messages: List[MessageModel] = Field(default_factory=list)
    agent_state: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at", "updated_at")
    def serialize_dates(self, value: datetime):
        return value.isoformat()

