from datetime import datetime
from app.Database.mongo_client import MongoClient
# from motor.motor_asyncio import AsyncIOMotorClient

class RSSRepository:
    def __init__(self):
        mongo = MongoClient()  # Singleton instance
        self.db = mongo.get_db
        self.collection = self.db["rss_news"]

    def save_news(self, article: dict):
        article["created_at"] = datetime.utcnow()
        self.collection.update_one(
            {"link": article["link"]},
            {"$set": article},
            upsert=True
        )

    def get_latest_news(self, limit: int = 20):
        cursor = self.collection.find().sort("created_at", -1).limit(limit)
        news_list = []
        for news in cursor:
            news["_id"] = str(news["_id"])  # ObjectId is not JSON serializable
            news_list.append(news)
        return news_list