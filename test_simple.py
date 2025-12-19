"""
Simple test script for the general responder.
Tests the chat API without needing complex setup.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8001"

def test_api_health():
    """Test if API is responding."""
    print("\n[1] Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✓ SUCCESS: {response.json()['message']}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        print("Make sure to run: docker compose up -d")
        return False

def test_greeting():
    """Test simple greeting (no tools needed)."""
    print("\n[2] Testing simple greeting...")
    try:
        response = requests.post(
            f"{BASE_URL}/chat/message",
            json={"message": "Hello!", "user_id": "test_user"},
            timeout=30
        )
        data = response.json()
        
        if response.status_code == 200:
            print(f"✓ SUCCESS!")
            print(f"  Intent: {data.get('intent')}")
            print(f"  Response: {data.get('response', '')[:200]}")
            return True
        else:
            print(f"✗ FAILED: {data.get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False

def test_news_search():
    """Test news search query."""
    print("\n[3] Testing news search...")
    try:
        response = requests.post(
            f"{BASE_URL}/chat/message",
            json={"message": "Show me recent news", "user_id": "test_user"},
            timeout=30
        )
        data = response.json()
        
        if response.status_code == 200:
            print(f"✓ SUCCESS!")
            print(f"  Intent: {data.get('intent')}")
            print(f"  Used Tools: {data.get('used_tools')}")
            print(f"  Response: {data.get('response', '')[:200]}")
            return True
        else:
            print(f"✗ FAILED: {data.get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Testing General Responder")
    print("="*50)
    
    # Run tests
    results = []
    results.append(test_api_health())
    if results[0]:  # Only continue if API is healthy
        results.append(test_greeting())
        results.append(test_news_search())
    
    # Summary
    print("\n" + "="*50)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("="*50)
    
    print("\nTo view logs: docker logs research_backend --tail 50")
    
    sys.exit(0 if all(results) else 1)
