"""
Test script to verify the general responder works with tools.

This script tests:
1. General conversational responses (no tools)
2. News search queries (should use tools)
3. Tool execution flow
"""

import asyncio
import logging
from app.services.chat.agent.schema import AgentState, MessageModel
from app.services.chat.tools.agent_pipeline import shopping_assistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_general_responder():
    """Test the general responder with different types of queries."""
    
    # Test cases
    test_cases = [
        {
            "name": "Greeting (no tools expected)",
            "input": "Hello! How are you?",
            "user_id": "test_user_1",
            "expected_tools": False
        },
        {
            "name": "News search (tools expected)",
            "input": "Show me recent news about technology",
            "user_id": "test_user_2",
            "expected_tools": True
        },
        {
            "name": "Topic search (tools expected)",
            "input": "What are the latest articles on AI?",
            "user_id": "test_user_3",
            "expected_tools": True
        },
        {
            "name": "General question (may use tools)",
            "input": "Can you help me find information about finance?",
            "user_id": "test_user_4",
            "expected_tools": True
        }
    ]
    
    print("\n" + "="*80)
    print("TESTING GENERAL RESPONDER WITH TOOLS")
    print("="*80 + "\n")
    
    for idx, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test {idx}: {test_case['name']}")
        print(f"{'='*80}")
        print(f"Input: {test_case['input']}")
        print(f"Expected tools: {test_case['expected_tools']}")
        print("-"*80)
        
        # Create initial state
        initial_state = AgentState(
            input=test_case["input"],
            user_id=test_case["user_id"],
            conversation_history=[]
        )
        
        try:
            # Run the agent
            result = await shopping_assistant.ainvoke(initial_state)
            
            # Display results
            print(f"\n✓ Test completed successfully")
            print(f"\nIntent Classification:")
            print(f"  - Current Intent: {result.get('current_intent')}")
            print(f"  - Last Intent: {result.get('last_intent')}")
            
            if result.get('has_tool_calls'):
                print(f"\n✓ Tools were used (as expected: {test_case['expected_tools']})")
                print(f"\nTool Calls:")
                for tool in result.get('tool_results', []):
                    if isinstance(tool, dict) and 'name' in tool:
                        print(f"  - {tool.get('name')}: {tool.get('args', {})}")
            else:
                print(f"\n✓ No tools used (as expected: {not test_case['expected_tools']})")
            
            print(f"\n📝 Final Output:")
            output = result.get('output', 'No output generated')
            # Truncate long outputs
            if len(output) > 300:
                print(f"  {output[:300]}...")
            else:
                print(f"  {output}")
            
            # Check if expectations met
            used_tools = result.get('has_tool_calls', False)
            if used_tools == test_case['expected_tools']:
                print(f"\n✅ PASSED: Tool usage matched expectations")
            else:
                print(f"\n⚠️  WARNING: Expected tools={test_case['expected_tools']}, but got tools={used_tools}")
            
        except Exception as e:
            print(f"\n❌ Test failed with error:")
            print(f"  {type(e).__name__}: {str(e)}")
            logger.exception("Detailed error:")
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80 + "\n")


async def test_conversation_flow():
    """Test a multi-turn conversation to verify history context works."""
    
    print("\n" + "="*80)
    print("TESTING CONVERSATION FLOW WITH HISTORY")
    print("="*80 + "\n")
    
    user_id = "test_user_conversation"
    conversation_history = []
    
    turns = [
        "Hello!",
        "Can you find news about artificial intelligence?",
        "What about the latest updates?",  # Should use context
    ]
    
    for idx, user_input in enumerate(turns, 1):
        print(f"\n{'='*60}")
        print(f"Turn {idx}")
        print(f"{'='*60}")
        print(f"User: {user_input}")
        print("-"*60)
        
        initial_state = AgentState(
            input=user_input,
            user_id=user_id,
            conversation_history=conversation_history.copy()
        )
        
        try:
            result = await shopping_assistant.ainvoke(initial_state)
            
            output = result.get('output', 'No response')
            print(f"Assistant: {output[:200]}..." if len(output) > 200 else f"Assistant: {output}")
            
            # Update conversation history
            conversation_history.append(MessageModel(role="user", content=user_input))
            conversation_history.append(MessageModel(role="assistant", content=output))
            
            if result.get('has_tool_calls'):
                print(f"[Tools used: {', '.join([t.get('name') for t in result.get('tool_results', []) if isinstance(t, dict) and 'name' in t])}]")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            logger.exception("Detailed error:")
    
    print("\n" + "="*80)
    print("CONVERSATION TEST COMPLETED")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\nStarting General Responder Tests...")
    print("Make sure your backend services (MongoDB, Weaviate, Ollama) are running!\n")
    
    # Run basic tests
    asyncio.run(test_general_responder())
    
    # Run conversation flow test
    asyncio.run(test_conversation_flow())
    
    print("\n✓ All tests completed!\n")
