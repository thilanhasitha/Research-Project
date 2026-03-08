"""
Test Plot Service Integration
=============================
Quick test to verify plot service endpoints are working
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_health():
    """Test plot service health endpoint."""
    print("Testing plot service health...")
    try:
        response = requests.get(f"{BASE_URL}/api/plots/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Plot service is healthy")
            print(f"  - Total plots: {data.get('total_plots', 0)}")
            print(f"  - Categories: {data.get('categories', [])}")
            print(f"  - Storage: {data.get('storage_mb', 0)} MB")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend. Is it running on port 8001?")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_search():
    """Test plot search functionality."""
    print("\nTesting plot search...")
    queries = [
        "stock price",
        "volume",
        "volatility",
        "correlation"
    ]
    
    for query in queries:
        try:
            response = requests.get(
                f"{BASE_URL}/api/plots/search",
                params={"query": query, "limit": 3},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    count = data.get('count', 0)
                    print(f"✓ Query '{query}': Found {count} plots")
                    for plot in data.get('plots', [])[:2]:
                        print(f"    - {plot['title']} (score: {plot['relevance_score']})")
                else:
                    print(f"✗ Query '{query}': Search failed")
            else:
                print(f"✗ Query '{query}': HTTP {response.status_code}")
                
        except Exception as e:
            print(f"✗ Query '{query}': {e}")

def test_image_access():
    """Test if plot images are accessible."""
    print("\nTesting image access...")
    
    # First search for a plot
    try:
        response = requests.get(
            f"{BASE_URL}/api/plots/search",
            params={"query": "price", "limit": 1},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            plots = data.get('plots', [])
            
            if plots:
                plot_id = plots[0]['plot_id']
                image_url = f"{BASE_URL}/api/plots/{plot_id}/image"
                
                img_response = requests.get(image_url, timeout=5)
                if img_response.status_code == 200:
                    print(f"✓ Image accessible for plot: {plot_id}")
                    print(f"  - Image size: {len(img_response.content)} bytes")
                    return True
                else:
                    print(f"✗ Cannot access image: HTTP {img_response.status_code}")
            else:
                print("⚠ No plots found to test image access")
        
    except Exception as e:
        print(f"✗ Image access test failed: {e}")
    
    return False

def main():
    print("=" * 60)
    print("Plot Service Integration Test")
    print("=" * 60)
    print()
    
    # Test health
    if not test_health():
        print("\n❌ Backend is not running or plot service is not available")
        print("\nTo start the backend:")
        print("  cd services/sentiment_chatbot_service/backend")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8001")
        return
    
    # Test search
    test_search()
    
    # Test image access
    test_image_access()
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nIf plots are missing, run:")
    print("  cd services/sentiment_chatbot_service/backend/lstm_stock_prediction")
    print("  python generate_plots.py")

if __name__ == "__main__":
    main()
