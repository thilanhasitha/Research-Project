"""
News Assistant Chat Routes
Provides conversational interface for querying financial news with RAG.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.services.news_rag_service import NewsRAGService
import logging

router = APIRouter(prefix="/news-chat", tags=["News Chat"])
logger = logging.getLogger(__name__)

# Initialize RAG service
news_rag = NewsRAGService()


# Request/Response Models
class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


class NewsChatRequest(BaseModel):
    """Request for news chat."""
    message: str = Field(..., description="User's message/question", min_length=1)
    user_id: str = Field(default="anonymous", description="User identifier")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    include_sources: bool = Field(default=True, description="Include source articles in response")
    context_limit: int = Field(default=5, ge=1, le=20, description="Number of articles to use as context")


class NewsChatResponse(BaseModel):
    """Response from news chat."""
    message: str = Field(..., description="Assistant's response")
    sources: Optional[List[Dict[str, Any]]] = Field(default=None, description="Source articles used")
    context_used: int = Field(..., description="Number of articles used for context")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class SearchNewsRequest(BaseModel):
    """Request for searching news."""
    query: str = Field(..., description="Search query", min_length=1)
    limit: int = Field(default=10, ge=1, le=50, description="Maximum results")
    sentiment_filter: Optional[str] = Field(None, description="Filter by sentiment: positive, negative, neutral")
    days: Optional[int] = Field(None, ge=1, le=90, description="Only return news from last N days")


class SentimentRequest(BaseModel):
    """Request for sentiment analysis."""
    topic: Optional[str] = Field(None, description="Optional topic to analyze")
    days: int = Field(default=7, ge=1, le=90, description="Number of days to analyze")


# Endpoints
@router.post("/ask", response_model=NewsChatResponse)
async def ask_question(request: NewsChatRequest):
    """
    Ask a question about financial news using RAG.
    The system will retrieve relevant news articles and generate a contextual answer.
    
    Example questions:
    - "What's the latest news about tech stocks?"
    - "Tell me about recent market trends"
    - "What's the sentiment around AI companies?"
    """
    try:
        logger.info(f"User {request.user_id} asked: {request.message}")
        
        # Get answer using RAG
        result = await news_rag.answer_question(
            question=request.message,
            context_limit=request.context_limit,
            include_sources=request.include_sources
        )
        
        # Check for errors
        if "error" in result:
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return NewsChatResponse(
            message=result["answer"],
            sources=result.get("sources"),
            context_used=result["context_used"],
            conversation_id=request.conversation_id,
            metadata={
                "user_id": request.user_id,
                "query": request.message
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ask_question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")


@router.post("/search", response_model=List[Dict[str, Any]])
async def search_news(request: SearchNewsRequest):
    """
    Search for news articles using semantic search.
    Returns relevant articles without generating an answer.
    """
    try:
        logger.info(f"Searching news with query: {request.query}")
        
        # Calculate date filter if specified
        date_from = None
        if request.days:
            from datetime import timedelta
            date_from = datetime.utcnow() - timedelta(days=request.days)
        
        results = await news_rag.search_news_by_text(
            query=request.query,
            limit=request.limit,
            sentiment_filter=request.sentiment_filter,
            date_from=date_from
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error in search_news: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to search news: {str(e)}")


@router.get("/trending")
async def get_trending(days: int = 7, limit: int = 10):
    """
    Get trending news articles from the last N days.
    Articles are sorted by sentiment score (higher = more positive).
    """
    try:
        logger.info(f"Getting trending news for last {days} days")
        
        results = await news_rag.get_trending_topics(days=days, limit=limit)
        
        return {
            "trending": results,
            "period_days": days,
            "count": len(results),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in get_trending: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get trending news: {str(e)}")


@router.post("/sentiment", response_model=Dict[str, Any])
async def analyze_sentiment(request: SentimentRequest):
    """
    Get sentiment analysis summary for a topic or overall market.
    Returns sentiment distribution and statistics.
    
    Examples:
    - POST /sentiment with {"topic": "AI stocks", "days": 7}
    - POST /sentiment with {"days": 30} (overall market sentiment)
    """
    try:
        logger.info(f"Analyzing sentiment for topic: {request.topic}, days: {request.days}")
        
        result = await news_rag.get_sentiment_summary(
            topic=request.topic,
            days=request.days
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_sentiment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to analyze sentiment: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Check if the news chat service is healthy and can connect to Weaviate.
    """
    try:
        # Try to get collection info
        if news_rag.weaviate_client.is_connected:
            collection = news_rag.weaviate_client.collection
            
            # Try a simple query to verify it's working
            response = collection.query.fetch_objects(limit=1)
            
            return {
                "status": "healthy",
                "weaviate_connected": True,
                "collection": "RSSNews",
                "sample_count": len(response.objects),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "degraded",
                "weaviate_connected": False,
                "message": "Weaviate not connected",
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/stats")
async def get_statistics():
    """
    Get general statistics about the news database.
    """
    try:
        collection = news_rag.weaviate_client.collection
        
        # Get total count
        total_response = collection.query.fetch_objects(limit=1)
        
        # Get sentiment distribution
        sentiment_summary = await news_rag.get_sentiment_summary(days=30)
        
        return {
            "total_articles": sentiment_summary.get("total_articles", 0),
            "last_30_days": sentiment_summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")
