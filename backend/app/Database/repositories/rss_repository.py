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
    async def get_latest_news(self, limit: int = 20, date_from: datetime = None):
        self._ensure_collection()
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[RSS_REPO] get_latest_news called with limit={limit}, date_from={date_from}")
        
        # Filter out fake/test articles
        fake_titles = [
            'Bitcoin Surges Past Record High',
            'Breaking News',
            'Tech Innovation',
            'Real-time Test',
            'Innovation in AI'
        ]
        
        # Query: exclude fake articles and sort by published date (most recent first)
        query = {
            "title": {"$nin": fake_titles},
            "link": {"$regex": "economynext.com"}  # Only economynext articles
        }
        
        # Add date filter if provided
        if date_from:
            query["published"] = {"$gte": date_from}
            logger.info(f"[RSS_REPO] Filtering articles published after {date_from}")
        
        logger.info(f"[RSS_REPO] Query: {query}")
        
        cursor = self.collection.find(query).sort("published", -1).limit(limit)
        news_list = []
        async for news in cursor:
            news["_id"] = str(news["_id"])
            news_list.append(news)
        
        logger.info(f"[RSS_REPO] Retrieved {len(news_list)} articles")
        if news_list:
            logger.info(f"[RSS_REPO] First article: {news_list[0].get('title', 'No title')} - {news_list[0].get('published', 'No date')}")
        
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
            # Filter out fake/test articles
            fake_titles = [
                'Bitcoin Surges Past Record High',
                'Breaking News',
                'Tech Innovation',
                'Real-time Test',
                'Innovation in AI'
            ]
            
            # Build query with proper MongoDB syntax
            query = {"$and": []}
            
            # Handle title search
            if "title" in filter_dict:
                title_value = filter_dict.pop("title")
                if isinstance(title_value, str):
                    # Search for title with regex
                    query["$and"].append({"title": {"$regex": title_value, "$options": "i"}})
                elif isinstance(title_value, dict):
                    query["$and"].append({"title": title_value})
            
            # Exclude fake articles
            query["$and"].append({"title": {"$nin": fake_titles}})
            
            # Only economynext articles
            query["$and"].append({"link": {"$regex": "economynext.com"}})
            
            # Handle content search
            if "content" in filter_dict:
                content_value = filter_dict.pop("content")
                if isinstance(content_value, str):
                    query["$and"].append({"content": {"$regex": content_value, "$options": "i"}})
            
            # Add remaining filters
            for key, value in filter_dict.items():
                query["$and"].append({key: value})
            
            # If $and array is empty, use empty query
            final_query = query if query["$and"] else {}
            
            cursor = self.collection.find(final_query).sort("published", -1).limit(limit)
            news_list = []
            async for news in cursor:
                news["_id"] = str(news["_id"])
                news_list.append(news)
            return news_list
        except Exception as e:
            return [{"error": f"Failed to search news: {str(e)}"}]
