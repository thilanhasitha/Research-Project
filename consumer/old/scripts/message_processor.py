import logging
from typing import Dict, Any, Optional, List
from scripts.models import RSSNews, KafkaMessage, OperationType
from scripts.embedding_service import EmbeddingService
from scripts.weaviate_client import WeaviateClient
from config import config

logger = logging.getLogger(__name__)

class MessageProcessor:
    """Processes MongoDB CDC Kafka messages and manages Weaviate vectors for RSS News."""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.weaviate_client = WeaviateClient()
        self.config = config
        
    def initialize(self):
        """Initialize external service connections such as Weaviate."""
        try:
            self.weaviate_client.connect()
            logger.info("Message processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize message processor: {e}")
            raise
    
    def process_cdc_message(self, cdc_message: KafkaMessage) -> bool:
        """
        Process MongoDB CDC message from Kafka for RSS news data.
        
        Args:
            cdc_message: CDC message captured from Kafka
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            mongo_id = cdc_message.get_mongo_id()
            operation = cdc_message.operationType
            logger.info(f"Processing {operation} operation for MongoDB ID: {mongo_id}")
            
            if operation == OperationType.INSERT:
                return self._handle_insert(cdc_message)
            elif operation in (OperationType.UPDATE, OperationType.REPLACE):
                return self._handle_update(cdc_message)
            elif operation == OperationType.DELETE:
                return self._handle_delete(cdc_message)
            else:
                logger.warning(f"Unknown operation type: {operation}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing CDC message: {e}")
            return False
    
    def _handle_insert(self, cdc_message: KafkaMessage) -> bool:
        try:
            mongo_id = cdc_message.get_mongo_id()
            rss_data = cdc_message.get_item_data()

            if not rss_data:
                logger.error(f"No RSS data found for insert: {mongo_id}")
                return False

            rss = self._create_rss_from_data(rss_data)
            if not rss:
                logger.error(f"Failed to create RSSNews model: {mongo_id}")
                return False

            vector = self._generate_embedding(rss)
            if not vector:
                logger.error(f"Failed to generate embedding: {mongo_id}")
                return False

            result = self.weaviate_client.insert_item(mongo_id, rss, vector)

            if result:
                logger.info(f"Successfully inserted RSS news: {mongo_id}")
                return True
            else:
                logger.error(f"Failed to insert RSS news into Weaviate: {mongo_id}")
                return False

        except Exception as e:
            logger.error(f"Error handling insert: {e}")
            return False

    def _handle_update(self, cdc_message: KafkaMessage) -> bool:
        try:
            mongo_id = cdc_message.get_mongo_id()
            rss_data = cdc_message.get_item_data()

            if not rss_data:
                logger.error(f"No RSS data found for update: {mongo_id}")
                return False

            rss = self._create_rss_from_data(rss_data)
            if not rss:
                logger.error(f"Failed to create RSSNews for update: {mongo_id}")
                return False

            vector = self._generate_embedding(rss)
            if not vector:
                logger.error(f"Failed to generate embedding for update: {mongo_id}")
                return False

            success = self.weaviate_client.update_item(mongo_id, rss, vector)

            if success:
                logger.info(f"Successfully updated RSS news: {mongo_id}")
                return True
            else:
                logger.warning(f"RSS news not found for update; inserting instead: {mongo_id}")
                return self.weaviate_client.insert_item(mongo_id, rss, vector)

        except Exception as e:
            logger.error(f"Error handling update: {e}")
            return False

    def _handle_delete(self, cdc_message: KafkaMessage) -> bool:
        try:
            mongo_id = cdc_message.get_mongo_id()
            success = self.weaviate_client.delete_item(mongo_id)
            
            if success:
                logger.info(f"Successfully deleted RSS news: {mongo_id}")
                return True
            else:
                logger.warning(f"RSS news not found for deletion: {mongo_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error handling delete: {e}")
            return False
    
    def _create_rss_from_data(self, data: Dict[str, Any]) -> Optional[RSSNews]:
        """Create RSSNews model from MongoDB document data."""
        try:
            processed_data = {
                "title": data.get("title", "Untitled"),
                "content": data.get("content", ""),
                "link": data.get("link", ""),
                "published": data.get("published"),  # expected datetime
                "source": data.get("source", "Unknown"),
                "category": data.get("category", "General"),
                "tags": self._normalize_list_field(data.get("tags", []))
            }
            rss = RSSNews(**processed_data)
            logger.debug(f"Created RSSNews model: {rss.title}")
            return rss
            
        except Exception as e:
            logger.error(f"Failed to create RSSNews model: {e}")
            logger.debug(f"Raw data: {data}")
            return None
    
    def _normalize_list_field(self, value: Any) -> List[str]:
        """Normalize list field to list of strings."""
        if isinstance(value, list):
            return [str(item) for item in value if item]
        elif isinstance(value, str):
            return [value] if value else []
        else:
            return []
    
    def _generate_embedding(self, rss: RSSNews) -> Optional[List[float]]:
        """Generate embedding from RSS News title + content."""
        try:
            text = f"{rss.title}. {rss.content}"
            return self.embedding_service.get_embedding(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def close(self):
        """Clean up resources."""
        self.weaviate_client.close()
        logger.info("Message processor closed")
