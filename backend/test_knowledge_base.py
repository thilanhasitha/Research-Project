"""
Quick Test Script for Knowledge Base
=====================================
Test the knowledge base without starting the full API server
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.services.knowledge_base_service import KnowledgeBaseService
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)


def main():
    print("\n" + "="*60)
    print("Knowledge Base Quick Test")
    print("="*60 + "\n")
    
    # Initialize service
    print("Initializing Knowledge Base Service...")
    kb = KnowledgeBaseService()
    
    # Check status
    stats = kb.get_stats()
    print(f"\nStatus: {stats.get('status')}")
    
    if stats.get('status') != 'active':
        print("\n⚠️  Knowledge base not found!")
        print("Run: python setup_knowledge_base.py")
        return
    
    print(f"Total chunks: {stats.get('total_chunks')}")
    print(f"Model: {stats.get('model')}")
    print(f"Embedding: {stats.get('embedding_model')}")
    
    # Test queries
    test_questions = [
        "What are the key financial highlights from 2024?",
        "What was the total trading volume?",
        "What risks are mentioned in the report?",
    ]
    
    print("\n" + "="*60)
    print("Testing Sample Queries")
    print("="*60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n[Query {i}]")
        print(f"Q: {question}")
        print("-" * 60)
        
        result = kb.query(question, n_results=3, include_sources=False)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"A: {result['answer'][:300]}...")
            print(f"\nConfidence: {result['confidence']:.2f}")
    
    print("\n" + "="*60)
    print("Interactive Mode")
    print("="*60)
    print("Enter your questions (or 'quit' to exit):\n")
    
    while True:
        try:
            question = input("\nYour question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if not question:
                continue
            
            print("\nProcessing...")
            result = kb.query(question, n_results=5)
            
            print(f"\n{result['answer']}")
            print(f"\n[Confidence: {result['confidence']:.2f}]")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
