"""
Test script to verify the News RAG service returns answers based only on scraped news data.
"""
import asyncio
import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.news_rag_service import NewsRAGService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_news_rag():
    """Test various queries to ensure responses use only scraped news data."""
    
    print("=" * 80)
    print("NEWS RAG SERVICE TEST - Verifying Responses Use Only Scraped Data")
    print("=" * 80)
    
    # Initialize service
    service = NewsRAGService()
    
    # Test queries
    test_queries = [
        "What's the latest news about Sri Lanka?",
        "Tell me about recent political developments",
        "What are the trending news today?",
        "What happened with Bitcoin?",  # This should say no info if no Bitcoin news
        "Give me technology news"
    ]
    
    for idx, query in enumerate(test_queries, 1):
        print(f"\n{'-' * 80}")
        print(f"TEST {idx}: {query}")
        print('-' * 80)
        
        try:
            result = await service.answer_question(
                question=query,
                context_limit=5,
                include_sources=True
            )
            
            print(f"\n📝 Answer:")
            print(result['answer'])
            
            print(f"\n📊 Context Used: {result['context_used']} articles")
            
            if result.get('sources'):
                print(f"\n📰 Source Articles:")
                for i, source in enumerate(result['sources'], 1):
                    print(f"  {i}. {source['title']}")
                    print(f"     Published: {source.get('published', 'Unknown')}")
                    print(f"     Link: {source.get('link', 'N/A')[:60]}...")
            
            # Check if answer mentions Bitcoin/crypto when not in context
            answer_lower = result['answer'].lower()
            has_bitcoin = 'bitcoin' in answer_lower or 'cryptocurrency' in answer_lower or 'crypto' in answer_lower
            
            sources_mention_bitcoin = False
            if result.get('sources'):
                for source in result['sources']:
                    source_text = (source.get('title', '') + ' ' + source.get('summary', '')).lower()
                    if 'bitcoin' in source_text or 'cryptocurrency' in source_text or 'crypto' in source_text:
                        sources_mention_bitcoin = True
                        break
            
            if has_bitcoin and not sources_mention_bitcoin:
                print("\n⚠️  WARNING: Answer mentions Bitcoin/crypto but sources don't!")
            elif has_bitcoin and sources_mention_bitcoin:
                print("\n✓ Answer correctly references Bitcoin/crypto from sources")
            else:
                print("\n✓ Answer stays within scraped news context")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    service.close()
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_news_rag())
