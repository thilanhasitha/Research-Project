"""
Chat routes for testing the general responder with tools.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.chat.agent.schema import AgentState, MessageModel, ChatRequest, ChatResponse
from app.services.chat.tools.agent_pipeline import shopping_assistant
import logging

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)


class SimpleChatRequest(BaseModel):
    """Simple chat request for testing."""
    message: str
    user_id: str = "test_user"


@router.post("/message", response_model=Dict[str, Any])
async def send_message(request: SimpleChatRequest):
    """
    Send a message to the general responder.
    Tests if the agent correctly uses tools when needed.
    """
    try:
        logger.info(f"Received chat message: {request.message}")
        
        # Create initial state
        initial_state = AgentState(
            input=request.message,
            user_id=request.user_id,
            conversation_history=[]
        )
        
        # Run the agent
        result = await shopping_assistant.ainvoke(initial_state)
        
        # Extract relevant information
        response = {
            "status": "success",
            "message": request.message,
            "response": result.get("output", "No response generated"),
            "intent": result.get("current_intent"),
            "used_tools": result.get("has_tool_calls", False),
            "tool_calls": []
        }
        
        # Add tool call details if any
        if result.get("tool_results"):
            for tool in result.get("tool_results", []):
                if isinstance(tool, dict) and "name" in tool:
                    response["tool_calls"].append({
                        "name": tool.get("name"),
                        "args": tool.get("args", {})
                    })
        
        logger.info(f"Response generated. Used tools: {response['used_tools']}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
async def test_responder():
    """
    Quick test endpoint to verify the chat system is working.
    """
    test_messages = [
        "Hello!",
        "Find me news about technology",
        "What are the latest articles?"
    ]
    
    results = []
    for msg in test_messages:
        try:
            initial_state = AgentState(
                input=msg,
                user_id="test_user_automated",
                conversation_history=[]
            )
            
            result = await shopping_assistant.ainvoke(initial_state)
            
            results.append({
                "message": msg,
                "intent": result.get("current_intent"),
                "used_tools": result.get("has_tool_calls", False),
                "response_preview": result.get("output", "")[:100] + "..."
            })
        except Exception as e:
            results.append({
                "message": msg,
                "error": str(e)
            })
    
    return {
        "status": "success",
        "test_results": results
    }
