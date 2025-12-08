import weaviate
import os
from dotenv import load_dotenv

load_dotenv()

class WeaviateClient:
    def __init__(self):
        self.url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.client = weaviate.Client(self.url)

    def insert_news(self, data: dict):
        """Insert a news item into Weaviate"""
        self.client.data_object.create(
            data_object=data,
            class_name="News"
        )

    def search(self, query: str, limit: int = 5):
        """Search news by query using vector similarity"""
        result = self.client.query.get(
            "News",
            ["title", "content", "link", "published", "summary", "sentiment"]
        ).with_near_text({"concepts": [query]}).with_limit(limit).do()
        return result
