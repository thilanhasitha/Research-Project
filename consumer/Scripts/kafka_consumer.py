import json
from kafka import KafkaConsumer
from typing import Dict, Any, Optional, List, Tuple
from config import config
from Scripts.models import KafkaMessage
import logging

logger = logging.getLogger(__name__)

class MultiKafkaConsumer:
    """Kafka consumer for MongoDB CDC messages from multiple topics."""

    def __init__(self):
        self.config = config
        self.consumer = None

    @staticmethod
    def safe_json_deserializer(x):
        if x is None:
            return None
        return json.loads(x.decode('utf-8'))

    def connect(self):
        """Initialize Kafka consumer subscribed to multiple topics."""
        try:
            topics: List[str] = [t.strip() for t in self.config.kafka_topics.split(",")]

            self.consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=[self.config.kafka_broker],
                group_id=self.config.kafka_group_id,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                auto_commit_interval_ms=5000,
                value_deserializer=MultiKafkaConsumer.safe_json_deserializer,
                consumer_timeout_ms=1000
            )

            logger.info(f"Connected to Kafka topics: {topics}")
            logger.info(f"Consumer group: {self.config.kafka_group_id}")

        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise

    from typing import Generator

    def consume_messages(self) -> Generator[Tuple[str, KafkaMessage], None, None]:
        """
        Generator that yields (topic, KafkaMessage) tuples.
        
        Yields:
            (topic, KafkaMessage) for each consumed message
        """
        if not self.consumer:
            raise RuntimeError("Consumer not initialized. Call connect() first.")

        try:
            logger.info("Starting to consume CDC messages...")

            for message in self.consumer:
                topic = message.topic
                try:
                    raw_data = message.value
                    logger.debug(f"Received raw message from topic={topic}: {raw_data}")

                    if raw_data is None:
                        mongo_id = self._extract_mongo_id_from_key(message.key) if message.key else None
                        if mongo_id:
                            logger.info(f"Tombstone received for MongoDB ID: {mongo_id} on topic {topic}")
                            delete_message = KafkaMessage(
                                operationType="delete",
                                documentKey={"_id": mongo_id},
                                fullDocument=None,
                                fullDocumentBeforeChange=None
                            )
                            yield topic, delete_message
                        else:
                            logger.warning("Tombstone message received but no key found")
                        continue

                    cdc_message = self._parse_cdc_message(raw_data)
                    if cdc_message:
                        logger.info(f"[{topic}] Processing {cdc_message.operationType} for MongoDB ID: {cdc_message.get_mongo_id()}")
                        yield topic, cdc_message
                    else:
                        logger.debug(f"[{topic}] Message skipped (empty or malformed)")

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode JSON message from {topic}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing message from {topic}: {e}")
                    continue

        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
        except Exception as e:
            logger.error(f"Error in message consumption: {e}")
            raise

    
    def _parse_cdc_message(self, raw_data: Dict[str, Any]) -> Optional[KafkaMessage]:
        """
        Parse raw Kafka message into CDC structure.
        
        Args:
            raw_data: Raw message from Kafka
            
        Returns:
            KafkaMessage if valid, None otherwise
        """
        try:
            if "operationType" in raw_data:
                return KafkaMessage(**raw_data)
            elif "op" in raw_data:
                return self._parse_debezium_format(raw_data)
            else:
                logger.warning("Legacy message format detected, treating as insert")
                return KafkaMessage(
                    operationType="insert",
                    documentKey={"_id": raw_data.get("_id", "unknown")},
                    fullDocument=raw_data
                )
                
        except Exception as e:
            logger.error(f"Failed to parse CDC message: {e}")
            return None
    
    def _parse_debezium_format(self, raw_data: Dict[str, Any]) -> Optional[KafkaMessage]:
        """
        Parse Debezium CDC format and handle stringified JSON in 'after'/'before'.
        Works for both payload-wrapped and flattened messages.
        """
        try:
            payload = raw_data.get("payload", raw_data)

            op = payload.get("op")
            op_mapping = {"c": "insert", "u": "update", "d": "delete", "r": "insert"}
            operation_type = op_mapping.get(op, "insert")

            doc_after_raw = payload.get("after")
            doc_before_raw = payload.get("before")
            doc_after = json.loads(doc_after_raw) if isinstance(doc_after_raw, str) else doc_after_raw
            doc_before = json.loads(doc_before_raw) if isinstance(doc_before_raw, str) else doc_before_raw

            if operation_type in ["insert", "update"] and not doc_after:
                logger.warning(f"Insert/Update message missing 'after': {raw_data}")
                return None
            if operation_type == "delete" and not doc_before and not payload.get("source", {}).get("collection"):
                logger.warning(f"Delete message missing 'before' and source info: {raw_data}")
                return None

            if operation_type == "delete":
                if doc_before and doc_before.get("_id"):
                    document_key = {"_id": doc_before["_id"]}
                elif doc_after and doc_after.get("_id"):
                    document_key = {"_id": doc_after["_id"]}
                else:
                    logger.warning(f"Delete message without document data, skipping: {raw_data}")
                    return None
            else:
                document_key = {"_id": (doc_after or doc_before or {}).get("_id")}

            return KafkaMessage(
                operationType=operation_type,
                documentKey=document_key,
                fullDocument=doc_after,
                fullDocumentBeforeChange=doc_before
            )

        except Exception as e:
            logger.error(f"Failed to parse Debezium format: {e}")
            return None
    
    def _extract_mongo_id_from_key(self, key_bytes: bytes) -> Optional[str]:
        """
        Extract MongoDB ObjectId from Kafka message key.
        
        Args:
            key_bytes: Raw key bytes from Kafka message
            
        Returns:
            Clean MongoDB ObjectId string, or None if extraction fails
        """
        try:
            key_str = key_bytes.decode('utf-8')
            logger.debug(f"Raw key: {key_str}")
            
            if key_str.startswith('{"id":'):
                import json
                key_obj = json.loads(key_str)
                id_value = key_obj.get("id", "")
                
                if id_value.startswith('{"$oid"'):
                    oid_obj = json.loads(id_value)
                    return oid_obj.get("$oid")
                else:
                    return id_value
            else:
                return key_str
                
        except Exception as e:
            logger.error(f"Failed to extract MongoDB ID from key: {e}")
            return None
    
    def close(self):
        """Close Kafka consumer."""
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")

