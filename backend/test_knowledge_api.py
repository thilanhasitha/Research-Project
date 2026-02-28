"""
Quick API Test for Knowledge Base
==================================
Test the knowledge base API endpoints
"""

import requests
import json
from typing import Dict, Any


class KnowledgeAPITester:
    """Test knowledge base API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/knowledge"
    
    def test_health(self) -> bool:
        """Test health check endpoint"""
        print("\n[1] Testing Health Check...")
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Status: {data.get('status')}")
                print(f"     Model: {data.get('ollama_model')}")
                print(f"     Embedding: {data.get('embedding_model')}")
                print(f"     KB Status: {data.get('knowledge_base_status')}")
                return True
            else:
                print(f"  ❌ Failed: Status code {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Connection failed: {e}")
            print("     Make sure the API server is running:")
            print("     uvicorn app.main:app --reload")
            return False
    
    def test_stats(self) -> bool:
        """Test stats endpoint"""
        print("\n[2] Testing Stats Endpoint...")
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Status: {data.get('status')}")
                print(f"     Total chunks: {data.get('total_chunks', 'N/A')}")
                print(f"     Collection: {data.get('collection_name', 'N/A')}")
                
                if data.get('status') == 'not_initialized':
                    print("  ⚠️  Knowledge base not built yet")
                    print("     Run: python setup_knowledge_base.py")
                    return False
                return True
            else:
                print(f"  ❌ Failed: Status code {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def test_query(self, question: str = "What are the key highlights?") -> bool:
        """Test query endpoint"""
        print("\n[3] Testing Query Endpoint...")
        print(f"  Question: {question}")
        
        try:
            payload = {
                "question": question,
                "n_results": 5,
                "include_sources": True
            }
            
            response = requests.post(
                f"{self.api_url}/query",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('error'):
                    print(f"  ❌ Error in response: {data['error']}")
                    return False
                
                answer = data.get('answer', '')
                confidence = data.get('confidence', 0)
                
                print(f"  ✅ Query successful!")
                print(f"\n  Answer: {answer[:200]}...")
                print(f"\n  Confidence: {confidence:.2f}")
                
                if data.get('sources'):
                    print(f"  Sources: {len(data['sources'])} chunks retrieved")
                
                return True
            else:
                print(f"  ❌ Failed: Status code {response.status_code}")
                print(f"     Response: {response.text[:200]}")
                return False
                
        except requests.exceptions.Timeout:
            print("  ❌ Request timed out (>30s)")
            print("     This might indicate Ollama is slow or not responding")
            return False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def interactive_test(self):
        """Interactive query testing"""
        print("\n" + "="*60)
        print("Interactive Testing Mode")
        print("="*60)
        print("Enter questions (or 'quit' to exit):\n")
        
        while True:
            try:
                question = input("\nYour question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break
                
                if not question:
                    continue
                
                print("\nQuerying...")
                
                payload = {
                    "question": question,
                    "n_results": 5,
                    "include_sources": False
                }
                
                response = requests.post(
                    f"{self.api_url}/query",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"\n{data.get('answer', 'No answer')}")
                    print(f"\n[Confidence: {data.get('confidence', 0):.2f}]")
                else:
                    print(f"\n❌ Error: Status {response.status_code}")
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


def main():
    """Main test function"""
    print("="*60)
    print("Knowledge Base API Test")
    print("="*60)
    
    tester = KnowledgeAPITester()
    
    # Run basic tests
    health_ok = tester.test_health()
    if not health_ok:
        print("\n❌ Cannot connect to API. Exiting.")
        return
    
    stats_ok = tester.test_stats()
    if not stats_ok:
        print("\n⚠️  Knowledge base not ready. Build it first.")
        print("   Run: python setup_knowledge_base.py")
        return
    
    query_ok = tester.test_query()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"  Health Check: {'✅' if health_ok else '❌'}")
    print(f"  Stats: {'✅' if stats_ok else '❌'}")
    print(f"  Query: {'✅' if query_ok else '❌'}")
    
    if health_ok and stats_ok and query_ok:
        print("\n🎉 All tests passed!")
        
        # Offer interactive mode
        print("\n" + "="*60)
        choice = input("\nEnter interactive mode? (y/n): ").strip().lower()
        if choice == 'y':
            tester.interactive_test()
    else:
        print("\n❌ Some tests failed. Check the errors above.")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
