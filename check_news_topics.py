"""
Quick check of what news is actually stored in Weaviate.
"""
import weaviate
from datetime import datetime

def check_news_content():
    """Check sample news in Weaviate to see what topics are stored."""
    
    try:
        client = weaviate.connect_to_custom(
            http_host="localhost",
            http_port=8080,
            http_secure=False,
            grpc_host="localhost",
            grpc_port=50051,
            grpc_secure=False
        )
        
        if not client.is_ready():
            print("Weaviate is not ready!")
            return
        
        print("=" * 80)
        print("CHECKING NEWS CONTENT IN WEAVIATE")
        print("=" * 80)
        
        collection = client.collections.get("RSSNews")
        
        # Get total count
        response = collection.aggregate.over_all(total_count=True)
        total = response.total_count
        print(f"\n📊 Total Articles: {total}")
        
        # Get recent samples
        print("\n📰 SAMPLE NEWS ARTICLES (Recent 20):")
        print("-" * 80)
        
        results = collection.query.fetch_objects(limit=20)
        
        # Track topics
        topics = {}
        
        for i, obj in enumerate(results.objects, 1):
            title = obj.properties.get('title', 'No title')
            content = obj.properties.get('clean_text', obj.properties.get('content', ''))[:100]
            pub_date = obj.properties.get('published', 'Unknown')
            
            print(f"\n{i}. {title}")
            print(f"   Date: {pub_date}")
            print(f"   Content: {content}...")
            
            # Extract keywords
            title_lower = title.lower()
            if 'bitcoin' in title_lower or 'crypto' in title_lower:
                topics['cryptocurrency'] = topics.get('cryptocurrency', 0) + 1
            if 'sri lanka' in title_lower or 'lanka' in title_lower:
                topics['sri_lanka'] = topics.get('sri_lanka', 0) + 1
            if 'tech' in title_lower or 'technology' in title_lower:
                topics['technology'] = topics.get('technology', 0) + 1
            if 'politic' in title_lower or 'government' in title_lower:
                topics['politics'] = topics.get('politics', 0) + 1
        
        print("\n" + "=" * 80)
        print("TOPIC DISTRIBUTION (in sample):")
        print("=" * 80)
        for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
            print(f"  {topic}: {count} articles")
        
        # Test a search
        print("\n" + "=" * 80)
        print("TEST SEARCH: 'Sri Lanka news'")
        print("=" * 80)
        
        search_results = collection.query.hybrid(
            query="Sri Lanka news",
            limit=5,
            return_metadata=["score"]
        )
        
        print(f"\nFound {len(search_results.objects)} results:")
        for i, obj in enumerate(search_results.objects, 1):
            title = obj.properties.get('title', 'No title')
            score = obj.metadata.score if hasattr(obj.metadata, 'score') else 'N/A'
            print(f"\n{i}. {title}")
            print(f"   Relevance Score: {score}")
        
        client.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_news_content()
