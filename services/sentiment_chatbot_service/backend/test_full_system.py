"""
Comprehensive Knowledge Base System Test
=========================================
Tests all components to verify the system is fully working
"""

import sys
from pathlib import Path
import subprocess
import time
import requests

# Add backend to path
sys.path.append(str(Path(__file__).parent))


class SystemTester:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
        
    def print_header(self, title):
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    
    def print_test(self, test_name, status, details=""):
        status_symbol = "✅" if status else "❌"
        print(f"\n{status_symbol} {test_name}")
        if details:
            print(f"   {details}")
        
        if status:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
        
        self.results.append({
            'test': test_name,
            'passed': status,
            'details': details
        })
    
    def test_dependencies(self):
        """Test if all required packages are installed"""
        self.print_header("1. TESTING DEPENDENCIES")
        
        packages = ['chromadb', 'ollama', 'PyPDF2', 'fastapi', 'uvicorn']
        
        for package in packages:
            try:
                __import__(package.replace('-', '_').lower())
                self.print_test(f"Package: {package}", True, "Installed")
            except ImportError:
                self.print_test(f"Package: {package}", False, "Not installed")
    
    def test_ollama_service(self):
        """Test if Ollama service is running"""
        self.print_header("2. TESTING OLLAMA SERVICE")
        
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                self.print_test("Ollama Service", True, "Running on port 11434")
                return True
            else:
                self.print_test("Ollama Service", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Ollama Service", False, str(e))
            print("   💡 Start Ollama: ollama serve")
            return False
    
    def test_ollama_models(self):
        """Test if required Ollama models are available"""
        self.print_header("3. TESTING OLLAMA MODELS")
        
        required_models = ['llama2', 'nomic-embed-text']
        
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                available_models = [model['name'].split(':')[0] for model in response.json().get('models', [])]
                
                for model in required_models:
                    if model in available_models:
                        self.print_test(f"Model: {model}", True, "Available")
                    else:
                        self.print_test(f"Model: {model}", False, "Not found")
                        print(f"   💡 Install: ollama pull {model}")
            else:
                self.print_test("Check Models", False, "Cannot connect to Ollama")
        except Exception as e:
            self.print_test("Check Models", False, str(e))
    
    def test_chromadb_connection(self):
        """Test ChromaDB connection"""
        self.print_header("4. TESTING CHROMADB")
        
        try:
            import chromadb
            client = chromadb.Client()
            collections = client.list_collections()
            self.print_test("ChromaDB Connection", True, f"Found {len(collections)} collection(s)")
            
            # Check if knowledge base collection exists
            collection_names = [c.name for c in collections]
            if 'knowledge_base' in collection_names:
                kb_collection = client.get_collection('knowledge_base')
                count = kb_collection.count()
                self.print_test("Knowledge Base Collection", True, f"{count} chunks stored")
            else:
                self.print_test("Knowledge Base Collection", False, "Not found")
                print("   💡 Build it: python setup_knowledge_base.py")
        except Exception as e:
            self.print_test("ChromaDB Connection", False, str(e))
    
    def test_pdf_file(self):
        """Test if PDF file exists"""
        self.print_header("5. TESTING PDF FILE")
        
        pdf_path = Path(__file__).parent / "data" / "uploads" / "CSE_Annual_Report_2024.pdf"
        
        if pdf_path.exists():
            size_mb = pdf_path.stat().st_size / (1024 * 1024)
            self.print_test("PDF File", True, f"Found ({size_mb:.2f} MB)")
        else:
            self.print_test("PDF File", False, "Not found")
            print(f"   💡 Place PDF at: {pdf_path}")
    
    def test_knowledge_base_service(self):
        """Test Knowledge Base Service"""
        self.print_header("6. TESTING KNOWLEDGE BASE SERVICE")
        
        try:
            from app.services.knowledge_base_service import KnowledgeBaseService
            
            kb = KnowledgeBaseService()
            self.print_test("Service Import", True, "Successfully imported")
            
            # Get stats
            stats = kb.get_stats()
            if stats.get('status') == 'active':
                self.print_test("Service Status", True, "Active")
                print(f"   Total chunks: {stats.get('total_chunks')}")
                print(f"   Model: {stats.get('model')}")
                print(f"   Embedding: {stats.get('embedding_model')}")
            else:
                self.print_test("Service Status", False, "Not active")
                return False
            
            # Test query
            result = kb.query("What is this document about?", n_results=3)
            if 'answer' in result:
                self.print_test("Query Test", True, "Successful")
                print(f"   Confidence: {result.get('confidence', 0):.2f}")
                print(f"   Answer preview: {result['answer'][:100]}...")
            else:
                self.print_test("Query Test", False, result.get('error', 'Unknown error'))
            
            return True
        except Exception as e:
            self.print_test("Service Test", False, str(e))
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints if server is running"""
        self.print_header("7. TESTING API ENDPOINTS")
        
        base_url = "http://localhost:8000"
        
        try:
            # Test health endpoint
            response = requests.get(f"{base_url}/api/knowledge/health", timeout=5)
            if response.status_code == 200:
                self.print_test("Health Endpoint", True, "Responding")
            else:
                self.print_test("Health Endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("API Server", False, "Not running")
            print("   💡 Start server: uvicorn app.main:app --reload")
            return False
        
        try:
            # Test stats endpoint
            response = requests.get(f"{base_url}/api/knowledge/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.print_test("Stats Endpoint", True, f"Status: {data.get('status')}")
            else:
                self.print_test("Stats Endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Stats Endpoint", False, str(e))
        
        try:
            # Test query endpoint
            response = requests.post(
                f"{base_url}/api/knowledge/query",
                json={"question": "What is this report about?", "n_results": 3},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.print_test("Query Endpoint", True, "Working")
                print(f"   Response time: {response.elapsed.total_seconds():.2f}s")
            else:
                self.print_test("Query Endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Query Endpoint", False, str(e))
    
    def test_file_structure(self):
        """Test if all necessary files exist"""
        self.print_header("8. TESTING FILE STRUCTURE")
        
        base_path = Path(__file__).parent
        
        files_to_check = [
            ("app/services/knowledge_base_service.py", "Service File"),
            ("app/routes/knowledge_routes.py", "Routes File"),
            ("setup_knowledge_base.py", "Setup Script"),
            ("test_knowledge_base.py", "Test Script"),
            ("data/uploads", "Upload Directory"),
        ]
        
        for file_path, description in files_to_check:
            full_path = base_path / file_path
            if full_path.exists():
                self.print_test(description, True, str(file_path))
            else:
                self.print_test(description, False, f"Missing: {file_path}")
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        total = self.tests_passed + self.tests_failed
        percentage = (self.tests_passed / total * 100) if total > 0 else 0
        
        print(f"\n  Total Tests: {total}")
        print(f"  ✅ Passed: {self.tests_passed}")
        print(f"  ❌ Failed: {self.tests_failed}")
        print(f"  Success Rate: {percentage:.1f}%")
        
        if self.tests_failed == 0:
            print("\n  🎉 ALL TESTS PASSED! System is fully operational!")
        else:
            print("\n  ⚠️  Some tests failed. Check details above.")
            print("  💡 Follow the suggestions to fix issues.")
        
        print("\n" + "="*70 + "\n")
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("  COMPREHENSIVE KNOWLEDGE BASE SYSTEM TEST")
        print("  Starting full system check...")
        print("="*70)
        
        self.test_file_structure()
        self.test_dependencies()
        self.test_ollama_service()
        self.test_ollama_models()
        self.test_chromadb_connection()
        self.test_pdf_file()
        self.test_knowledge_base_service()
        self.test_api_endpoints()
        
        self.print_summary()
        
        return self.tests_failed == 0


def main():
    tester = SystemTester()
    success = tester.run_all_tests()
    
    if not success:
        print("Quick Fix Guide:")
        print("-" * 70)
        print("1. Install missing packages: pip install chromadb ollama PyPDF2")
        print("2. Start Ollama: ollama serve")
        print("3. Pull models: ollama pull llama2 && ollama pull nomic-embed-text")
        print("4. Build knowledge base: python setup_knowledge_base.py")
        print("5. Start API server: uvicorn app.main:app --reload")
        print("-" * 70)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
