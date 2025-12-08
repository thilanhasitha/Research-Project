# weaviate_client.py
import weaviate
from weaviate.classes.config import Property, DataType, Configure
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class WeaviateClient:
    """
    Reusable Weaviate client with:
    - Singleton pattern
    - Safe connection handling
    - Auto-load or create News collection
    - Support for manual embeddings (Ollama)
    """

    _instance: Optional["WeaviateClient"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        collection_name: str = None,
        host: str = "weaviate",
        http_port: int = 8080,
        grpc_port: int = 50051,
        http_secure: bool = False,
        grpc_secure: bool = False,
    ):
        if self._initialized and collection_name and collection_name != self.collection_name:
            logger.info(f"Updating collection from {self.collection_name} to {collection_name}")
            self.collection_name = collection_name
            self._collection = None
            if self._client:
                self._load_collection()
            return
        
        if self._initialized:
            return

        self.collection_name = collection_name
        self.host = host
        self.http_port = http_port
        self.grpc_port = grpc_port
        self.http_secure = http_secure
        self.grpc_secure = grpc_secure

        self._client: Optional[weaviate.WeaviateClient] = None
        self._collection = None
        self._initialized = True

    # ---------- Context Manager ----------
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    # ---------- Connection ----------
    def connect(self):
        """Establish connection to Weaviate and load collection if provided."""
        if self._client is not None:
            return

        try:
            self._client = weaviate.connect_to_custom(
                http_host=self.host,
                http_port=self.http_port,
                http_secure=self.http_secure,
                grpc_host=self.host,
                grpc_port=self.grpc_port,
                grpc_secure=self.grpc_secure,
            )
            logger.info(f"Connected to Weaviate at {self.host}:{self.http_port}")

            if self.collection_name:
                self._load_collection()

        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise

    # ---------- Collection Loader ----------
    def _load_collection(self):
        if not self.collection_name:
            logger.warning("No collection name provided")
            return
        
        try:
            if self._client.collections.exists(self.collection_name):
                self._collection = self._client.collections.get(self.collection_name)
                logger.info(f"Loaded existing collection: {self.collection_name}")
            else:
                logger.warning(
                    f"Collection '{self.collection_name}' does not exist. "
                    f"Call create_collection() or create_news_collection()."
                )
        except Exception as e:
            logger.error(f"Failed to load collection: {e}")
            raise

    # ---------- NEWS COLLECTION CREATION ----------
    def create_news_collection(self):
        """
        Create `News` collection for storing embedded news articles
        with vector support via Ollama embeddings.
        """
        if not self._client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            if self._client.collections.exists("News"):
                self._collection = self._client.collections.get("News")
                logger.info("Loaded existing collection: News")
                return self._collection

            logger.info("Creating Weaviate collection: News")

            self._collection = self._client.collections.create(
                name="News",
                properties=[
                    Property(name="title", data_type=DataType.TEXT),
                    Property(name="content", data_type=DataType.TEXT),
                    Property(name="source", data_type=DataType.TEXT),
                    Property(name="published_at", data_type=DataType.DATE),
                    Property(name="url", data_type=DataType.TEXT),
                ],
                vectorizer_config=Configure.Vectorizer.none()  # using Ollama embeddings
            )

            logger.info("Created collection: News")
            return self._collection

        except Exception as e:
            logger.error(f"Failed to create News collection: {e}")
            raise

    # ---------- Utility ----------
    def list_collections(self) -> List[str]:
        """List all available collections."""
        try:
            collections = self._client.collections.list_all()
            return [col for col in collections.keys()]
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            raise

    def delete_collection(self, name: str):
        """Delete a specific collection."""
        try:
            self._client.collections.delete(name)
            logger.info(f"Deleted collection: {name}")
            if name == self.collection_name:
                self._collection = None
        except Exception as e:
            logger.error(f"Failed to delete collection {name}: {e}")
            raise

    def close(self):
        """Close the Weaviate connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._collection = None
            logger.info("Weaviate connection closed")

    def reset_instance(self):
        """Reset singleton instance (useful for testing only)."""
        self.close()
        WeaviateClient._instance = None
        self._initialized = False

    # ---------- Properties ----------
    @property
    def client(self):
        if self._client is None:
            raise RuntimeError("Client not connected. Call connect() first.")
        return self._client

    @property
    def collection(self):
        if self._collection is None:
            raise RuntimeError(
                f"Collection '{self.collection_name}' not loaded. "
                "Create it using create_news_collection()."
            )
        return self._collection

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    @property
    def has_collection(self) -> bool:
        return self._collection is not None
