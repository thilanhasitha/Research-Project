from datetime import datetime
from app.Database.mongo_client import MongoClient

class RSSRepository:
    def __init__(self):
        mongo = MongoClient()  # Singleton instance
        try:
            self.db = mongo.get_db
            self.collection = self.db["rss_news"]
        except RuntimeError:
            # DB not connected yet - will be initialized on first use
            self.db = None
            self.collection = None
    
    def _ensure_collection(self):
        """Lazy initialization of collection if not already set."""
        if self.collection is None:
            mongo = MongoClient()
            self.db = mongo.get_db
            self.collection = self.db["rss_news"]

    # ------------------------------
    # SAVE NEWS ASYNC
    # ------------------------------
    async def save_news(self, article: dict):
        self._ensure_collection()
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
        self._ensure_collection()
        doc = await self.collection.find_one({"link": link})
        return doc is not None

    # ------------------------------
    # GET LATEST NEWS ASYNC
    # ------------------------------
    async def get_latest_news(self, limit: int = 20):
        self._ensure_collection()
        cursor = self.collection.find().sort("created_at", -1).limit(limit)
        news_list = []
        async for news in cursor:
            news["_id"] = str(news["_id"])
            news_list.append(news)
        return news_list

    # ------------------------------
    # GET NEWS BY ID
    # ------------------------------
    async def get_by_id(self, item_id: str):
        """Fetch a single news article by its MongoDB _id."""
        self._ensure_collection()
        from bson import ObjectId
        try:
            news = await self.collection.find_one({"_id": ObjectId(item_id)})
            if news:
                news["_id"] = str(news["_id"])
            return news
        except Exception as e:
            return {"error": f"Failed to fetch news: {str(e)}"}

    # ------------------------------
    # FIND NEWS BY FILTER
    # ------------------------------
    async def find_by_filter(self, filter_dict: dict, limit: int = 100):
        """Query MongoDB with a custom filter dictionary."""
        self._ensure_collection()
        try:
            # Handle text search if 'title' or 'content' is in the filter
            if "title" in filter_dict and isinstance(filter_dict["title"], str):
                filter_dict["title"] = {"$regex": filter_dict["title"], "$options": "i"}
            if "content" in filter_dict and isinstance(filter_dict["content"], str):
                filter_dict["content"] = {"$regex": filter_dict["content"], "$options": "i"}
            
            cursor = self.collection.find(filter_dict).sort("created_at", -1).limit(limit)
            news_list = []
            async for news in cursor:
                news["_id"] = str(news["_id"])
                news_list.append(news)
            return news_list
        except Exception as e:
            return [{"error": f"Failed to search news: {str(e)}"}]
