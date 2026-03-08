"""
Knowledge Base Validation Script
=================================
Comprehensive validation and testing of the knowledge base system
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List
import json

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.services.knowledge_base_service import KnowledgeBaseService

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class KnowledgeBaseValidator:
    """Validator for knowledge base system"""
    
    def __init__(self):
        self.kb_service = None
        self.validation_results = []
    
    def validate_ollama_connection(self) -> bool:
        """Validate Ollama is running and accessible"""
        print("\n[1/5] Validating Ollama Connection...")
        try:
            import ollama
            models = ollama.list()
            print("  ✅ Ollama is accessible")
            
            # Get model lists
            if isinstance(models, dict):
                model_names = [m.get('name', m.get('model', '')) for m in models.get('models', [])]
            else:
                model_names = [m.name if hasattr(m, 'name') else str(m) for m in getattr(models, 'models', [])]
            
            if model_names:
                print(f"  ✅ Found {len(model_names)} models: {', '.join(model_names[:3])}...")
                self.validation_results.append({"test": "ollama_connection", "status": "passed"})
                return True
            else:
                print("  ⚠️  No models found. Please run: ollama pull llama3.2")
                self.validation_results.append({"test": "ollama_connection", "status": "warning", "message": "No models"})
                return False
                
        except Exception as e:
            print(f"  ❌ Ollama connection failed: {e}")
            print("     Make sure Ollama is running: ollama serve")
            self.validation_results.append({"test": "ollama_connection", "status": "failed", "error": str(e)})
            return False
    
    def validate_chromadb(self) -> bool:
        """Validate ChromaDB installation and setup"""
        print("\n[2/5] Validating ChromaDB...")
        try:
            import chromadb
            print("  ✅ ChromaDB is installed")
            
            # Check data directory
            data_dir = Path("./data/knowledge_base")
            if data_dir.exists():
                print(f"  ✅ Knowledge base directory exists: {data_dir.absolute()}")
            else:
                print(f"  ℹ️  Knowledge base directory will be created: {data_dir.absolute()}")
            
            self.validation_results.append({"test": "chromadb", "status": "passed"})
            return True
            
        except ImportError:
            print("  ❌ ChromaDB not installed")
            print("     Run: pip install chromadb")
            self.validation_results.append({"test": "chromadb", "status": "failed", "error": "Not installed"})
            return False
        except Exception as e:
            print(f"  ❌ ChromaDB validation failed: {e}")
            self.validation_results.append({"test": "chromadb", "status": "failed", "error": str(e)})
            return False
    
    def validate_service_initialization(self) -> bool:
        """Validate knowledge base service can be initialized"""
        print("\n[3/5] Validating Service Initialization...")
        try:
            self.kb_service = KnowledgeBaseService()
            print("  ✅ Knowledge base service initialized")
            
            stats = self.kb_service.get_stats()
            if stats.get('status') == 'active':
                print(f"  ✅ Knowledge base is active with {stats.get('total_chunks', 0)} chunks")
                self.validation_results.append({"test": "service_init", "status": "passed", "chunks": stats.get('total_chunks')})
                return True
            elif stats.get('status') == 'not_initialized':
                print("  ℹ️  Knowledge base not built yet")
                print("     Run: python setup_knowledge_base.py")
                self.validation_results.append({"test": "service_init", "status": "warning", "message": "Not built"})
                return False
            else:
                print(f"  ⚠️  Knowledge base status: {stats.get('status')}")
                self.validation_results.append({"test": "service_init", "status": "warning", "message": stats.get('status')})
                return False
                
        except Exception as e:
            print(f"  ❌ Service initialization failed: {e}")
            self.validation_results.append({"test": "service_init", "status": "failed", "error": str(e)})
            return False
    
    def validate_embedding_generation(self) -> bool:
        """Test embedding generation"""
        print("\n[4/5] Validating Embedding Generation...")
        if not self.kb_service:
            print("  ⚠️  Service not initialized, skipping")
            return False
        
        try:
            test_text = "This is a test sentence for embedding generation."
            embeddings = self.kb_service.get_embeddings(test_text)
            
            if embeddings and len(embeddings) > 0:
                print(f"  ✅ Embeddings generated successfully (dimension: {len(embeddings)})")
                self.validation_results.append({"test": "embedding_generation", "status": "passed", "dimension": len(embeddings)})
                return True
            else:
                print("  ❌ No embeddings generated")
                self.validation_results.append({"test": "embedding_generation", "status": "failed"})
                return False
                
        except Exception as e:
            print(f"  ❌ Embedding generation failed: {e}")
            self.validation_results.append({"test": "embedding_generation", "status": "failed", "error": str(e)})
            return False
    
    def validate_query_functionality(self) -> bool:
        """Test query functionality"""
        print("\n[5/5] Validating Query Functionality...")
        if not self.kb_service:
            print("  ⚠️  Service not initialized, skipping")
            return False
        
        stats = self.kb_service.get_stats()
        if stats.get('status') != 'active':
            print("  ⚠️  Knowledge base not active, skipping query test")
            print("     Build the knowledge base first: python setup_knowledge_base.py")
            return False
        
        try:
            test_question = "What are the key highlights?"
            print(f"  Testing query: '{test_question}'")
            
            result = self.kb_service.query(test_question, n_results=3)
            
            if 'error' in result:
                print(f"  ❌ Query returned error: {result.get('error')}")
                self.validation_results.append({"test": "query_functionality", "status": "failed", "error": result.get('error')})
                return False
            
            if result.get('answer'):
                print(f"  ✅ Query successful")
                print(f"     Answer preview: {result['answer'][:100]}...")
                print(f"     Confidence: {result.get('confidence', 0):.2f}")
                self.validation_results.append({
                    "test": "query_functionality", 
                    "status": "passed",
                    "confidence": result.get('confidence')
                })
                return True
            else:
                print("  ❌ No answer generated")
                self.validation_results.append({"test": "query_functionality", "status": "failed"})
                return False
                
        except Exception as e:
            print(f"  ❌ Query test failed: {e}")
            self.validation_results.append({"test": "query_functionality", "status": "failed", "error": str(e)})
            return False
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.validation_results if r.get('status') == 'passed')
        failed = sum(1 for r in self.validation_results if r.get('status') == 'failed')
        warnings = sum(1 for r in self.validation_results if r.get('status') == 'warning')
        
        print(f"\nTotal Tests: {len(self.validation_results)}")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⚠️  Warnings: {warnings}")
        
        if failed == 0 and warnings == 0:
            print("\n🎉 All validations passed! Knowledge base system is fully operational.")
        elif failed == 0:
            print("\n⚠️  System is operational but has warnings. Check details above.")
        else:
            print("\n❌ System has failures. Please fix the issues above.")
        
        print("\nNext Steps:")
        if not self.kb_service or self.kb_service.get_stats().get('status') != 'active':
            print("  1. Build the knowledge base: python setup_knowledge_base.py")
            print("  2. Start the API server: uvicorn app.main:app --reload")
            print("  3. Test interactively: python test_knowledge_base.py")
        else:
            print("  1. Start the API server: uvicorn app.main:app --reload")
            print("  2. Test interactively: python test_knowledge_base.py")
            print("  3. Access API docs: http://localhost:8000/docs")
        
        print("\n" + "="*60)


def main():
    """Main validation function"""
    print("="*60)
    print("Knowledge Base System Validation")
    print("="*60)
    
    validator = KnowledgeBaseValidator()
    
    # Run all validations
    validator.validate_ollama_connection()
    validator.validate_chromadb()
    validator.validate_service_initialization()
    validator.validate_embedding_generation()
    validator.validate_query_functionality()
    
    # Print summary
    validator.print_summary()


if __name__ == "__main__":
    main()
