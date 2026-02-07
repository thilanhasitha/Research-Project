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
        llm = LLMFactory.get_provider("ollama")    # Get Ollama provider (not just the LLM)
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


# TEST OLLAMA CONNECTION
# -----------------------------------------------------
@router.get("/test-ollama")
async def test_ollama():
    """
    Test endpoint to verify Ollama connectivity and summary generation.
    """
    try:
        llm = LLMFactory.get_provider("ollama")
        
        test_text = """Sri Lanka's economy showed signs of recovery as the central bank 
        maintained interest rates at current levels. Foreign reserves increased by $200 million 
        last month, bringing the total to $3.5 billion. Tourism arrivals also increased by 15% 
        compared to the previous quarter."""
        
        # Test summary generation
        summary = await RSSService(llm).generate_summary(test_text)
        
        # Test sentiment analysis
        sentiment = await RSSService(llm).analyze_sentiment(test_text)
        
        return {
            "status": "success",
            "message": "✓ Ollama connection working!",
            "test_text_length": len(test_text),
            "generated_summary": summary,
            "sentiment_analysis": sentiment
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"✗ Ollama connection failed: {str(e)}",
            "error": str(e)
        }
