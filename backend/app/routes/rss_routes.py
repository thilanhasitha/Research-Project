from fastapi import APIRouter
from app.services.news.rss_service import RSSService
from app.llm.LLMFactory import LLMFactory
from app.Database.repositories.rss_repository import RSSRepository

router = APIRouter(prefix="/rss", tags=["RSS News"])

RSS_FEEDS = [
    "https://economynext.com/feed/",
    "https://www.ft.lk/feed/",
    "https://news.google.com/rss/search?q=stock+market",
]

@router.get("/collect")
async def collect_news():
    try:
        llm = LLMFactory.get_llm("ollama")
        service = RSSService(llm)

        results = []
        for feed in RSS_FEEDS:
            res = await service.fetch_and_store(feed)
            results.append(res)

        return {"message": "RSS collection completed", "feeds": results}

    except Exception as e:
        return {"error": str(e)}


# @router.get("/latest")
# def latest_news(limit: int = 20):
#     """
#     Returns the latest news stored in the database.
#     limit: number of articles to return
#     """
#     try:
#         service = RSSService(llm=None)  # no LLM needed for latest news
#         news = service.get_latest_news(limit=limit)
#         return {"latest_news": news}
#     except Exception as e:
#         return {"error": str(e)}

@router.get("/latest")
def latest_news(limit: int = 20):
    try:
        repo = RSSRepository()
        news = repo.get_latest_news(limit=limit)
        return {"latest_news": news}
    except Exception as e:
        return {"error": str(e)}

