import requests
from typing import Optional, List
from config import config
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings using Ollama."""

    def __init__(self):
        self.host = config.ollama_host.rstrip("/")  # ensure no trailing slash
        self.model = config.ollama_model

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for the given text using Ollama API.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            List of floats representing the embedding, or None if failed
        """
        if not text.strip():
            logger.warning("Empty text provided for embedding")
            return None

        try:
            response = self._call_ollama_api(text)

            if response is None:
                return None

            # Ollama v0.9.3 embedding response
            # {
            #   "object": "list",
            #   "data": [{"object": "embedding", "embedding": [...], "index": 0}],
            #   "model": "nomic-embed-text",
            #   "usage": {...}
            # }
            if "embeddings" in response and len(response["embeddings"]) > 0:
                embedding = response["embeddings"][0]
                logger.debug(f"Embedding: {embedding}")
                logger.debug(f"Embedding length: {len(embedding)}")
                return embedding

            logger.error(f"Unexpected embedding response format: {response}")
            return None

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def _call_ollama_api(self, text: str) -> Optional[dict]:
        """
        Call Ollama API.
        
        Args:
            text: Text to process
            
        Returns:
            API response as dict, or None if request fails
        """
        url = f"{self.host}/api/embed"
        payload = {
            "model": self.model,
            "input": text
        }

        try:
            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                return response.json()

            logger.warning(f"Ollama API returned {response.status_code}: {response.text}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for Ollama embeddings API: {e}")
            return None
