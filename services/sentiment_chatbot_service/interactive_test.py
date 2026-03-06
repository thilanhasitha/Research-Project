"""
Interactive Pipeline Tester
============================
Manually test knowledge base and news queries with progress indicators
"""

import requests
import json
import time
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(70)}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.END}\n")

def print_info(text):
    print(f"{Colors.BLUE}ℹ{Colors.END} {text}")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.END} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.END} {text}")

def print_waiting(text):
    print(f"{Colors.YELLOW}⏳{Colors.END} {text}")

def test_knowledge_base_query():
    """Test knowledge base with a real query"""
    print_header("TESTING KNOWLEDGE BASE QUERY")
    
    question = input(f"{Colors.BOLD}Enter your question (or press Enter for default): {Colors.END}").strip()
    if not question:
        question = "What are the key financial highlights in the CSE Annual Report?"
    
    print_info(f"Question: {question}")
    print_waiting("Sending request to backend... (this may take 15-30 seconds)")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8001/api/knowledge/query",
            json={
                "question": question,
                "n_results": 5,
                "include_sources": True
            },
            timeout=60  # Give it 60 seconds
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('error'):
                print_error(f"Error in response: {data['error']}")
                return False
            
            print_success(f"Query completed in {elapsed:.1f} seconds")
            
            answer = data.get('answer', '')
            confidence = data.get('confidence', 0)
            sources = data.get('sources', [])
            
            print(f"\n{Colors.BOLD}Answer:{Colors.END}")
            print(f"{answer}\n")
            
            print_info(f"Confidence: {confidence:.2f}")
            print_info(f"Sources used: {len(sources)} chunks")
            
            if sources and input("\nShow sources? (y/n): ").lower() == 'y':
                for i, source in enumerate(sources[:3], 1):
                    print(f"\n{Colors.CYAN}Source {i}:{Colors.END}")
                    print(f"  {source.get('text', 'N/A')[:200]}...")
            
            return True
            
        else:
            print_error(f"Request failed with status {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timed out after 60 seconds")
        print_info("This might indicate Ollama is slow. Check logs: docker logs ollama_new")
        return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_news_query():
    """Test news RAG with a real query"""
    print_header("TESTING NEWS RAG QUERY")
    
    message = input(f"{Colors.BOLD}Enter your message (or press Enter for default): {Colors.END}").strip()
    if not message:
        message = "What is the latest news about Sri Lankan stock market?"
    
    print_info(f"Message: {message}")
    print_waiting("Sending request to backend... (this may take 15-30 seconds)")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8001/news-chat/ask",
            json={
                "message": message,
                "use_rag": True
            },
            timeout=60
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('error'):
                print_error(f"Error in response: {data['error']}")
                return False
            
            print_success(f"Query completed in {elapsed:.1f} seconds")
            
            response_text = data.get('response', '')
            sources = data.get('sources', [])
            
            print(f"\n{Colors.BOLD}Response:{Colors.END}")
            print(f"{response_text}\n")
            
            print_info(f"Sources: {len(sources)} articles")
            
            if sources and input("\nShow sources? (y/n): ").lower() == 'y':
                for i, source in enumerate(sources[:3], 1):
                    print(f"\n{Colors.CYAN}Source {i}:{Colors.END}")
                    print(f"  Title: {source.get('title', 'N/A')}")
                    print(f"  URL: {source.get('link', 'N/A')}")
                    if 'summary' in source:
                        print(f"  Summary: {source['summary'][:150]}...")
            
            return True
            
        else:
            print_error(f"Request failed with status {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timed out after 60 seconds")
        print_info("This might indicate Ollama is slow or Weaviate has no data")
        return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def check_knowledge_base_status():
    """Check knowledge base initialization status"""
    print_header("KNOWLEDGE BASE STATUS")
    
    try:
        response = requests.get("http://localhost:8001/api/knowledge/stats", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            
            if status in ['ready', 'active']:
                print_success(f"Knowledge base is {status}")
                print_info(f"Total chunks: {data.get('total_chunks', 'N/A')}")
                print_info(f"Model: {data.get('model', 'N/A')}")
                print_info(f"Embedding model: {data.get('embedding_model', 'N/A')}")
                print_info(f"Collection: {data.get('collection_name', 'N/A')}")
                return True
            elif status == 'not_initialized':
                print_error("Knowledge base is not initialized!")
                print_info("Run: python backend/setup_knowledge_base.py")
                return False
            else:
                print_error(f"Unknown status: {status}")
                return False
        else:
            print_error(f"Failed to get status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Failed to check status: {e}")
        return False

def check_news_rag_status():
    """Check news RAG system status"""
    print_header("NEWS RAG STATUS")
    
    try:
        response = requests.get("http://localhost:8001/news-chat/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            
            if status == 'healthy':
                print_success("News RAG system is healthy")
                if 'database' in data:
                    print_info(f"Database: {data.get('database')}")
                if 'vector_db' in data:
                    print_info(f"Vector DB: {data.get('vector_db')}")
                
                # Check if Weaviate has data
                weav_response = requests.get(
                    "http://localhost:8080/v1/objects?class=RSSNews&limit=1",
                    timeout=5
                )
                if weav_response.status_code == 200:
                    weav_data = weav_response.json()
                    count = weav_data.get('totalResults', 0)
                    print_info(f"News articles in Weaviate: {count}")
                    if count == 0:
                        print_error("No news data! Run: python backend/sync_to_weaviate.py")
                        return False
                
                return True
            else:
                print_error(f"News RAG status: {status}")
                return False
        else:
            print_error(f"Failed to get health: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Failed to check health: {e}")
        return False

def main_menu():
    """Interactive menu"""
    while True:
        print_header("PIPELINE INTERACTIVE TESTER")
        print(f"{Colors.BOLD}Choose a test:{Colors.END}")
        print("1. Check Knowledge Base Status")
        print("2. Test Knowledge Base Query")
        print("3. Check News RAG Status")
        print("4. Test News Query")
        print("5. Run All Checks")
        print("6. Exit")
        
        choice = input(f"\n{Colors.BOLD}Enter choice (1-6): {Colors.END}").strip()
        
        if choice == '1':
            check_knowledge_base_status()
        elif choice == '2':
            if check_knowledge_base_status():
                test_knowledge_base_query()
        elif choice == '3':
            check_news_rag_status()
        elif choice == '4':
            if check_news_rag_status():
                test_news_query()
        elif choice == '5':
            kb_ok = check_knowledge_base_status()
            news_ok = check_news_rag_status()
            
            if kb_ok and input("\nTest knowledge base query? (y/n): ").lower() == 'y':
                test_knowledge_base_query()
            
            if news_ok and input("\nTest news query? (y/n): ").lower() == 'y':
                test_news_query()
        elif choice == '6':
            print("\nGoodbye!")
            break
        else:
            print_error("Invalid choice")
        
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.END}")

if __name__ == "__main__":
    print(f"{Colors.CYAN}Interactive Pipeline Tester{Colors.END}")
    print(f"{Colors.CYAN}Testing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    main_menu()
