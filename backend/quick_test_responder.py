"""
Quick test script to verify general responder functionality.
Run this after starting your Docker services.
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.chat.agent.schema import AgentState
from app.services.chat.tools.agent_pipeline import shopping_assistant


async def quick_test():
    """Quick test of general responder."""
    
    print("\n" + "="*60)
    print("QUICK TEST: General Responder with Tools")
    print("="*60)
    
    # Test 1: Simple greeting (should NOT use tools)
    print("\n[Test 1] Testing greeting...")
    state1 = AgentState(
        input="Hi there!",
        user_id="quick_test_1",
        conversation_history=[]
    )
    
    try:
        result1 = await shopping_assistant.ainvoke(state1)
        print(f"✓ Intent: {result1.get('current_intent')}")
        print(f"✓ Used tools: {result1.get('has_tool_calls', False)}")
        print(f"✓ Response: {result1.get('output', '')[:100]}...")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: News query (SHOULD use tools)
    print("\n[Test 2] Testing news search...")
    state2 = AgentState(
        input="Find me news about technology",
        user_id="quick_test_2",
        conversation_history=[]
    )
    
    try:
        result2 = await shopping_assistant.ainvoke(state2)
        print(f"✓ Intent: {result2.get('current_intent')}")
        print(f"✓ Used tools: {result2.get('has_tool_calls', False)}")
        if result2.get('tool_results'):
            tools_used = [t.get('name') for t in result2.get('tool_results', []) if isinstance(t, dict) and 'name' in t]
            print(f"✓ Tools called: {tools_used}")
        print(f"✓ Response: {result2.get('output', '')[:100]}...")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "="*60)
    print("Quick test complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\n⚠️  Make sure Docker services are running: docker compose up -d")
    print("Press Enter to continue...")
    input()
    
    asyncio.run(quick_test())
