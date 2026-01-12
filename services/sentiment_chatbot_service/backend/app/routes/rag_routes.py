from fastapi import APIRouter
from app.services.rag_chat_service import RAGChatService

router = APIRouter(prefix="/rag")

@router.post("/ask")
async def ask_rag(question: str):
    service: RAGChatService = router.service
    return await service.answer(question)
