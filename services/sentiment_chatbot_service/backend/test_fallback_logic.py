"""
Test the fallback date filtering logic
"""
import asyncio
from datetime import datetime
from app.services.news_rag_service import NewsRAGService

async def test_fallback():
    print("\n" + "="*70)
    print("TESTING FALLBACK DATE FILTERING")
    print("="*70 + "\n")
    
    service = NewsRAGService()
    
    # Test: Ask for today's news (which might not exist)
    question = "What are the latest news today?"
    print(f" Question: '{question}'")
    print("-" * 70)
    
    try:
        result = await service.answer_question(
            question=question,
            context_limit=5,
            include_sources=True
        )
        
        print(f"\n Response received!")
        print(f" Context used: {result['context_used']} articles")
        print(f" Date range used: {result.get('date_range_used', 'Not specified')}")
        
        if result.get('sources'):
            print(f"\n Source articles:")
            for i, source in enumerate(result['sources'], 1):
                pub_date = source.get('published', 'Unknown')
                if isinstance(pub_date, datetime):
                    pub_date = pub_date.strftime('%Y-%m-%d %H:%M')
                print(f"   {i}. [{pub_date}] {source['title'][:60]}...")
        
        print(f"\n Answer preview:")
        answer_preview = result['answer'][:300] + "..." if len(result['answer']) > 300 else result['answer']
        print(f"   {answer_preview}")
        
        print("\n" + "="*70)
        print("FALLBACK LOGIC EXPLANATION:")
        print("="*70)
        print("""
When user asks for "today's news":
1. First tries: Articles from TODAY (Jan 7, 2026)
2. If none found: Falls back to LAST 7 DAYS
3. If still none: Falls back to LAST 30 DAYS  
4. If still none: Searches ALL ARTICLES
5. User is informed about which date range was used

This ensures users ALWAYS get relevant news, even if today's 
articles haven't been published yet!
        """)
        
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
    
    service.weaviate_client.close()
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(test_fallback())
