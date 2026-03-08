"""
Interactive Demo - Greeting and Out-of-Scope Handler
Test the query classification in real-time without needing database or LLM.
"""

import sys
import os

# Add parent directories to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

from app.utils.query_classifier import QueryClassifier


def print_banner():
    """Print welcome banner."""
    print("\n" + "="*80)
    print("🤖 GREETING & OUT-OF-SCOPE QUERY HANDLER - INTERACTIVE DEMO")
    print("="*80)
    print("\nThis demo shows how the system handles different types of queries:")
    print("  ✅ Greetings  → Direct friendly response")
    print("  ⛔ Out-of-scope → Polite redirect to financial topics")
    print("  💰 Financial  → Proceeds with RAG (article retrieval + LLM)\n")
    print("Type 'examples' to see sample queries, or 'quit' to exit.\n")
    print("="*80 + "\n")


def show_examples():
    """Show example queries."""
    print("\n" + "="*80)
    print("EXAMPLE QUERIES")
    print("="*80 + "\n")
    
    print("✅ GREETINGS (get instant friendly response):")
    print("  • Hello")
    print("  • Hi there")
    print("  • Good morning")
    print("  • What's up\n")
    
    print("⛔ OUT-OF-SCOPE (get polite redirect):")
    print("  • What is the weather today?")
    print("  • Tell me a joke")
    print("  • Who won the football match?")
    print("  • What movie should I watch?")
    print("  • Who are you?\n")
    
    print("💰 FINANCIAL/IN-SCOPE (normal RAG processing):")
    print("  • What's the latest news about stocks?")
    print("  • Tell me about Tesla stock price")
    print("  • Show me market trends")
    print("  • What's the sentiment around Apple?")
    print("  • Latest IPO news")
    print("  • How are the markets performing?\n")
    
    print("="*80 + "\n")


def format_response(classification: str, response: str, query: str) -> str:
    """Format the response for display."""
    
    # Classification emoji
    emoji_map = {
        'greeting': '👋',
        'out_of_scope': '⛔',
        'in_scope': '💰'
    }
    
    # Status text
    status_map = {
        'greeting': 'GREETING DETECTED',
        'out_of_scope': 'OUT-OF-SCOPE QUERY',
        'in_scope': 'FINANCIAL QUERY (In-Scope)'
    }
    
    emoji = emoji_map.get(classification, '❓')
    status = status_map.get(classification, 'UNKNOWN')
    
    output = []
    output.append("\n" + "-"*80)
    output.append(f"{emoji} {status}")
    output.append("-"*80)
    output.append(f"Your Query: \"{query}\"")
    output.append("")
    
    if classification == 'in_scope':
        output.append("✅ Status: This query will proceed with RAG processing:")
        output.append("   1. Retrieve relevant financial news articles from database")
        output.append("   2. Generate contextual answer using LLM")
        output.append("   3. Return answer with source citations")
    else:
        output.append("📨 INSTANT RESPONSE (no database/LLM needed):")
        output.append("")
        output.append(f"   {response}")
        output.append("")
        output.append("⚡ Processing time: < 1ms")
        output.append(f"💾 Database queries: 0")
        output.append(f"🤖 LLM calls: 0")
    
    output.append("-"*80 + "\n")
    
    return "\n".join(output)


def main():
    """Run interactive demo."""
    
    print_banner()
    
    classifier = QueryClassifier()
    
    while True:
        try:
            # Get user input
            user_query = input("💬 Enter your query (or 'examples'/'quit'): ").strip()
            
            if not user_query:
                continue
            
            # Handle special commands
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thanks for trying the demo! Goodbye!\n")
                break
            
            if user_query.lower() in ['examples', 'example', 'help', 'h']:
                show_examples()
                continue
            
            # Classify the query
            classification, response = classifier.classify_query(user_query)
            
            # Display result
            print(format_response(classification, response, user_query))
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
