import asyncio
import logging
from typing import List, Dict
from app.Database.repositories.rss_repository import RSSRepository

logger = logging.getLogger(__name__)

# Base schema describing each field in RSSNews
BASE_SCHEMA: Dict[str, str] = {
    "title": "News title (string). Not suitable for filtering.",
    "link": "Original article link (string). Not suitable for filtering.",
    "content": "Full content of the article (string).",
    "clean_text": "Cleaned and processed text (string).",
    "published": "Published date (datetime). Useful for date filtering.",
    "summary": "Short AI-generated summary of the article (string).",
    "sentiment": "AI-generated sentiment score (string). Example: positive, negative, neutral.",
    "score": "Numerical AI confidence score (float).",
}


class DynamicSchemaManager:
    """
    Generates a dynamic schema string using the RSSNews MongoDB collection.
    Helps the LLM understand valid fields + valid distinct values.
    """

    def __init__(self, repo: RSSRepository = None):
        self.repo = repo or RSSRepository()
        self._schema_cache: str = None
        self._cache_lock = asyncio.Lock()

    async def _fetch_distinct(self, field: str, limit: int = 50) -> List[str]:
        """
        Fetch distinct values for a given RSSNews field.
        Example: distinct sentiments -> ["positive", "negative", "neutral"]
        """
        pipeline = [
            {"$group": {"_id": f"${field}"}},
            {"$sort": {"_id": 1}},
            {"$limit": limit},
            {"$group": {"_id": None, "values": {"$push": "$_id"}}},
        ]

        try:
            collection = await self.repo._get_collection()
            result = await collection.aggregate(pipeline).to_list(1)

            if result and "values" in result[0]:
                return [v for v in result[0]["values"] if v]

        except Exception as e:
            logger.error(f"Failed to fetch distinct values for '{field}': {e}")

        return []

    async def get_dynamic_schema_string(self) -> str:
        """
        Builds a schema string containing:
        - RSSNews field descriptions
        - Distinct values fetched from MongoDB (sentiment, score ranges, etc.)
        """

        async with self._cache_lock:

            # Return from cache
            if self._schema_cache:
                return self._schema_cache

            logger.info("Building dynamic schema for RSSNews...")

            # Only fields that make sense to fetch dynamically
            fields_to_fetch = {
                "sentiment": self._fetch_distinct("sentiment"),
            }

            # Run all tasks concurrently
            results = await asyncio.gather(*fields_to_fetch.values())
            distinct_values = dict(zip(fields_to_fetch.keys(), results))

            # Construct full schema
            schema_lines = []

            for field, description in BASE_SCHEMA.items():
                line = f"- {field}: {description}"

                # Add dynamic values if exist
                if field in distinct_values and distinct_values[field]:
                    line += f" | Valid values: {distinct_values[field]}"

                schema_lines.append(line)

            schema_string = "\n".join(schema_lines)

            # Cache for later use
            self._schema_cache = schema_string
            logger.info("Dynamic RSS schema built and cached.")

            return schema_string
