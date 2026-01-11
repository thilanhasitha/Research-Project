"""
Sync MongoDB news articles to Weaviate
This will copy all economynext articles from MongoDB to Weaviate for vector search
"""
import asyncio
from app.Database.repositories.rss_repository import RSSRepository
from app.Database.weaviate_client import WeaviateClient
from datetime import datetime

async def sync_mongodb_to_weaviate():
    print("\n" + "="*60)
    print("SYNCING MONGODB TO WEAVIATE")
    print("="*60 + "\n")
    
    try:
        # Connect to MongoDB first
        from app.Database.mongo_client import MongoClient
        mongo_client = MongoClient()
        await mongo_client.connect()
        print(" Connected to MongoDB")
        
        # Connect to both databases
        mongo_repo = RSSRepository()
        weaviate_client = WeaviateClient(collection_name="RSSNews")
        
        if not weaviate_client.is_connected:
            weaviate_client.connect()
        
        print(" Connected to MongoDB and Weaviate\n")
        
        # Get all economynext articles from MongoDB
        print(" Fetching articles from MongoDB...")
        articles = await mongo_repo.get_latest_news(limit=100)  # Get up to 100 latest
        
        print(f"   Found {len(articles)} articles in MongoDB\n")
        
        if not articles:
            print(" No articles found in MongoDB!")
            return
        
        # Sync each article to Weaviate
        print(" Syncing to Weaviate...")
        synced = 0
        skipped = 0
        errors = 0
        
        for article in articles:
            try:
                # Check if already exists in Weaviate (by mongoId)
                mongo_id = article.get("_id")
                
                # Prepare data for Weaviate
                data = {
                    "mongoId": mongo_id,
                    "title": article.get("title", ""),
                    "content": article.get("content", ""),
                    "clean_text": article.get("clean_text", ""),
                    "summary": article.get("summary", ""),
                    "link": article.get("link", ""),
                    "published": article.get("published", datetime.utcnow()),
                    "sentiment": article.get("sentiment", "neutral"),
                    "score": article.get("score", 0.0)
                }
                
                # Add to Weaviate
                weaviate_client.collection.data.insert(properties=data)
                synced += 1
                
                if synced % 5 == 0:
                    print(f"   Synced {synced} articles...")
                    
            except Exception as e:
                errors += 1
                print(f"     Error syncing article '{article.get('title', 'unknown')}': {e}")
        
        print(f"\n Sync complete!")
        print(f"   Synced: {synced}")
        print(f"   Skipped: {skipped}")
        print(f"   Errors: {errors}")
        
        # Verify count
        result = weaviate_client.collection.aggregate.over_all(total_count=True)
        total = result.total_count if hasattr(result, 'total_count') else 0
        print(f"\n Total documents in Weaviate now: {total}")
        
        weaviate_client.close()
        
    except Exception as e:
        print(f"\n ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(sync_mongodb_to_weaviate())
