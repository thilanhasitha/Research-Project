from fastapi import APIRouter
from app.services.news.rss_service import RSSService
from app.llm.LLMFactory import LLMFactory
from app.Database.repositories.rss_repository import RSSRepository

router = APIRouter(prefix="/rss", tags=["RSS News"])

RSS_FEEDS = [
    "https://economynext.com/feed/",
    "https://www.ft.lk/feed/",
    "https://www.tradingview.com/markets/stocks-sri-lanka/news/",
]


# COLLECT & PROCESS NEWS WITH LLM
# -----------------------------------------------------
@router.get("/collect")
async def collect_news():
    """
    Fetches RSS feeds, cleans text, generates summary, sentiment,
    and stores them in MongoDB.
    """
    try:
        llm = LLMFactory.get_llm("ollama")    # Get Ollama model instance
        service = RSSService(llm)

        results = []
        for feed_url in RSS_FEEDS:
            response = await service.fetch_and_store(feed_url)
            results.append({
                "feed": feed_url,
                "result": response
            })

        return {
            "status": "success",
            "message": "RSS collection completed",
            "feeds": results
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}



# GET LATEST SAVED NEWS
# -----------------------------------------------------
@router.get("/latest")
def latest_news(limit: int = 20):
    """
    Returns the latest news documents stored in MongoDB.
    No LLM usage required.
    """
    try:
        repo = RSSRepository()
        articles = repo.get_latest_news(limit)
        return {
            "status": "success",
            "count": len(articles),
            "data": articles
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
