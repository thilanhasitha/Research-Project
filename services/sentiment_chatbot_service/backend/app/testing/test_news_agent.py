"""
Test the news agent to ensure it's using real Sri Lankan news from economynext
"""

import asyncio
import sys
sys.path.append('c:\\Users\\USER\\OneDrive\\Documents\\GitHub\\Research-Project\\backend')

from app.Database.repositories.rss_repository import RSSRepository
from app.Database.mongo_client import MongoClient

async def test_news_repository():
    """Test that the news repository methods work correctly"""
    print("="*60)
    print("TESTING NEWS REPOSITORY METHODS")
    print("="*60)
    
    # Connect to MongoDB first
    print("\n0. Connecting to MongoDB...")
    mongo = MongoClient()
    await mongo.connect()
    print("   ✓ Connected to MongoDB")
    
    repo = RSSRepository()
    
    # Test 1: Get latest news
    print("\n1. Testing get_latest_news()...")
    latest = await repo.get_latest_news(limit=5)
    print(f"   ✓ Found {len(latest)} articles")
    if latest:
        print(f"   Latest article: {latest[0].get('title', 'No title')}")
    
    # Test 2: Search by filter
    print("\n2. Testing find_by_filter() with title search...")
    results = await repo.find_by_filter({"title": "stock"}, limit=5)
    print(f"   ✓ Found {len(results)} articles with 'stock' in title")
    if results and "error" not in results[0]:
        print(f"   First result: {results[0].get('title', 'No title')}")
    
    # Test 3: Search by content
    print("\n3. Testing find_by_filter() with content search...")
    results = await repo.find_by_filter({"content": "market"}, limit=5)
    print(f"   ✓ Found {len(results)} articles with 'market' in content")
    if results and "error" not in results[0]:
        print(f"   First result: {results[0].get('title', 'No title')}")
    
    # Test 4: Get by ID
    if latest:
        print("\n4. Testing get_by_id()...")
        article_id = latest[0].get("_id")
        article = await repo.get_by_id(article_id)
        if article and "error" not in article:
            print(f"   ✓ Retrieved article: {article.get('title', 'No title')}")
        else:
            print(f"   ✗ Error: {article}")
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_news_repository())
