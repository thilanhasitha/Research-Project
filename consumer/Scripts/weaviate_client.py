import weaviate
from weaviate.classes.config import Property, DataType, Configure
from weaviate.classes.query import Filter
from typing import Dict, Any, List, Optional
from config import config
from scripts.models import RSSNews
import logging

logger = logging.getLogger(__name__)

class WeaviateClient:
    """Weaviate client wrapper for managing RSS News collection."""

    def __init__(self):
        self.config = config
        self.client = None
        self.collections = {} 

    def connect(self):
        """Establish connection to Weaviate."""
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

            # Create only RSS News collection
            self._setup_collection("rss_news", RSSNews)

        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise

    def _setup_collection(self, name: str, model_cls):
        """Create Weaviate collection dynamically from RSSNews Pydantic model."""
        try:
            if self.client.collections.exists(name):
                logger.info(f"Collection {name} already exists")
                self.collections[name] = self.client.collections.get(name)
                return

            schema_properties = [
                Property(name="mongoId", data_type=DataType.TEXT)
            ]

            # Map Pydantic fields into Weaviate schema
            for field_name, field_type in model_cls.model_fields.items():
                if field_type.annotation == str:
                    dtype = DataType.TEXT
                elif field_type.annotation == List[str]:
                    dtype = DataType.TEXT_ARRAY
                elif field_type.annotation in [int, float]:
                    dtype = DataType.NUMBER
                elif field_type.annotation == bool:
                    dtype = DataType.BOOL
                else:
                    dtype = DataType.TEXT

                schema_properties.append(
                    Property(name=field_name, data_type=dtype)
                )

            # Enable AI embeddings via Ollama
            vector_config = Configure.Vectors.text2vec_ollama(
                api_endpoint=self.config.ollama_host,
                model=self.config.ollama_model,
                vectorize_collection_name=False
            )

            # Create the collection
            self.client.collections.create(
                name=name,
                properties=schema_properties,
                vector_config=vector_config
            )
            logger.info(f"Created collection '{name}'")

            self.collections[name] = self.client.collections.get(name)

        except Exception as e:
            logger.error(f"Error setting up collection {name}: {e}")
            raise

    def insert_object(self, collection_name: str, mongo_id: str, model_obj) -> bool:
        """Insert RSS news into Weaviate."""
        try:
            collection = self.collections[collection_name]
            properties = {"mongoId": mongo_id, **model_obj.model_dump()}
            collection.data.insert(properties=properties)
            logger.info(f"Inserted RSS news into {collection_name} with ID={mongo_id}")
            return True
        except Exception as e:
            logger.error(f"Insert failed in {collection_name}: {e}")
            return False

    def update_object(self, collection_name: str, mongo_id: str, model_obj) -> bool:
        """Update RSS news in Weaviate."""
        try:
            collection = self.collections[collection_name]
            result = collection.query.fetch_objects(
                filters=Filter.by_property("mongoId").equal(mongo_id),
                limit=1
            )
            if not result.objects:
                logger.warning(f"{collection_name}: no object with mongoId={mongo_id} to update")
                return False

            weaviate_uuid = str(result.objects[0].uuid)
            properties = {"mongoId": mongo_id, **model_obj.model_dump()}
            collection.data.update(uuid=weaviate_uuid, properties=properties)
            logger.info(f"Updated RSS news in {collection_name} with ID={mongo_id}")
            return True
        except Exception as e:
            logger.error(f"Update failed in {collection_name}: {e}")
            return False

    def delete_object(self, collection_name: str, mongo_id: str) -> bool:
        """Delete RSS news from Weaviate."""
        try:
            collection = self.collections[collection_name]
            result = collection.query.fetch_objects(
                filters=Filter.by_property("mongoId").equal(mongo_id),
                limit=1
            )
            if not result.objects:
                logger.warning(f"{collection_name}: no object with mongoId={mongo_id} to delete")
                return False

            weaviate_uuid = str(result.objects[0].uuid)
            collection.data.delete_by_id(weaviate_uuid)
            logger.info(f"Deleted RSS news in {collection_name} with ID={mongo_id}")
            return True
        except Exception as e:
            logger.error(f"Delete failed in {collection_name}: {e}")
            return False
    
    def close(self):
        """Close Weaviate connection."""
        if self.client:
            self.client.close()
            logger.info("Weaviate connection closed")
