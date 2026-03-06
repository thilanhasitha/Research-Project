"""
PDF RAG Service - Annual Report Q&A
Service layer for handling PDF RAG queries via API
"""

import sys
import os
from typing import Dict, Optional
from pydantic import BaseModel

# Add lstm_stock_prediction to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'lstm_stock_prediction'))

try:
    from pdf_rag_ollama import PDFRagSystem
except ImportError as e:
    print(f"Warning: Could not import PDFRagSystem: {e}")
    PDFRagSystem = None


class QuestionRequest(BaseModel):
    """Request model for PDF questions"""
    question: str
    n_results: Optional[int] = 5
    model: Optional[str] = "llama3.2:latest"
    show_context: Optional[bool] = False


class AnswerResponse(BaseModel):
    """Response model for PDF answers"""
    status: str
    question: str
    answer: str
    chunks_found: int
    model: str
    duration: Optional[float] = None
    context: Optional[str] = None
    error: Optional[str] = None


class PDFRagService:
    """
    Service for handling PDF RAG queries
    """
    
    def __init__(self):
        """Initialize PDF RAG system"""
        self.rag_system = None
        self.initialize()
    
    def initialize(self):
        """Initialize the RAG system"""
        try:
            if PDFRagSystem is None:
                print("❌ PDFRagSystem not available")
                return
            
            # Path to the PDF index
            index_path = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', 
                'lstm_stock_prediction', 
                'pdf_index_data', 
                'pdf_index.json'
            )
            
            self.rag_system = PDFRagSystem(
                index_file=index_path,
                ollama_url="http://localhost:11434"
            )
            print("✓ PDF RAG Service initialized")
            
        except Exception as e:
            print(f"❌ Error initializing PDF RAG Service: {e}")
            self.rag_system = None
    
    async def ask_question(self, request: QuestionRequest) -> AnswerResponse:
        """
        Process a question about the Annual Report
        
        Args:
            request: Question request with parameters
            
        Returns:
            Answer response with AI-generated answer
        """
        if self.rag_system is None:
            return AnswerResponse(
                status="error",
                question=request.question,
                answer="",
                chunks_found=0,
                model=request.model,
                error="PDF RAG system not initialized. Please check if index file exists."
            )
        
        try:
            # Use the RAG system (non-streaming for API)
            result = self.rag_system.ask(
                query=request.question,
                n_results=request.n_results,
                model=request.model,
                show_context=request.show_context,
                stream=False  # Don't stream for API responses
            )
            
            if result['status'] == 'success':
                return AnswerResponse(
                    status="success",
                    question=request.question,
                    answer=result['response'],
                    chunks_found=result['chunks_found'],
                    model=result['model'],
                    duration=result.get('duration'),
                    context=result.get('context') if request.show_context else None
                )
            elif result['status'] == 'no_context':
                return AnswerResponse(
                    status="no_context",
                    question=request.question,
                    answer=result['response'],
                    chunks_found=0,
                    model=request.model,
                    error="No relevant information found in the Annual Report"
                )
            else:
                return AnswerResponse(
                    status="error",
                    question=request.question,
                    answer="",
                    chunks_found=result.get('chunks_found', 0),
                    model=request.model,
                    error=result.get('error', 'Unknown error')
                )
                
        except Exception as e:
            return AnswerResponse(
                status="error",
                question=request.question,
                answer="",
                chunks_found=0,
                model=request.model,
                error=f"Error processing question: {str(e)}"
            )
    
    def health_check(self) -> Dict:
        """Check service health"""
        if self.rag_system is None:
            return {
                "status": "unhealthy",
                "rag_system": "not initialized",
                "ollama": "unknown",
                "index": "unknown"
            }
        
        # Check if index is loaded
        index_loaded = len(self.rag_system.chunks) > 0
        
        # Check Ollama connection
        ollama_connected = self.rag_system.check_ollama()
        
        return {
            "status": "healthy" if (index_loaded and ollama_connected) else "degraded",
            "rag_system": "initialized",
            "ollama": "connected" if ollama_connected else "disconnected",
            "index": {
                "loaded": index_loaded,
                "chunks": len(self.rag_system.chunks) if index_loaded else 0
            }
        }
