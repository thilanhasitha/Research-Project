import os
from dataclasses import dataclass

@dataclass
class Config:
   # Kafka Configuration
    kafka_broker: str = os.getenv("KAFKA_BROKER", "kafka:9092")
    kafka_topics: str = os.getenv("KAFKA_TOPICS", "research_db.research_db.rss_news")
    kafka_group_id: str = os.getenv("KAFKA_GROUP_ID", "research-consumer-group")
    
    # Weaviate Configuration
    weaviate_host: str = os.getenv("WEAVIATE_HOST", "weaviate")
    weaviate_http_port: int = int(os.getenv("WEAVIATE_HTTP_PORT", "8080"))
    weaviate_grpc_port: int = int(os.getenv("WEAVIATE_GRPC_PORT", "50051"))
    
    # Ollama Configuration (for automatic vectorization)
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "nomic-embed-text")
    
    # Processing Configuration
    retry_delay: int = int(os.getenv("RETRY_DELAY", "1"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))

# Global config instance
config = Config()