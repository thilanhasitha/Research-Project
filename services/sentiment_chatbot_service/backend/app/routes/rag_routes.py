"""
RAG Routes - Annual Report Q&A API
FastAPI routes for PDF RAG with Ollama
"""

from fastapi import APIRouter, HTTPException
from app.services.pdf_rag_service import PDFRagService, QuestionRequest, AnswerResponse

router = APIRouter(prefix="/api/pdf-rag", tags=["PDF RAG"])

# Initialize service
rag_service = PDFRagService()


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about the Annual Report
    
    Args:
        request: Question with optional parameters
        
    Returns:
        AI-generated answer based on Annual Report content
        
    Example:
        POST /api/pdf-rag/ask
        {
            "question": "What was the revenue in 2024?",
            "n_results": 5,
            "model": "llama3.2:latest",
            "show_context": false
        }
    """
    try:
        response = await rag_service.ask_question(request)
        
        if response.status == "error":
            raise HTTPException(status_code=500, detail=response.error)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Check PDF RAG service health
    
    Returns:
        Health status of RAG system, Ollama, and PDF index
    """
    return rag_service.health_check()


@router.get("/info")
async def get_info():
    """
    Get information about the indexed documents
    
    Returns:
        Information about available documents and chunks
    """
    if rag_service.rag_system is None:
        return {
            "status": "unavailable",
            "message": "RAG system not initialized"
        }
    
    chunks = rag_service.rag_system.chunks
    
    # Get unique sources
    sources = {}
    for chunk in chunks:
        source = chunk.get('source', 'unknown')
        if source not in sources:
            sources[source] = {
                'chunks': 0,
                'total_characters': 0,
                'timestamp': chunk.get('timestamp', 'N/A')
            }
        sources[source]['chunks'] += 1
        sources[source]['total_characters'] += len(chunk.get('text', ''))
    
    return {
        "status": "available",
        "total_chunks": len(chunks),
        "documents": sources,
        "ollama_url": rag_service.rag_system.ollama_url
    }

