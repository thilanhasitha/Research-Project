import feedparser
import re
import asyncio
import json
import time
import html
from datetime import datetime
from urllib.parse import urlparse, urlunparse
from app.models.rss_model import RSSNews
from app.Database.repositories.rss_repository import RSSRepository

class RSSService:
    def __init__(self, llm=None):
        self.repo = RSSRepository()
        self.llm = llm

    # ------------------------------
    # CLEAN TEXT
    # ------------------------------
    def clean_text(self, text: str):
        text = re.sub(r"<.*?>", "", text)  # remove HTML tags
        text = re.sub(r"\s+", " ", text)   # normalize spaces
        return html.unescape(text.strip())  # decode &nbsp; and entities

    # ------------------------------
    # NORMALIZE URL
    # ------------------------------
    def normalize_link(self, link: str):
        parsed = urlparse(link)
        return urlunparse(parsed._replace(query=""))  # remove query parameters

    # ------------------------------
    # FETCH RSS FEED
    # ------------------------------
    async def fetch_feed(self, feed_url: str):
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None,
        lambda: feedparser.parse(feed_url, request_headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NewsBot/1.0",
            "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8"
        })
    )

        articles = []
        for entry in feed.entries:
            published_struct = entry.get("published_parsed") or entry.get("updated_parsed")
            published = datetime.fromtimestamp(time.mktime(published_struct)) if published_struct else datetime.utcnow()

            raw_summary = entry.get("summary", "") or entry.get("description", "")
            clean_summary = self.clean_text(raw_summary)

            article = RSSNews(
                title=entry.get("title", ""),
                link=self.normalize_link(entry.get("link", "")),
                content=raw_summary,
                clean_text=clean_summary,
                published=published
            )
            articles.append(article)

        return articles

    # ------------------------------
    # LLM SUMMARY
    # ------------------------------
    async def generate_summary(self, text: str):
        if not self.llm:
            return "Summary unavailable: LLM not initialized"
        try:
            prompt = f"""
            Summarize the following news article in 2-3 sentences.
            Focus on the main financial or economic insight.
            Return ONLY the summary text.
            Text: {text}
            """
            summary = await self.llm.generate([prompt])
            return summary.strip()
        except Exception as e:
            return f"Summary error: {str(e)}"

    # ------------------------------
    # LLM SENTIMENT
    # ------------------------------
    async def analyze_sentiment(self, text: str):
        if not self.llm:
            return {"sentiment": "neutral", "score": 0}
        try:
            prompt = f"""
            Analyze the sentiment of this financial news.
            Give:
            - sentiment: positive, neutral, or negative
            - score: a number between -1 and 1
            - reason: short explanation
            Return JSON only.
            Text: {text}
            """
            result = await self.llm.generate([prompt])
            return json.loads(result)
        except Exception:
            return {"sentiment": "neutral", "score": 0}

    # ------------------------------
    # FETCH & STORE
    # ------------------------------
    async def fetch_and_store(self, feed_url: str):
        try:
            articles = await self.fetch_feed(feed_url)
            count = 0

            for article in articles:
                if await self.repo.exists(article.link):
                    print(f"Skipped (already exists): {article.title}")
                    continue

                # Generate summary
                article.summary = await self.generate_summary(article.clean_text)

                # Sentiment analysis
                sentiment_data = await self.analyze_sentiment(article.clean_text)
                article.sentiment = sentiment_data.get("sentiment", "neutral")
                article.score = sentiment_data.get("score", 0)

                # Save to DB
                await self.repo.save_news(article.to_dict())
                count += 1

            return {"status": "success", "new_articles": count}

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    # ------------------------------
    # GET LATEST NEWS
    # ------------------------------
    async def get_latest_news(self, limit: int = 10):
        return await self.repo.get_latest_news(limit)
