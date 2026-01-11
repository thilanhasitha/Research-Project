# import asyncio
# from app.llm.LLMFactory import LLMFactory
# from app.llm.OllamaProvider import OllamaProvider
# from app.services.news.rss_service import RSSService

# # -----------------------------
# # Register Ollama Provider
# # -----------------------------
# # Important: Pass the class, NOT an instance
# LLMFactory.register_provider("ollama", OllamaProvider)

# # -----------------------------
# # Test RSS feed and sentiment
# # -----------------------------
# TEST_FEED = "https://economynext.com/feed/"

# async def test_ollama_rss():
#     print(" Getting Ollama LLM instance...")
#     try:
#         llm = LLMFactory.get_llm("ollama")
#         print(" Ollama LLM instance obtained")
#     except Exception as e:
#         print(" Failed to get Ollama instance:", e)
#         return

#     rss_service = RSSService(llm)

#     # Fetch articles
#     print(f" Fetching RSS feed: {TEST_FEED}")
#     try:
#         articles = await rss_service.fetch_feed(TEST_FEED)
#         print(f" Fetched {len(articles)} articles")
#     except Exception as e:
#         print(" Failed to fetch feed:", e)
#         return

#     if not articles:
#         print(" No articles found in feed.")
#         return

#     # Analyze sentiment of first article
#     sample_text = articles[0].summary
#     print(f" Analyzing sentiment of first article: {sample_text[:60]}...")

#     try:
#         sentiment = await rss_service.analyze_sentiment(sample_text)
#         print(" Sentiment analysis result:", sentiment)
#     except Exception as e:
#         print(" Sentiment analysis failed:", e)

# if __name__ == "__main__":
#     asyncio.run(test_ollama_rss())


import asyncio
from app.llm.LLMFactory import LLMFactory
from app.llm.OllamaProvider import OllamaProvider
from app.services.news.rss_service import RSSService

# -----------------------------
# Register Ollama Provider
# -----------------------------
# Pass the class, not an instance
LLMFactory.register_provider("ollama", OllamaProvider)

# -----------------------------
# Subclass RSSService to skip DB
# -----------------------------
class RSSServiceNoDB(RSSService):
    def __init__(self, llm):
        self.repo = None  # skip repository
        self.llm = llm

    async def fetch_and_store(self, feed_url: str):
        """Fetch feed and analyze sentiment without storing to DB."""
        articles = await self.fetch_feed(feed_url)
        for article in articles:
            sentiment_data = await self.analyze_sentiment(article.summary)
            article.sentiment = sentiment_data.get("sentiment")
            article.score = sentiment_data.get("score")
        return articles

# -----------------------------
# Test RSS feed and sentiment
# -----------------------------
TEST_FEED = "https://economynext.com/feed/"

async def test_ollama_rss():
    print(" Getting Ollama LLM instance...")
    try:
        llm = LLMFactory.get_llm("ollama")
        print(" Ollama LLM instance obtained")
    except Exception as e:
        print(" Failed to get Ollama instance:", e)
        return

    rss_service = RSSServiceNoDB(llm)

    # Fetch articles
    print(f"🔹 Fetching RSS feed: {TEST_FEED}")
    try:
        articles = await rss_service.fetch_and_store(TEST_FEED)
        print(f" Fetched {len(articles)} articles and analyzed sentiment")
    except Exception as e:
        print(" Failed to fetch feed or analyze sentiment:", e)
        return

    if not articles:
        print(" No articles found in feed.")
        return

    # Print sentiment of first article
    first = articles[0]
    print(f"\nFirst article title: {first.title}")
    print(f"Summary: {first.summary[:100]}...")
    print(f"Sentiment: {first.sentiment}, Score: {first.score}")

if __name__ == "__main__":
    asyncio.run(test_ollama_rss())

