# from scripts.weaviate_client import WeaviateClient
# from scripts.models import RSSNews, KafkaMessage, OperationType
# import logging
# from datetime import datetime

# logger = logging.getLogger(__name__)

# class MessageProcessor:
#     def __init__(self):
#         self.weaviate_client = WeaviateClient()

#     def initialize(self):
#         self.weaviate_client.connect()

#     def process_rss_message(self, cdc_message: KafkaMessage) -> bool:
#         mongo_id = cdc_message.get_mongo_id()
#         try:
#             # If DELETE, remove from vector DB
#             if cdc_message.operationType == OperationType.DELETE:
#                 return self.weaviate_client.delete_object("rss_news", mongo_id)

#             # Otherwise, INSERT or UPDATE
#             raw_doc = cdc_message.get_data()
#             normalized = self._normalize_mongo_dates(raw_doc)

#             # Convert to Pydantic model
#             rss_news = RSSNews(**normalized)

#             if cdc_message.operationType == OperationType.INSERT:
#                 return self.weaviate_client.insert_object("rss_news", mongo_id, rss_news)

#             elif cdc_message.operationType in [OperationType.UPDATE, OperationType.REPLACE]:
#                 return self.weaviate_client.update_object("rss_news", mongo_id, rss_news)

#         except Exception as e:
#             logger.error(f"Failed to process RSS CDC message: {e}", exc_info=True)
#             return False

#     @staticmethod
#     def _normalize_mongo_dates(doc: dict) -> dict:
#         if not isinstance(doc, dict):
#             return doc

#         new_doc = {}
#         for k, v in doc.items():
#             if isinstance(v, dict) and "$date" in v:
#                 date_str = v["$date"]
#                 try:
#                     new_doc[k] = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
#                 except (ValueError, TypeError):
#                     logger.warning(f"Could not parse date string: {date_str}")
#                     new_doc[k] = None
#             elif isinstance(v, dict):
#                 new_doc[k] = MessageProcessor._normalize_mongo_dates(v)
#             elif isinstance(v, list):
#                 new_doc[k] = [MessageProcessor._normalize_mongo_dates(item) for item in v]
#             else:
#                 new_doc[k] = v
#         return new_doc

#     def close(self):
#         self.weaviate_client.close()


# message_processor.py
import logging
from typing import Optional, List, Dict, Any
from scripts.models import RSSNews, KafkaMessage, OperationType
from scripts.weaviate_client import WeaviateClient
from scripts.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class MessageProcessor:
    """End-to-end processor for MongoDB CDC messages with embeddings."""

    def __init__(self):
        self.weaviate_client = WeaviateClient()
        self.embedding_service = EmbeddingService()

    def initialize(self):
        """Connect to Weaviate and prepare the collection."""
        try:
            self.weaviate_client.connect()
            logger.info("MessageProcessor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MessageProcessor: {e}")
            raise

    def process_cdc_message(self, cdc_message: KafkaMessage) -> bool:
        """Process a single MongoDB CDC message."""
        mongo_id = cdc_message.get_mongo_id()
        try:
            # Handle DELETE
            if cdc_message.operationType == OperationType.DELETE:
                return self.weaviate_client.delete_item(mongo_id)

            # Handle INSERT or UPDATE
            raw_doc = cdc_message.get_data()
            if not raw_doc:
                logger.warning(f"No document data for Mongo ID: {mongo_id}")
                return False

            # Convert to RSSNews model
            rss_news = self._create_rss_from_data(raw_doc)
            if not rss_news:
                logger.error(f"Failed to create RSSNews model for {mongo_id}")
                return False

            # Generate embedding
            vector = self._generate_embedding(rss_news)
            if not vector:
                logger.error(f"Failed to generate embedding for {mongo_id}")
                return False

            # Upsert to Weaviate
            if cdc_message.operationType == OperationType.INSERT:
                return self.weaviate_client.insert_item(mongo_id, rss_news, vector)
            elif cdc_message.operationType in [OperationType.UPDATE, OperationType.REPLACE]:
                return self.weaviate_client.update_item(mongo_id, rss_news, vector)

        except Exception as e:
            logger.error(f"Error processing CDC message for {mongo_id}: {e}", exc_info=True)
            return False

    def _create_rss_from_data(self, data: Dict[str, Any]) -> Optional[RSSNews]:
        """Create RSSNews model from MongoDB document."""
        try:
            processed_data = {
                "title": data.get("title", "Untitled"),
                "content": data.get("content", ""),
                "link": data.get("link", ""),
                "clean_text": data.get("clean_text", ""),
                "published": data.get("published"),
                "summary": data.get("summary"),
                "sentiment": data.get("sentiment"),
                "score": data.get("score"),
            }
            return RSSNews(**processed_data)
        except Exception as e:
            logger.error(f"Failed to create RSSNews from data: {e}")
            return None

    def _generate_embedding(self, rss_news: RSSNews) -> Optional[List[float]]:
        """Generate embedding vector for Weaviate."""
        try:
            text = f"{rss_news.title}. {rss_news.content}"
            return self.embedding_service.get_embedding(text)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None

    def close(self):
        """Clean up resources."""
        self.weaviate_client.close()
        logger.info("MessageProcessor closed")
