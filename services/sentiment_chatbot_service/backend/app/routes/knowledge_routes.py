"""
Knowledge Base API Routes
=========================
API endpoints for querying CSE Annual Report knowledge base
"""

from fastapi import APIRouter, HTTPException  # , UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import logging
from pathlib import Path
import shutil

from app.services.knowledge_base_service import KnowledgeBaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])

# Initialize knowledge base service
kb_service = KnowledgeBaseService()


class QueryRequest(BaseModel):
    """Request model for knowledge base queries"""
    question: str = Field(..., description="Question to ask about CSE Annual Report")
    n_results: int = Field(default=5, ge=1, le=10, description="Number of relevant chunks to retrieve")
    include_sources: bool = Field(default=True, description="Include source documents in response")


class QueryResponse(BaseModel):
    """Response model for knowledge base queries"""
    answer: str
    confidence: float
    sources: Optional[List[Dict]] = None
    metadata: Optional[Dict] = None
    error: Optional[str] = None


class BuildRequest(BaseModel):
    """Request model for building knowledge base"""
    pdf_path: str = Field(..., description="Path to CSE Annual Report PDF")
    force_rebuild: bool = Field(default=False, description="Force rebuild if collection exists")


class StatsResponse(BaseModel):
    """Response model for knowledge base statistics"""
    status: str
    total_chunks: Optional[int] = None
    model: Optional[str] = None
    embedding_model: Optional[str] = None
    collection_name: Optional[str] = None
    error: Optional[str] = None


@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """
    Query the CSE Annual Report knowledge base
    
    Example questions:
    - "What was the total trading volume in 2024?"
    - "What are the main financial highlights?"
    - "What risks are mentioned in the report?"
    """
    try:
        result = kb_service.query(
            question=request.question,
            n_results=request.n_results,
            include_sources=request.include_sources
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in query endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/build")
async def build_knowledge_base(request: BuildRequest):
    """
    Build knowledge base from CSE Annual Report PDF
    
    This endpoint processes the PDF and creates vector embeddings.
    It may take several minutes depending on the document size.
    """
    try:
        pdf_path = Path(request.pdf_path)
        
        if not pdf_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"PDF file not found: {request.pdf_path}"
            )
        
        logger.info(f"Building knowledge base from: {request.pdf_path}")
        
        success = kb_service.build_from_pdf(
            pdf_path=str(pdf_path),
            force_rebuild=request.force_rebuild
        )
        
        if success:
            stats = kb_service.get_stats()
            return {
                "status": "success",
                "message": "Knowledge base built successfully",
                "stats": stats
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to build knowledge base"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error building knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Temporarily commented out - requires python-multipart
# @router.post("/upload-pdf")
# async def upload_pdf(file: UploadFile = File(...)):
#     """
#     Upload CSE Annual Report PDF and build knowledge base
#     
#     This combines upload and knowledge base creation in one step.
#     """
#     try:
#         # Validate file type
#         if not file.filename.endswith('.pdf'):
#             raise HTTPException(
#                 status_code=400,
#                 detail="Only PDF files are supported"
#             )
#         
#         # Save uploaded file
#         upload_dir = Path("./data/uploads")
#         upload_dir.mkdir(parents=True, exist_ok=True)
#         
#         file_path = upload_dir / file.filename
#         
#         with file_path.open("wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
#         
#         logger.info(f"PDF uploaded: {file_path}")
#         
#         # Build knowledge base
#         success = kb_service.build_from_pdf(
#             pdf_path=str(file_path),
#             force_rebuild=True
#         )
#         
#         if success:
#             stats = kb_service.get_stats()
#             return {
#                 "status": "success",
#                 "message": f"PDF uploaded and knowledge base built successfully",
#                 "filename": file.filename,
#                 "stats": stats
#             }
#         else:
#             raise HTTPException(
#                 status_code=500,
#                 detail="PDF uploaded but failed to build knowledge base"
#             )
#             
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error uploading PDF: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StatsResponse)
async def get_knowledge_base_stats():
    """Get statistics about the knowledge base"""
    try:
        stats = kb_service.get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Check if knowledge base service is healthy"""
    try:
        stats = kb_service.get_stats()
        
        return {
            "status": "healthy",
            "service": "Knowledge Base Service",
            "knowledge_base_status": stats.get('status', 'unknown'),
            "ollama_model": kb_service.model_name,
            "embedding_model": kb_service.embedding_model
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.delete("/reset")
async def reset_knowledge_base():
    """
    Reset/delete the knowledge base
    
    WARNING: This will delete all stored embeddings and require rebuilding.
    """
    try:
        kb_service.client.delete_collection("cse_annual_report_2024")
        kb_service.collection = None
        
        return {
            "status": "success",
            "message": "Knowledge base has been reset"
        }
    except Exception as e:
        logger.error(f"Error resetting knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))
