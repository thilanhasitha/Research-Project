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
            # Limit text length to avoid token limits and improve speed
            text_sample = text[:1000] if len(text) > 1000 else text
            
            prompt = f"""Summarize this news article in 2-3 clear sentences.
Focus on the main financial or economic points.
Write only the summary, no extra text or labels.

Article:
{text_sample}

Summary:"""
            
            summary = await self.llm.generate([prompt])
            
            # Clean up the response
            summary = summary.strip()
            
            # Remove common prefixes that LLMs might add
            prefixes_to_remove = [
                "Summary:", "Here's the summary:", "Here is the summary:",
                "The summary is:", "Summary of the article:"
            ]
            for prefix in prefixes_to_remove:
                if summary.startswith(prefix):
                    summary = summary[len(prefix):].strip()
            
            # Ensure we have some content
            if not summary or len(summary) < 10:
                return "Unable to generate summary"
            
            return summary
            
        except Exception as e:
            print(f"Summary generation error: {e}")
            return f"Summary error: {str(e)}"

    # ------------------------------
    # LLM SENTIMENT
    # ------------------------------
    async def analyze_sentiment(self, text: str):
        if not self.llm:
            return {"sentiment": "neutral", "score": 0}
        try:
            # Limit text length to avoid token limits
            text_sample = text[:800] if len(text) > 800 else text
            
            prompt = f"""Analyze the sentiment of this financial news.
You MUST respond with ONLY valid JSON, nothing else.

Required format:
{{"sentiment": "positive", "score": 0.8, "reason": "brief explanation"}}

Rules:
- sentiment: must be exactly "positive", "neutral", or "negative"
- score: number between -1.0 (very negative) and 1.0 (very positive)
- reason: one short sentence explaining why

Text to analyze:
{text_sample}

Respond with JSON only:"""

            result = await self.llm.generate([prompt])
            
            # Try to extract JSON from response (in case LLM adds extra text)
            import re
            json_match = re.search(r'\{.*?\}', result, re.DOTALL)
            if json_match:
                result = json_match.group()
            
            parsed = json.loads(result)
            
            # Validate the response structure
            if "sentiment" not in parsed or "score" not in parsed:
                raise ValueError("Missing required fields")
            
            # Ensure sentiment is one of the valid values
            valid_sentiments = ["positive", "neutral", "negative"]
            if parsed["sentiment"] not in valid_sentiments:
                parsed["sentiment"] = "neutral"
            
            # Ensure score is a number
            try:
                parsed["score"] = float(parsed["score"])
            except (ValueError, TypeError):
                parsed["score"] = 0.0
            
            return parsed
            
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return {"sentiment": "neutral", "score": 0, "reason": "Error parsing response"}

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
