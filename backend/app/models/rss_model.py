from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


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

    def to_dict(self):
        return self.model_dump()
