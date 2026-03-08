"""
Full Pipeline End-to-End Test
===============================
Test the complete pipeline: Frontend -> Backend -> Ollama -> ChromaDB/Weaviate

This test verifies:
1. All services are running (backend, ollama, weaviate, chromadb)
2. Knowledge base is initialized and queryable
3. News RAG system is working
4. Frontend API endpoints respond correctly
5. Ollama models are loaded and functional

Usage:
    python test_full_pipeline.py
"""

import requests
import time
import json
from typing import Dict, List, Optional
from datetime import datetime


class Colors:
    """Terminal colors for pretty output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


class PipelineTester:
    """End-to-end pipeline tester"""
    
    def __init__(self, backend_url: str = "http://localhost:8001"):
        self.backend_url = backend_url
        self.results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'tests': []
        }
    
    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")
    
    def print_test(self, name: str):
        """Print test name"""
        print(f"{Colors.BOLD}{Colors.WHITE}[TEST] {name}{Colors.END}")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"  {Colors.GREEN}✓{Colors.END} {message}")
        self.results['passed'] += 1
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"  {Colors.RED}✗{Colors.END} {message}")
        self.results['failed'] += 1
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"  {Colors.YELLOW}⚠{Colors.END} {message}")
        self.results['warnings'] += 1
    
    def print_info(self, message: str, indent: int = 2):
        """Print info message"""
        print(" " * indent + f"{Colors.BLUE}ℹ{Colors.END} {message}")
    
    def test_backend_health(self) -> bool:
        """Test if backend is running and healthy"""
        self.print_test("Backend Health Check")
        try:
            # Try root endpoint first
            response = requests.get(f"{self.backend_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Backend is running")
                self.print_info(f"Message: {data.get('message', 'N/A')}")
                self.print_info(f"Version: {data.get('version', 'N/A')}")
                return True
            else:
                self.print_error(f"Backend returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.print_error("Cannot connect to backend. Is it running?")
            self.print_info("Start with: docker compose up -d", indent=4)
            return False
        except Exception as e:
            self.print_error(f"Unexpected error: {e}")
            return False
    
    def test_ollama_connection(self) -> bool:
        """Test Ollama service"""
        self.print_test("Ollama Service Check")
        try:
            # Try backend's ollama endpoint
            response = requests.get(f"{self.backend_url}/api/ollama/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.print_success("Ollama is accessible")
                self.print_info(f"Status: {data.get('status', 'unknown')}")
                if 'models' in data:
                    self.print_info(f"Available models: {', '.join(data['models'])}")
                return True
            else:
                self.print_warning("Ollama health check endpoint not found")
                # Try direct connection
                return self._test_ollama_direct()
        except Exception as e:
            self.print_warning(f"Backend Ollama check failed: {e}")
            return self._test_ollama_direct()
    
    def _test_ollama_direct(self) -> bool:
        """Test Ollama directly"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [m.get('name', '') for m in data.get('models', [])]
                self.print_success("Ollama is running (direct connection)")
                self.print_info(f"Models: {', '.join(models)}")
                return True
            else:
                self.print_error("Ollama not responding correctly")
                return False
        except:
            self.print_error("Cannot connect to Ollama on port 11434")
            return False
    
    def test_weaviate_connection(self) -> bool:
        """Test Weaviate service"""
        self.print_test("Weaviate Service Check")
        try:
            response = requests.get("http://localhost:8080/v1/.well-known/ready", timeout=5)
            if response.status_code == 200:
                self.print_success("Weaviate is running")
                # Get meta info
                meta_response = requests.get("http://localhost:8080/v1/meta", timeout=5)
                if meta_response.status_code == 200:
                    meta = meta_response.json()
                    self.print_info(f"Version: {meta.get('version', 'unknown')}")
                return True
            else:
                self.print_error(f"Weaviate returned status {response.status_code}")
                return False
        except:
            self.print_error("Cannot connect to Weaviate on port 8080")
            return False
    
    def test_knowledge_base_status(self) -> Dict:
        """Test knowledge base service"""
        self.print_test("Knowledge Base Status")
        try:
            response = requests.get(
                f"{self.backend_url}/api/knowledge/stats",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                
                if status == 'ready':
                    self.print_success("Knowledge base is initialized")
                    self.print_info(f"Total chunks: {data.get('total_chunks', 'N/A')}")
                    self.print_info(f"Model: {data.get('model', 'N/A')}")
                    self.print_info(f"Embedding model: {data.get('embedding_model', 'N/A')}")
                    return data
                elif status == 'not_initialized':
                    self.print_warning("Knowledge base not initialized")
                    self.print_info("Run: python backend/setup_knowledge_base.py", indent=4)
                    return data
                else:
                    self.print_warning(f"Knowledge base status: {status}")
                    return data
            else:
                self.print_error(f"Stats endpoint returned {response.status_code}")
                return {}
        except Exception as e:
            self.print_error(f"Failed to get knowledge base stats: {e}")
            return {}
    
    def test_knowledge_base_query(self) -> bool:
        """Test knowledge base query"""
        self.print_test("Knowledge Base Query Test")
        
        test_question = "What are the key financial highlights?"
        self.print_info(f"Question: {test_question}")
        
        try:
            response = requests.post(
                f"{self.backend_url}/api/knowledge/query",
                json={
                    "question": test_question,
                    "n_results": 3,
                    "include_sources": True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('error'):
                    self.print_error(f"Query returned error: {data['error']}")
                    return False
                
                answer = data.get('answer', '')
                confidence = data.get('confidence', 0)
                
                self.print_success("Query executed successfully")
                self.print_info(f"Confidence: {confidence:.2f}")
                self.print_info(f"Answer length: {len(answer)} chars")
                
                if len(answer) > 50:
                    self.print_info(f"Answer preview: {answer[:100]}...", indent=4)
                else:
                    self.print_info(f"Answer: {answer}", indent=4)
                
                if data.get('sources'):
                    self.print_info(f"Retrieved {len(data['sources'])} source chunks")
                
                return True
            else:
                self.print_error(f"Query failed with status {response.status_code}")
                if response.text:
                    self.print_info(f"Error: {response.text[:200]}", indent=4)
                return False
                
        except requests.exceptions.Timeout:
            self.print_error("Query timed out (>30s)")
            self.print_info("This might indicate Ollama is slow or not responding", indent=4)
            return False
        except Exception as e:
            self.print_error(f"Query failed: {e}")
            return False
    
    def test_news_rag_health(self) -> bool:
        """Test News RAG system health"""
        self.print_test("News RAG System Check")
        try:
            # Try the responder health endpoint
            response = requests.get(
                f"{self.backend_url}/news-chat/health",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_success("News RAG system is online")
                self.print_info(f"Status: {data.get('status', 'unknown')}")
                if 'database' in data:
                    self.print_info(f"Database: {data.get('database', 'N/A')}")
                if 'vector_db' in data:
                    self.print_info(f"Vector DB: {data.get('vector_db', 'N/A')}")
                return True
            elif response.status_code == 404:
                self.print_warning("News RAG health endpoint not found")
                return self._test_news_rag_alternate()
            else:
                self.print_error(f"News RAG returned status {response.status_code}")
                return False
        except Exception as e:
            self.print_warning(f"News RAG health check failed: {e}")
            return self._test_news_rag_alternate()
    
    def _test_news_rag_alternate(self) -> bool:
        """Alternate test for news RAG"""
        try:
            # Just check if Weaviate has news data
            response = requests.get(
                "http://localhost:8080/v1/objects?class=RSSNews&limit=1",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                total = data.get('totalResults', 0)
                if total > 0:
                    self.print_success(f"News data available ({total} items)")
                    return True
                else:
                    self.print_warning("No news data in Weaviate")
                    self.print_info("Run sync script to populate news", indent=4)
                    return False
            return False
        except:
            self.print_error("Cannot verify news data")
            return False
    
    def test_news_query(self) -> bool:
        """Test news query functionality"""
        self.print_test("News Query Test")
        
        test_query = "What is the latest news about Sri Lankan stock market?"
        self.print_info(f"Query: {test_query}")
        
        try:
            response = requests.post(
                f"{self.backend_url}/news-chat/ask",
                json={
                    "message": test_query,
                    "use_rag": True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('error'):
                    self.print_error(f"News query error: {data['error']}")
                    return False
                
                response_text = data.get('response', '')
                sources = data.get('sources', [])
                
                self.print_success("News query executed")
                self.print_info(f"Response length: {len(response_text)} chars")
                self.print_info(f"Sources: {len(sources)} items")
                
                if len(response_text) > 50:
                    self.print_info(f"Response preview: {response_text[:100]}...", indent=4)
                
                return True
            else:
                self.print_error(f"News query failed with status {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            self.print_error("News query timed out")
            return False
        except Exception as e:
            self.print_error(f"News query failed: {e}")
            return False
    
    def test_quick_actions(self) -> Dict:
        """Test frontend quick actions"""
        self.print_test("Quick Actions Compatibility")
        
        actions_tested = {
            'knowledge_base': [],
            'news_rag': []
        }
        
        # Knowledge base actions
        kb_actions = [
            ('cse_highlights', 'What are the CSE report highlights?'),
            ('financial_overview', 'Provide a financial overview from the CSE report'),
        ]
        
        self.print_info("Testing Knowledge Base actions...")
        for action, question in kb_actions:
            try:
                response = requests.post(
                    f"{self.backend_url}/api/knowledge/query",
                    json={"question": question, "n_results": 3},
                    timeout=20
                )
                if response.status_code == 200:
                    actions_tested['knowledge_base'].append((action, True))
                    self.print_info(f"  ✓ {action}", indent=4)
                else:
                    actions_tested['knowledge_base'].append((action, False))
                    self.print_info(f"  ✗ {action}", indent=4)
            except:
                actions_tested['knowledge_base'].append((action, False))
                self.print_info(f"  ✗ {action}", indent=4)
        
        # News RAG actions
        news_actions = [
            ('latest_news', 'What is the latest news?'),
            ('market_trends', 'What are the current market trends?'),
        ]
        
        self.print_info("Testing News RAG actions...")
        for action, query in news_actions:
            try:
                response = requests.post(
                    f"{self.backend_url}/news-chat/ask",
                    json={"message": query, "use_rag": True},
                    timeout=20
                )
                if response.status_code == 200:
                    actions_tested['news_rag'].append((action, True))
                    self.print_info(f"  ✓ {action}", indent=4)
                else:
                    actions_tested['news_rag'].append((action, False))
                    self.print_info(f"  ✗ {action}", indent=4)
            except:
                actions_tested['news_rag'].append((action, False))
                self.print_info(f"  ✗ {action}", indent=4)
        
        kb_success = sum(1 for _, result in actions_tested['knowledge_base'] if result)
        news_success = sum(1 for _, result in actions_tested['news_rag'] if result)
        
        if kb_success > 0 and news_success > 0:
            self.print_success(f"Quick actions working ({kb_success} KB, {news_success} News)")
        elif kb_success > 0 or news_success > 0:
            self.print_warning(f"Partial functionality ({kb_success} KB, {news_success} News)")
        else:
            self.print_error("No quick actions working")
        
        return actions_tested
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        total = self.results['passed'] + self.results['failed']
        
        print(f"{Colors.GREEN}  Passed:   {self.results['passed']}/{total}{Colors.END}")
        print(f"{Colors.RED}  Failed:   {self.results['failed']}/{total}{Colors.END}")
        print(f"{Colors.YELLOW}  Warnings: {self.results['warnings']}{Colors.END}")
        
        if self.results['failed'] == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}  ✓ ALL SYSTEMS OPERATIONAL{Colors.END}")
            print(f"\n{Colors.WHITE}  Your pipeline is ready to use!{Colors.END}")
            print(f"{Colors.WHITE}  Frontend: http://localhost:3001{Colors.END}")
            print(f"{Colors.WHITE}  Backend:  http://localhost:8001{Colors.END}")
        elif self.results['failed'] < 3:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}  ⚠ MOSTLY OPERATIONAL{Colors.END}")
            print(f"\n{Colors.WHITE}  Some components need attention{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}  ✗ SYSTEM ISSUES DETECTED{Colors.END}")
            print(f"\n{Colors.WHITE}  Please fix the failed tests before using{Colors.END}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        self.print_header("FULL PIPELINE END-TO-END TEST")
        
        print(f"{Colors.WHITE}Testing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
        print(f"{Colors.WHITE}Backend URL: {self.backend_url}{Colors.END}")
        
        # Core services
        self.print_header("1. CORE SERVICES")
        backend_ok = self.test_backend_health()
        if not backend_ok:
            print(f"\n{Colors.RED}Cannot proceed without backend. Stopping tests.{Colors.END}")
            self.print_summary()
            return
        
        ollama_ok = self.test_ollama_connection()
        weaviate_ok = self.test_weaviate_connection()
        
        # Knowledge Base
        self.print_header("2. KNOWLEDGE BASE (CSE Report)")
        kb_stats = self.test_knowledge_base_status()
        if kb_stats.get('status') == 'ready':
            self.test_knowledge_base_query()
        elif kb_stats.get('status') == 'not_initialized':
            self.print_info("Skipping query test - knowledge base not initialized")
        
        # News RAG
        self.print_header("3. NEWS RAG SYSTEM")
        news_ok = self.test_news_rag_health()
        if news_ok:
            self.test_news_query()
        
        # Integration
        self.print_header("4. FRONTEND INTEGRATION")
        self.test_quick_actions()
        
        # Summary
        self.print_summary()


def main():
    """Main entry point"""
    import sys
    
    # Get backend URL from args or use default
    backend_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001"
    
    tester = PipelineTester(backend_url=backend_url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
