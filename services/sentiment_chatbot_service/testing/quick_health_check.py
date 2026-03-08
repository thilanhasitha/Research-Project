"""
Quick Pipeline Health Check
============================
Fast connectivity test for all services (no LLM queries)
"""

import requests
import sys

def check_service(name, url, expected_status=200):
    """Quick check if a service responds"""
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == expected_status:
            print(f"✓ {name}: OK")
            return True
        else:
            print(f"✗ {name}: Status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ {name}: Cannot connect")
        return False
    except Exception as e:
        print(f"✗ {name}: Error - {e}")
        return False

def main():
    print("\n" + "="*50)
    print("QUICK HEALTH CHECK")
    print("="*50 + "\n")
    
    results = []
    
    # Check all services
    results.append(check_service("Backend API", "http://localhost:8001/"))
    results.append(check_service("Frontend", "http://localhost:3001/"))
    results.append(check_service("Ollama", "http://localhost:11434/api/tags"))
    results.append(check_service("Weaviate", "http://localhost:8080/v1/.well-known/ready"))
    results.append(check_service("News RAG Health", "http://localhost:8001/news-chat/health"))
    results.append(check_service("Knowledge Base Stats", "http://localhost:8001/api/knowledge/stats"))
    
    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"  ✓ ALL SERVICES UP ({passed}/{total})")
        print("  Ready to test queries!")
    else:
        print(f"  ⚠ {passed}/{total} services responding")
    print("="*50 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
