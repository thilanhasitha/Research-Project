"""
Test Query Classifier
Tests the greeting and out-of-scope detection without requiring database or LLM.
"""

import sys
import os

# Add parent directories to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

from app.utils.query_classifier import QueryClassifier


def test_query_classifier():
    """Test the query classifier with various inputs."""
    
    classifier = QueryClassifier()
    
    # Test cases with expected classifications
    test_cases = [
        # Greetings
        ("Hello", "greeting"),
        ("Hi", "greeting"),
        ("Hey there", "greeting"),
        ("Good morning", "greeting"),
        ("What's up", "greeting"),
        ("Howdy!", "greeting"),
        
        # Out-of-scope queries
        ("What is the weather today?", "out_of_scope"),
        ("Who won the football match?", "out_of_scope"),
        ("Tell me a recipe for pizza", "out_of_scope"),
        ("What movie should I watch?", "out_of_scope"),
        ("Who are you?", "out_of_scope"),
        ("What's your name?", "out_of_scope"),
        ("How to write Python code?", "out_of_scope"),
        ("Tell me about the French Revolution", "out_of_scope"),
        
        # In-scope queries (financial/stock market)
        ("What's the latest news about stocks?", "in_scope"),
        ("Tell me about the stock market today", "in_scope"),
        ("What's the price of Tesla stock?", "in_scope"),
        ("Show me recent trading news", "in_scope"),
        ("What are the latest financial news?", "in_scope"),
        ("Tell me about the market crash", "in_scope"),
        ("What's the sentiment around Apple?", "in_scope"),
        ("How are the markets performing?", "in_scope"),
        ("Tell me about dividend stocks", "in_scope"),
        ("What's the latest on cryptocurrency?", "in_scope"),
        ("What's happening in the banking sector?", "in_scope"),
        ("Show me trending financial articles", "in_scope"),
        ("What are the current interest rates?", "in_scope"),
        ("Tell me about the recent IPO", "in_scope"),
        ("What's the latest earnings report?", "in_scope"),
    ]
    
    print("\n" + "="*80)
    print("QUERY CLASSIFIER TESTS")
    print("="*80 + "\n")
    
    passed = 0
    failed = 0
    
    for query, expected_classification in test_cases:
        classification, response = classifier.classify_query(query)
        
        status = "✓ PASS" if classification == expected_classification else "✗ FAIL"
        
        if classification == expected_classification:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | Query: '{query}'")
        print(f"       | Expected: {expected_classification}, Got: {classification}")
        
        if response:
            # Truncate response for display
            response_preview = response[:100] + "..." if len(response) > 100 else response
            print(f"       | Response: {response_preview}")
        
        print()
    
    print("="*80)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*80 + "\n")
    
    return failed == 0


def test_individual_methods():
    """Test individual classifier methods."""
    
    classifier = QueryClassifier()
    
    print("\n" + "="*80)
    print("INDIVIDUAL METHOD TESTS")
    print("="*80 + "\n")
    
    # Test is_greeting
    print("Testing is_greeting():")
    greetings = ["Hello", "Hi there", "Good morning", "Hey"]
    for greeting in greetings:
        result = classifier.is_greeting(greeting)
        print(f"  '{greeting}' -> {result}")
    print()
    
    # Test is_in_scope
    print("Testing is_in_scope():")
    financial_queries = [
        "What's the stock price?",
        "Tell me about the market",
        "Show me trading news",
        "What's the weather?"  # Should be False
    ]
    for query in financial_queries:
        result = classifier.is_in_scope(query)
        print(f"  '{query}' -> {result}")
    print()


if __name__ == "__main__":
    print("\n🧪 Starting Query Classifier Tests...\n")
    
    # Test individual methods
    test_individual_methods()
    
    # Run comprehensive tests
    success = test_query_classifier()
    
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
