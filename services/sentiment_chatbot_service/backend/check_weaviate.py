"""
Check Weaviate RSSNews collection status
"""
import asyncio
from app.Database.weaviate_client import WeaviateClient

async def check_weaviate():
    print("\n" + "="*60)
    print("CHECKING WEAVIATE STATUS")
    print("="*60 + "\n")
    
    try:
        client = WeaviateClient(collection_name="RSSNews")
        
        if not client.is_connected:
            client.connect()
        
        print(f" Connected to Weaviate")
        print(f"Collection name: {client.collection_name}")
        
        # Check if collection exists
        collection = client.collection
        
        # Get total count
        result = collection.aggregate.over_all(total_count=True)
        total = result.total_count if hasattr(result, 'total_count') else 0
        
        print(f"\n Total documents in RSSNews: {total}")
        
        if total == 0:
            print("\n PROBLEM: RSSNews collection is EMPTY!")
            print("   This is why searches return no results.")
            print("   You need to sync MongoDB data to Weaviate.")
        else:
            print(f"\n Collection has {total} documents")
            
            # Try a simple search
            print("\n Testing search for 'Sri Lanka'...")
            search_result = collection.query.hybrid(
                query="Sri Lanka",
                limit=3
            )
            
            print(f"   Found {len(search_result.objects)} results:")
            for i, obj in enumerate(search_result.objects[:3], 1):
                print(f"   {i}. {obj.properties.get('title', 'No title')}")
        
    except Exception as e:
        print(f" ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(check_weaviate())
