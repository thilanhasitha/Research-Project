import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # load .env variables

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

        self.mongo_uri = mongo_uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = db_name or os.getenv("DB_NAME", "research_db")
        self._client: Optional[AsyncIOMotorClient] = None
        self._db = None
        self._initialized = True

    async def connect(self):
        if self._client is None:
            try:
                 self._client = AsyncIOMotorClient(self.mongo_uri)
                 self._db = self._client[self.db_name]
                 await self._client.admin.command('ping')
                 logger.info(f"Connected to MongoDB at {self.mongo_uri}")

            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
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
