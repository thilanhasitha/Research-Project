from Scripts.weaviate_client import WeaviateClient
from Scripts.models import RSSNews, KafkaMessage, OperationType
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MessageProcessor:
    """Process MongoDB CDC messages and sync to Weaviate with automatic vectorization."""
    
    def __init__(self):
        self.weaviate_client = WeaviateClient()

    def initialize(self):
        """Connect to Weaviate and prepare the collection."""
        self.weaviate_client.connect()
        logger.info("MessageProcessor initialized successfully")

    def process_rss_message(self, cdc_message: KafkaMessage) -> bool:
        """Process RSS news CDC message from MongoDB."""
        mongo_id = cdc_message.get_mongo_id()
        
        try:
            # Handle DELETE operation
            if cdc_message.operationType == OperationType.DELETE:
                logger.info(f"Processing DELETE for RSS news ID: {mongo_id}")
                return self.weaviate_client.delete_object("RSSNews", mongo_id)

            # Handle INSERT or UPDATE operations
            raw_doc = cdc_message.get_data()
            if not raw_doc:
                logger.warning(f"No document data for MongoDB ID: {mongo_id}")
                return False

            # Normalize MongoDB dates and convert to Pydantic model
            normalized = self._normalize_mongo_dates(raw_doc)
            rss_news = RSSNews(**normalized)

            # Insert or update in Weaviate (automatic vectorization happens here)
            if cdc_message.operationType == OperationType.INSERT:
                logger.info(f"Processing INSERT for RSS news ID: {mongo_id}")
                # Use upsert pattern: check if exists, update if so, otherwise insert
                if not self.weaviate_client.update_object("RSSNews", mongo_id, rss_news):
                    return self.weaviate_client.insert_object("RSSNews", mongo_id, rss_news)
                return True

            elif cdc_message.operationType in [OperationType.UPDATE, OperationType.REPLACE]:
                logger.info(f"Processing UPDATE for RSS news ID: {mongo_id}")
                return self.weaviate_client.update_object("RSSNews", mongo_id, rss_news)

        except Exception as e:
            logger.error(f"Failed to process RSS CDC message for {mongo_id}: {e}", exc_info=True)
            return False

    @staticmethod
    def _normalize_mongo_dates(doc: dict) -> dict:
        """Normalize MongoDB date formats to Python datetime objects."""
        if not isinstance(doc, dict):
            return doc

        new_doc = {}
        for k, v in doc.items():
            # Handle MongoDB $date format
            if isinstance(v, dict) and "$date" in v:
                date_str = v["$date"]
                try:
                    new_doc[k] = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    logger.warning(f"Could not parse date string: {date_str}")
                    new_doc[k] = datetime.utcnow()
            # Recursively handle nested dicts
            elif isinstance(v, dict):
                new_doc[k] = MessageProcessor._normalize_mongo_dates(v)
            # Recursively handle lists
            elif isinstance(v, list):
                new_doc[k] = [MessageProcessor._normalize_mongo_dates(item) for item in v]
            else:
                new_doc[k] = v
        return new_doc

    def close(self):
        """Clean up resources."""
        self.weaviate_client.close()
        logger.info("MessageProcessor closed")
