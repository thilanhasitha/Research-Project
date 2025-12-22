import logging
import sys
import time
from Scripts.kafka_consumer import MultiKafkaConsumer 
from Scripts.message_processor import MessageProcessor
from config import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("./logs/consumer.log")
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application entry point."""
    logger.info("Starting Kafka to Weaviate consumer service")
    logger.info(
        f"Configuration: Kafka={config.kafka_broker}, Topics={config.kafka_topics}, "
        f"Weaviate={config.weaviate_host}:{config.weaviate_http_port}"
    )

    kafka_consumer = MultiKafkaConsumer()
    message_processor = MessageProcessor()

    # Retry connection
    while True:
        try:
            logger.info("Initializing connections...")
            kafka_consumer.connect()
            message_processor.initialize()
            break
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}", exc_info=True)
            logger.info("Retrying initialization in 5 seconds...")
            time.sleep(5)

    logger.info("Starting message processing loop...")
    process_messages(kafka_consumer, message_processor)


def process_messages(consumer: MultiKafkaConsumer, processor: MessageProcessor):
    """Main message processing loop for CDC messages."""
    processed_count = 0
    failed_count = 0
    operation_stats = {"insert": 0, "update": 0, "delete": 0}

    while True:
        try:
            for topic, cdc_message in consumer.consume_messages():
                try:
                    # Process RSS News messages
                    if topic.endswith("rss_news"):
                        success = processor.process_rss_message(cdc_message)
                    else:
                        logger.warning(f"Unhandled topic {topic}, skipping...")
                        success = False

                    # Track success/failure
                    if success:
                        processed_count += 1
                        operation_stats[cdc_message.operationType] = operation_stats.get(cdc_message.operationType, 0) + 1
                        logger.debug(f"Messages processed: {processed_count}")
                    else:
                        failed_count += 1
                        logger.warning(
                            f"Failed to process {cdc_message.operationType} for "
                            f"{cdc_message.get_mongo_id()} from {topic}, total failures: {failed_count}"
                        )
                        time.sleep(config.retry_delay)

                except Exception as e:
                    failed_count += 1
                    logger.error(f"Unexpected error processing message from {topic}: {e}", exc_info=True)
                    time.sleep(config.retry_delay)

                # Log every 10 messages
                if (processed_count + failed_count) % 10 == 0:
                    logger.info(f"Progress: {processed_count} processed, {failed_count} failed")
                    logger.info(f"Operations: {operation_stats}")

        except Exception as e:
            logger.error(f"Error in consumer loop: {e}", exc_info=True)
            logger.info("Restarting message loop after 5s...")
            time.sleep(5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error in service: {e}", exc_info=True)
    finally:
        try:
            logger.info("Cleaning up resources...")
            try:
                MultiKafkaConsumer().close()
            except Exception:
                pass
            try:
                MessageProcessor().close()
            except Exception:
                pass
        finally:
            logger.info("Service stopped")
