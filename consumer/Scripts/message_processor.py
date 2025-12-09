from scripts.weaviate_client import WeaviateClient
from scripts.models import RSSNews, KafkaMessage, OperationType
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MessageProcessor:
    def __init__(self):
        self.weaviate_client = WeaviateClient()

    def initialize(self):
        self.weaviate_client.connect()

    def process_rss_message(self, cdc_message: KafkaMessage) -> bool:
        mongo_id = cdc_message.get_mongo_id()
        try:
            # If DELETE, remove from vector DB
            if cdc_message.operationType == OperationType.DELETE:
                return self.weaviate_client.delete_object("rss_news", mongo_id)

            # Otherwise, INSERT or UPDATE
            raw_doc = cdc_message.get_data()
            normalized = self._normalize_mongo_dates(raw_doc)

            # Convert to Pydantic model
            rss_news = RSSNews(**normalized)

            if cdc_message.operationType == OperationType.INSERT:
                return self.weaviate_client.insert_object("rss_news", mongo_id, rss_news)

            elif cdc_message.operationType in [OperationType.UPDATE, OperationType.REPLACE]:
                return self.weaviate_client.update_object("rss_news", mongo_id, rss_news)

        except Exception as e:
            logger.error(f"Failed to process RSS CDC message: {e}", exc_info=True)
            return False

    @staticmethod
    def _normalize_mongo_dates(doc: dict) -> dict:
        if not isinstance(doc, dict):
            return doc

        new_doc = {}
        for k, v in doc.items():
            if isinstance(v, dict) and "$date" in v:
                date_str = v["$date"]
                try:
                    new_doc[k] = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    logger.warning(f"Could not parse date string: {date_str}")
                    new_doc[k] = None
            elif isinstance(v, dict):
                new_doc[k] = MessageProcessor._normalize_mongo_dates(v)
            elif isinstance(v, list):
                new_doc[k] = [MessageProcessor._normalize_mongo_dates(item) for item in v]
            else:
                new_doc[k] = v
        return new_doc

    def close(self):
        self.weaviate_client.close()
