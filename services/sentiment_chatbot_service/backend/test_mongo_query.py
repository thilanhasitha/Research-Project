"""
Test MongoDB query to verify news articles are being retrieved
"""
import asyncio
from app.Database.repositories.rss_repository import RSSRepository

async def test_get_latest_news():
    print("\n" + "="*60)
    print("TESTING GET_LATEST_NEWS")
    print("="*60 + "\n")
    
    repo = RSSRepository()
    
    # Test 1: Get latest news
    print(" Fetching latest 5 news articles...")
    news = await repo.get_latest_news(limit=5)
    
    if news and len(news) > 0:
        print(f" SUCCESS: Retrieved {len(news)} articles\n")
        for idx, article in enumerate(news, 1):
            print(f"{idx}. {article.get('title', 'No title')}")
            print(f"   Link: {article.get('link', 'No link')[:50]}...")
            print(f"   Published: {article.get('published', 'No date')}")
            print()
    else:
        print(" FAILED: No articles retrieved")
        print(f"Result: {news}")
    
    # Test 2: Check total count
    total = await repo.collection.count_documents({})
    economynext_count = await repo.collection.count_documents({"link": {"$regex": "economynext.com"}})
    
    print("\n" + "="*60)
    print("DATABASE STATS")
    print("="*60)
    print(f"Total articles in DB: {total}")
    print(f"Economynext articles: {economynext_count}")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_get_latest_news())
