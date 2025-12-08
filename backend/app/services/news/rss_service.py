import feedparser
import re
import asyncio
import json
from datetime import datetime
from app.models.rss_model import RSSNews
from app.Database.repositories.rss_repository import RSSRepository

class RSSService:
    def __init__(self, llm):        
        self.repo = RSSRepository()
        self.llm = llm

   
    # CLEAN TEXT
    # ------------------------------
    def clean_text(self, text: str):
        text = re.sub(r"<.*?>", "", text)          # remove HTML
        text = re.sub(r"\s+", " ", text)           # normalize spaces
        return text.strip()

    
    # FETCH RSS FEED
    # ------------------------------
    async def fetch_feed(self, feed_url: str):
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, feed_url)

        articles = []
        for entry in feed.entries:
            raw_summary = entry.get("summary", "") or entry.get("description", "")
            clean_summary = self.clean_text(raw_summary)

            article = RSSNews(
                title=entry.get("title", ""),
                link=entry.get("link", ""),
                content=raw_summary,
                clean_text=clean_summary,
                published=datetime.utcnow()
            )
            articles.append(article)

        return articles

    # LLM SUMMARY GENERATION
    # ------------------------------
    async def generate_summary(self, text: str):
        if not self.llm:
            return "Summary unavailable: LLM not initialized"

        prompt = f"""
        Summarize the following news article in 2-3 sentences.
        Focus on the main financial or economic insight.
        Return ONLY the summary text.
        Text: {text}
        """

        try:
            summary = await self.llm.generate([prompt])
            return summary.strip()
        except Exception as e:
            return f"Summary error: {str(e)}"

  
    # LLM SENTIMENT ANALYSIS
    # ------------------------------
    async def analyze_sentiment(self, text: str):
        if not self.llm:
            return {"sentiment": "neutral", "score": 0}

        prompt = f"""
        Analyze the sentiment of this financial news.
        Give:
        - sentiment: positive, neutral, or negative
        - score: a number between -1 and 1
        - reason: short explanation

        Return JSON only.

        Text: {text}
        """

        try:
            result = await self.llm.generate([prompt])
            return json.loads(result)
        except Exception as e:
            return {"sentiment": "neutral", "score": 0}

    # ------------------------------
    # PIPELINE EXECUTION
    # ------------------------------
    async def fetch_and_store(self, feed_url: str):
        try:
            articles = await self.fetch_feed(feed_url)
            count = 0

            for article in articles:

                # STEP 1 — Generate Summary
                article.summary = await self.generate_summary(article.clean_text)

                # STEP 2 — Sentiment
                sentiment_data = await self.analyze_sentiment(article.clean_text)
                article.sentiment = sentiment_data.get("sentiment")
                article.score = sentiment_data.get("score")

                # STEP 3 — Save to DB
                self.repo.save_news(article.to_dict())
                count += 1

            return {"status": "success", "count": count}

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    # ------------------------------
    # GET LATEST NEWS
    # ------------------------------
    def get_latest_news(self, limit: int = 10):
        return self.repo.get_latest_news(limit)

