from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RSSNews(BaseModel):
    title: str
    summary: str
    link: str
    published: Optional[datetime]
    sentiment: Optional[str] = None
    score: Optional[float] = None