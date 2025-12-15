from datetime import datetime
from app.Database.mongo_client import MongoClient

class RSSRepository:
    def __init__(self):
        mongo = MongoClient()  # Singleton instance
        self.db = mongo.get_db
        self.collection = self.db["rss_news"]

    # ------------------------------
    # SAVE NEWS ASYNC
    # ------------------------------
    async def save_news(self, article: dict):
        article["created_at"] = datetime.utcnow()
        await self.collection.update_one(
            {"link": article["link"]},  # prevent duplicates by link
            {"$set": article},
            upsert=True
        )

    # ------------------------------
    # CHECK IF NEWS EXISTS
    # ------------------------------
    async def exists(self, link: str) -> bool:
        doc = await self.collection.find_one({"link": link})
        return doc is not None

    # ------------------------------
    # GET LATEST NEWS ASYNC
    # ------------------------------
    async def get_latest_news(self, limit: int = 20):
        cursor = self.collection.find().sort("created_at", -1).limit(limit)
        news_list = []
        async for news in cursor:
            news["_id"] = str(news["_id"])
            news_list.append(news)
        return news_list
