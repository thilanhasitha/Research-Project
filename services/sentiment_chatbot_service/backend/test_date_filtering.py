"""
Test script to verify date filtering for "latest news" queries
"""
import asyncio
from datetime import datetime, timedelta
from app.services.news_rag_service import NewsRAGService

async def test_date_filtering():
    print("\n" + "="*70)
    print("TESTING DATE FILTERING FOR 'LATEST NEWS' QUERIES")
    print("="*70 + "\n")
    
    service = NewsRAGService()
    
    # Test cases with different time-related keywords
    test_queries = [
        "What are the latest news today?",
        "Tell me today's headlines",
        "What is the latest news?",
        "Show me recent articles",
        "What happened yesterday?",
        "News from this week",
        "General economy news"  # No time keyword - should search all
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 70)
        
        # Detect what date filter would be applied
        date_filter = service._detect_time_filter(query)
        
        if date_filter:
            print(f"✅ Date filter detected: Articles from {date_filter.strftime('%Y-%m-%d %H:%M:%S')} onwards")
            days_ago = (datetime.utcnow() - date_filter).days
            print(f"   (Filtering last {days_ago} days)")
        else:
            print("❌ No date filter - searching all articles")
        
        # Search with the detected filter
        try:
            results = await service.search_news_by_text(
                query=query,
                limit=3,
                date_from=date_filter
            )
            
            if results:
                print(f"\n   Found {len(results)} articles:")
                for i, article in enumerate(results, 1):
                    pub_date = article.get('published', 'Unknown')
                    if isinstance(pub_date, datetime):
                        pub_date = pub_date.strftime('%Y-%m-%d %H:%M')
                    print(f"   {i}. [{pub_date}] {article['title'][:60]}...")
            else:
                print("   ⚠️  No articles found")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70 + "\n")
    
    service.weaviate_client.close()

if __name__ == "__main__":
    asyncio.run(test_date_filtering())
