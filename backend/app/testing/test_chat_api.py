"""
Test the chat agent via the API to see if it returns real Sri Lankan news
"""
import requests
import json
import time

# Try the backend directly (port 8001) without /api prefix
API_URL = "http://localhost:8001/news-chat/ask"

def test_news_query(message):
    """Test a chat message"""
    print(f"\n{'='*80}")
    print(f"USER: {message}")
    print(f"{'='*80}")
    
    payload = {
        "message": message,
        "user_id": "test_user_123",
        "conversation_id": None,
        "include_sources": True,
        "context_limit": 5
    }
    
    try:
        print("Sending request...")
        response = requests.post(API_URL, json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        print(f"\n ASSISTANT: {data.get('message', 'No message')}")
        
        sources = data.get('sources', [])
        if sources:
            print(f"\n SOURCES ({len(sources)} articles):")
            for idx, source in enumerate(sources[:3], 1):
                print(f"\n  {idx}. {source.get('title', 'No title')}")
                print(f"     Link: {source.get('link', 'No link')}")
                print(f"     Published: {source.get('published', 'Unknown date')}")
                print(f"     Sentiment: {source.get('sentiment', 'neutral')}")
        else:
            print("\n No sources returned")
        
        print(f"\n✓ Context used: {data.get('context_used', 0)} articles")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"\n ERROR: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"   Details: {error_data}")
            except:
                print(f"   Response: {e.response.text[:200]}")
        return None

def main():
    print("="*80)
    print("TESTING SRI LANKAN NEWS RAG SERVICE")
    print("="*80)
    
    # Wait for backend to be ready
    print("\nWaiting for backend to start...")
    time.sleep(3)
    
    # Test 1: Ask for latest news
    test_news_query("What's the latest news about Sri Lankan stock market?")
    
    time.sleep(2)
    
    # Test 2: Ask about specific topic  
    test_news_query("Tell me about Sri Lankan bonds")
    
    time.sleep(2)
    
    # Test 3: Ask for recent updates
    test_news_query("What happened in Sri Lanka today?")
    
    print("\n" + "="*80)
    print("TESTS COMPLETED")
    print("="*80)

if __name__ == "__main__":
    main()
