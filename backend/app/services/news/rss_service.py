import feedparser
import re
from datetime import datetime
import asyncio
import json
from app.models.rss_model import RSSNews
from app.Database.repositories.rss_repository import RSSRepository

class RSSService:
    def __init__(self, llm):
        self.repo = RSSRepository()
        self.llm = llm

    def clean_text(self, text: str):
        text = re.sub(r"<.*?>", "", text)
        text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
        return text.strip()

    async def fetch_feed(self, feed_url: str):
        # Run synchronous feedparser in a thread
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, feed_url)

        articles = []
        for entry in feed.entries:
            article = RSSNews(
                title=entry.get("title", ""),
                summary=self.clean_text(entry.get("summary", "")),
                link=entry.get("link", ""),
                published=datetime.utcnow()
            )
            articles.append(article)
        return articles

    async def analyze_sentiment(self, text: str):
        if not self.llm:
            return {"sentiment": "neutral", "score": 0, "reason": "LLM not initialized"}

        prompt = f"""
        Analyze the sentiment of this financial news.
        Return JSON: sentiment, score (-1 to 1), and reason.
        Text: {text}
        """
        try:
            sentiment_data = await self.llm.generate(prompt)
            if isinstance(sentiment_data, str):
                sentiment_data = json.loads(sentiment_data)
            return sentiment_data
        except Exception as e:
            return {"sentiment": "neutral", "score": 0, "reason": str(e)}

    async def fetch_and_store(self, feed_url: str):
        try:
            articles = await self.fetch_feed(feed_url)
            count = 0

            for article in articles:
                sentiment_data = await self.analyze_sentiment(article.summary)
                article.sentiment = sentiment_data.get("sentiment")
                article.score = sentiment_data.get("score")

                # Save synchronously if repo is sync
                try:
                    self.repo.save_news(article.dict())
                    count += 1
                except Exception as e:
                    print(f"Failed to save article '{article.title}': {e}")

            return {"status": "success", "count": count}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def get_latest_news(self, limit: int = 10):
        try:
            return self.repo.get_latest_news(limit=limit)  # sync call
        except Exception as e:
            print(f"Error fetching latest news: {e}")
            return []
