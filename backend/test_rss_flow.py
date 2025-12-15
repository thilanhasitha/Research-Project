"""
Complete test for RSS news collection with summary and sentiment analysis
Run this to verify your setup is working correctly
"""
import asyncio
import sys
from app.Database.mongo_client import MongoClient
from app.llm.LLMFactory import LLMFactory
from app.llm.client.ollama_client import OllamaClient
from app.services.news.rss_service import RSSService

# Register Ollama provider
LLMFactory.register_provider("ollama", OllamaClient)

async def test_complete_flow():
    print("="*60)
    print("🧪 Testing RSS News Collection with LLM Processing")
    print("="*60)
    
    # Step 1: Test MongoDB connection
    print("\n1️⃣  Testing MongoDB Connection...")
    try:
        mongo = MongoClient()
        await mongo.connect()
        print("✅ MongoDB connected successfully!")
        db = mongo.get_db
        collection = db["rss_news"]
        count = await collection.count_documents({})
        print(f"   Current documents in rss_news: {count}")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("   Fix: Check MONGO_URI in .env file")
        return
    
    # Step 2: Test Ollama LLM
    print("\n2️⃣  Testing Ollama LLM...")
    try:
        llm = LLMFactory.get_llm("ollama")
        provider = LLMFactory.get_provider("ollama")
        
        print(f"   Model: {provider._default_model}")
        print(f"   Host: {provider._ollama_host}")
        
        test_response = await provider.generate("Say 'Hello' in one word")
        print(f"✅ Ollama is working! Response: {test_response[:50]}...")
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        print("   Fix: Ensure Ollama container is running and model is pulled")
        print("   Run: docker exec ollama_new ollama pull llama3.2")
        return
    
    # Step 3: Test RSS fetching
    print("\n3️⃣  Testing RSS Feed Fetching...")
    try:
        service = RSSService(llm)
        test_feed = "https://economynext.com/feed/"
        
        print(f"   Fetching from: {test_feed}")
        articles = await service.fetch_feed(test_feed)
        
        if not articles:
            print("⚠️  No articles found in feed")
            return
        
        print(f"✅ Found {len(articles)} articles")
        
        # Show first article
        first = articles[0]
        print(f"\n   Sample Article:")
        print(f"   Title: {first.title[:60]}...")
        print(f"   Link: {first.link[:60]}...")
        print(f"   Text length: {len(first.clean_text)} chars")
        
    except Exception as e:
        print(f"❌ RSS fetching failed: {e}")
        return
    
    # Step 4: Test Summary Generation
    print("\n4️⃣  Testing Summary Generation...")
    try:
        sample_text = first.clean_text[:500]  # Use first 500 chars
        print(f"   Input text: {sample_text[:100]}...")
        
        summary = await service.generate_summary(sample_text)
        print(f"✅ Summary generated successfully!")
        print(f"   Summary: {summary}")
        
    except Exception as e:
        print(f"❌ Summary generation failed: {e}")
        return
    
    # Step 5: Test Sentiment Analysis
    print("\n5️⃣  Testing Sentiment Analysis...")
    try:
        sentiment_data = await service.analyze_sentiment(sample_text)
        print(f"✅ Sentiment analysis completed!")
        print(f"   Sentiment: {sentiment_data.get('sentiment', 'N/A')}")
        print(f"   Score: {sentiment_data.get('score', 'N/A')}")
        print(f"   Reason: {sentiment_data.get('reason', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Sentiment analysis failed: {e}")
        return
    
    # Step 6: Test Complete Flow (Fetch and Store)
    print("\n6️⃣  Testing Complete Flow (Limited to 2 articles)...")
    try:
        # Temporarily limit articles for testing
        original_fetch = service.fetch_feed
        
        async def limited_fetch(feed_url):
            articles = await original_fetch(feed_url)
            return articles[:2]  # Only process 2 articles for testing
        
        service.fetch_feed = limited_fetch
        
        result = await service.fetch_and_store(test_feed)
        
        print(f"✅ Complete flow executed!")
        print(f"   Status: {result.get('status')}")
        print(f"   New articles saved: {result.get('new_articles', 0)}")
        
        # Verify in database
        new_count = await collection.count_documents({})
        print(f"   Total documents in DB now: {new_count}")
        
        # Show one saved document
        sample_doc = await collection.find_one({"summary": {"$exists": True}})
        if sample_doc:
            print(f"\n   Sample Saved Document:")
            print(f"   Title: {sample_doc.get('title', 'N/A')[:60]}...")
            print(f"   Summary: {sample_doc.get('summary', 'N/A')[:100]}...")
            print(f"   Sentiment: {sample_doc.get('sentiment', 'N/A')}")
            print(f"   Score: {sample_doc.get('score', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Complete flow failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Cleanup
    await mongo.close()
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED! Your system is working correctly!")
    print("="*60)
    print("\n📝 Next Steps:")
    print("   1. Call GET http://localhost:8001/rss/collect to process all feeds")
    print("   2. Call GET http://localhost:8001/rss/latest to view stored news")
    print("   3. Check MongoDB to see stored documents with summaries")
    print("")

if __name__ == "__main__":
    try:
        asyncio.run(test_complete_flow())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
