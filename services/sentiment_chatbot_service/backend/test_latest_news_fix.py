"""
Test script to verify latest news functionality is working correctly
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.Database.repositories.rss_repository import RSSRepository
from app.services.news_rag_service import NewsRAGService


async def test_rss_repository():
    """Test 1: Verify RSS repository returns latest news"""
    print("\n" + "="*60)
    print("TEST 1: RSS Repository - get_latest_news()")
    print("="*60)
    
    repo = RSSRepository()
    articles = await repo.get_latest_news(limit=5)
    
    if articles:
        print(f"✅ SUCCESS: Retrieved {len(articles)} articles")
        print(f"\nFirst article:")
        print(f"  Title: {articles[0].get('title')}")
        print(f"  Published: {articles[0].get('published')}")
        print(f"  Link: {articles[0].get('link')}")
        print(f"  Has summary: {bool(articles[0].get('summary'))}")
        print(f"  Sentiment: {articles[0].get('sentiment')}")
        print(f"  Score: {articles[0].get('score')}")
        return True
    else:
        print("❌ FAILED: No articles returned")
        return False


async def test_news_rag_service():
    """Test 2: Verify News RAG service search"""
    print("\n" + "="*60)
    print("TEST 2: News RAG Service - search_news_by_text()")
    print("="*60)
    
    try:
        rag = NewsRAGService()
        
        # Test generic "latest news" query
        print("\nTesting query: 'latest news'")
        results = await rag.search_news_by_text("latest news", limit=5)
        
        if results:
            print(f"✅ SUCCESS: Retrieved {len(results)} articles")
            print(f"\nFirst article:")
            print(f"  Title: {results[0].get('title')}")
            print(f"  Published: {results[0].get('published')}")
            return True
        else:
            print("❌ FAILED: No results returned")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_answer_question():
    """Test 3: Verify RAG answer generation"""
    print("\n" + "="*60)
    print("TEST 3: News RAG Service - answer_question()")
    print("="*60)
    
    try:
        rag = NewsRAGService()
        
        # Test question answering
        print("\nTesting question: 'What are the latest news?'")
        result = await rag.answer_question("What are the latest news?", context_limit=3)
        
        if result and result.get('answer'):
            print(f"✅ SUCCESS: Generated answer")
            print(f"\nAnswer preview: {result['answer'][:200]}...")
            print(f"Context used: {result['context_used']} articles")
            print(f"Has sources: {bool(result.get('sources'))}")
            return True
        else:
            print("❌ FAILED: No answer generated")
            print(f"Result: {result}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("\n" + "="*60)
    print("TESTING LATEST NEWS FUNCTIONALITY")
    print("="*60)
    
    # Run all tests
    test1 = await test_rss_repository()
    test2 = await test_news_rag_service()
    test3 = await test_answer_question()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"RSS Repository: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"News RAG Search: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"Answer Question: {'✅ PASS' if test3 else '❌ FAIL'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 ALL TESTS PASSED! Latest news functionality is working correctly.")
    else:
        print("\n⚠️ SOME TESTS FAILED. Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main())
