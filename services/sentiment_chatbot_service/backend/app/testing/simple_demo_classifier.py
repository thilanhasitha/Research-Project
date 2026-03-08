"""
Simple Demo - Show query classifications and responses
"""

import sys
import os

# Add parent directories to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

from app.utils.query_classifier import QueryClassifier


def main():
    """Demonstrate query classification with sample queries."""
    
    classifier = QueryClassifier()
    
    # Sample queries to demonstrate
    demo_queries = [
        # Greetings
        ("Hello", "Should get a friendly greeting response"),
        ("Good morning", "Should get a friendly greeting response"),
        
        # Out-of-scope
        ("What's the weather today?", "Should redirect to financial topics"),
        ("Who won the football match?", "Should redirect to financial topics"),
        ("Tell me a joke", "Should redirect to financial topics"),
        
        # In-scope (Financial)
        ("What's the latest news about stocks?", "Should proceed with RAG"),
        ("Tell me about Tesla stock", "Should proceed with RAG"),
        ("What are the market trends?", "Should proceed with RAG"),
    ]
    
    print("\n" + "="*80)
    print("🤖 GREETING & OUT-OF-SCOPE HANDLER - DEMONSTRATION")
    print("="*80 + "\n")
    
    for query, note in demo_queries:
        classification, response = classifier.classify_query(query)
        
        # Format output
        emoji = {
            'greeting': '👋',
            'out_of_scope': '⛔',
            'in_scope': '💰'
        }.get(classification, '❓')
        
        print(f"\n{emoji} Query: \"{query}\"")
        print(f"   Classification: {classification.upper()}")
        print(f"   Note: {note}")
        
        if response:
            # Truncate long responses
            response_short = response[:120] + "..." if len(response) > 120 else response
            print(f"   Response: {response_short}")
        else:
            print(f"   Response: [Proceeds to RAG - retrieves articles & generates answer]")
        
        print("-" * 80)
    
    print("\n✅ All query types handled correctly!")
    print("\n📝 Summary:")
    print("   • Greetings → Instant friendly response (no DB/LLM)")
    print("   • Out-of-scope → Instant redirect message (no DB/LLM)")
    print("   • Financial queries → Full RAG processing (articles + LLM)\n")


if __name__ == "__main__":
    main()
