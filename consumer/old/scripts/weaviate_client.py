import weaviate
from weaviate.classes.config import Property, DataType, Configure
from weaviate.classes.query import Filter
from typing import Dict, Any, List, Optional
import logging

from config import config      # your config.py
from scripts.models import RSSNews  # <<< UPDATED MODEL NAME

logger = logging.getLogger(__name__)

class WeaviateClient:
    """Reusable Weaviate client wrapper for rss_news collection."""

    def __init__(self):
        self.config = config
        self.client = None
        self.collection = None
        self.collection_name = "rss_news"     # collection/table name
        self.vector_dimension = self.config.vector_dim

    # ============================================================
    #  CONNECTION & COLLECTION CREATION
    # ============================================================
    def connect(self):
        """Establish connection & load/create collection."""
        try:
            self.client = weaviate.connect_to_custom(
                http_host=self.config.weaviate_host,
                http_port=self.config.weaviate_http_port,
                http_secure=False,
                grpc_host=self.config.weaviate_host,
                grpc_port=self.config.weaviate_grpc_port,
                grpc_secure=False
            )
            logger.info("Connected to Weaviate")
            self._setup_collection()

        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise

    def _setup_collection(self):
        """Create Weaviate collection dynamically from RSSNews model if not existing."""
        try:
            if not self.client.collections.exists(self.collection_name):
                schema_properties = [
                    Property(name="mongoId", data_type=DataType.TEXT)
                ]

                # Auto-create schema based on Pydantic fields
                for field_name, field_type in RSSNews.model_fields.items():
                    annotation = field_type.annotation
                    if annotation == str:
                        dtype = DataType.TEXT
                    elif annotation == List[str]:
                        dtype = DataType.TEXT_ARRAY
                    elif annotation in [int, float]:
                        dtype = DataType.NUMBER
                    elif annotation == bool:
                        dtype = DataType.BOOL
                    else:
                        dtype = DataType.TEXT

                    schema_properties.append(Property(name=field_name, data_type=dtype))

                # Vector config
                vector_config = Configure.Vectors.self_provided(name="embedding")

                # Create Collection
                self.client.collections.create(
                    name=self.collection_name,
                    properties=schema_properties,
                    vector_config=vector_config
                )
                logger.info(f"Created collection '{self.collection_name}'")
            else:
                logger.info(f"Collection '{self.collection_name}' already exists")

            self.collection = self.client.collections.get(self.collection_name)

        except Exception as e:
            logger.error(f"Error setting up collection: {e}")
            raise

    # ============================================================
    #  CRUD OPERATIONS WITH UPSERT
    # ============================================================
    def insert_item(self, mongo_id: str, rss_news: RSSNews, vector: List[float]) -> bool:
        """Insert with upsert logic using mongoId."""
        try:
            existing_uuid = self._find_by_mongo_id(mongo_id)

            if existing_uuid:
                logger.info(f"Updating existing Weaviate record for Mongo ID: {mongo_id}")
                return self.update_item(mongo_id, rss_news, vector)

            properties = {"mongoId": mongo_id, **rss_news.model_dump()}
            uuid = self.collection.data.insert(properties=properties, vector=vector)
            logger.info(f"Inserted rss_news mongoId={mongo_id}, uuid={uuid}")
            return True

        except Exception as e:
            logger.error(f"Insert failed: {e}")
            return False

    def update_item(self, mongo_id: str, rss_news: RSSNews, vector: List[float]) -> bool:
        """Update Weaviate rss_news item by mongoId."""
        try:
            uuid = self._find_by_mongo_id(mongo_id)
            if not uuid:
                logger.warning(f"Cannot update: mongoId {mongo_id} not found")
                return False

            properties = {"mongoId": mongo_id, **rss_news.model_dump()}
            self.collection.data.update(uuid=uuid, properties=properties, vector=vector)
            logger.info(f"Updated rss_news mongoId={mongo_id}")
            return True

        except Exception as e:
            logger.error(f"Update failed: {e}")
            return False

    def delete_item(self, mongo_id: str) -> bool:
        """Delete rss_news using mongoId."""
        try:
            uuid = self._find_by_mongo_id(mongo_id)
            if not uuid:
                logger.warning(f"Delete skipped: mongoId {mongo_id} not found")
                return False

            self.collection.data.delete_by_id(uuid)
            logger.info(f"Deleted rss_news mongoId={mongo_id}")
            return True

        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False

    # ============================================================
    #  UTILITY FUNCTIONS
    # ============================================================
    def clear_collection(self) -> bool:
        """Delete all records in collection (use for dev only)."""
        try:
            self.collection.data.delete_many(where=None)
            logger.info("Cleared collection")
            return True
        except Exception as e:
            logger.error(f"Clear failed: {e}")
            return False

    def _find_by_mongo_id(self, mongo_id: str) -> Optional[str]:
        """Return UUID matching given mongoId."""
        try:
            result = self.collection.query.fetch_objects(
                filters=Filter.by_property("mongoId").equal(mongo_id),
                limit=1
            )
            if result.objects:
                return str(result.objects[0].uuid)
            return None
        except Exception as e:
            logger.error(f"Find by mongoId failed: {e}")
            return None

    def close(self):
        """Close Weaviate client."""
        if self.client:
            self.client.close()
            logger.info("Weaviate connection closed")
