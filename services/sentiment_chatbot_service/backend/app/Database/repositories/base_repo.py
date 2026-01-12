from app.Database.mongo_client import MongoClient
import logging

logger = logging.getLogger(__name__)

class BaseRepository:
    """Base repository class with common MongoDB operations."""
    
    def __init__(self, mongo_client: MongoClient = None, collection_name: str = None):
        self.mongo_client = mongo_client or MongoClient()
        self.collection_name = collection_name
        
    async def _ensure_connected(self):
        """Ensure MongoDB client is connected."""
        if self.mongo_client._client is None:
            await self.mongo_client.connect()
    
    async def _get_collection(self):
        """Get the collection for this repository."""
        await self._ensure_connected()
        return self.mongo_client.get_db[self.collection_name]

    async def find_all(self, limit: int = 1000) -> list:
        """Get all documents in the collection with optional limit."""
        collection = await self._get_collection()
        cursor = collection.find().limit(limit)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        return docs






    



