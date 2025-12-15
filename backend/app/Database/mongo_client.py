import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

logger = logging.getLogger(__name__)

class MongoClient:
    """Async MongoDB client with singleton behavior."""
    _instance: Optional["MongoClient"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, mongo_uri: str = None, db_name: str = None):
        if hasattr(self, "_initialized") and self._initialized:
            return

        # Get MONGO_URI from environment, default to Docker service name
        self.mongo_uri = mongo_uri or os.getenv("MONGO_URI", "mongodb://research:user@mongo:27017/research_db?authSource=admin&directConnection=true")
        self.db_name = db_name or os.getenv("DB_NAME", "research_db")
        self._client: Optional[AsyncIOMotorClient] = None
        self._db = None
        self._initialized = True
        
        logger.info(f"MongoDB client initialized with URI: {self.mongo_uri.split('@')[1] if '@' in self.mongo_uri else self.mongo_uri}")

    async def connect(self):
        if self._client is None:
            try:
                self._client = AsyncIOMotorClient(self.mongo_uri, serverSelectionTimeoutMS=10000)
                self._db = self._client[self.db_name]
                await self._client.admin.command('ping')
                logger.info(f"✅ Connected to MongoDB successfully")
            except Exception as e:
                logger.error(f"❌ MongoDB connection failed: {e}")
                logger.error(f"URI attempted: {self.mongo_uri.split('@')[1] if '@' in self.mongo_uri else self.mongo_uri}")
                raise

    async def close(self):
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed")

    @property
    def client(self):
        if self._client is None:
            raise RuntimeError("Client not connected. Call connect() first.")
        return self._client

    @property
    def get_db(self):
        if self._db is None:
            raise RuntimeError("Database not connected")
        return self._db