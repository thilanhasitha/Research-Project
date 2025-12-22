from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from app.Database.mongo_client import MongoClient
from app.routes.rss_routes import router as rss_router
from app.routes.chat_routes import router as chat_router
from app.routes.news_chat_routes import router as news_chat_router
# from app.routes.rag_routes import router as rag_router
from app.llm.client.ollama_client import OllamaClient
from app.llm.LLMFactory import LLMFactory 


app = FastAPI(
    title="Trading Sentiment Bot",
    description="AI-powered financial news analysis and trading sentiment bot with RAG capabilities",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

@app.get("/")
def read_root():
    return {
        "message": "Trading Sentiment Bot API is running",
        "version": "1.0.0",
        "endpoints": {
            "news_chat": "/news-chat/ask - Chat with AI about financial news",
            "search": "/news-chat/search - Search news articles",
            "trending": "/news-chat/trending - Get trending news",
            "sentiment": "/news-chat/sentiment - Analyze sentiment",
            "health": "/news-chat/health - Service health check"
        }
    }



# Register providers
LLMFactory.register_provider("ollama", OllamaClient)

# Use one LLM for routing (can choose Gemini or Ollama)
router_llm = LLMFactory.get_llm("ollama")

# MongoDB Singleton Instance
mongo_client = MongoClient()

# Register all Routers
app.include_router(rss_router)
app.include_router(chat_router)
app.include_router(news_chat_router)
#app.include_router(rag_router)

@app.on_event("startup")
async def startup():
    # Connect MongoDB
    await mongo_client.connect()
    logger.info("MongoDB connection initialized")

@app.on_event("shutdown")
async def shutdown():
    # Close MongoDB
    await mongo_client.close()
    logger.info("MongoDB connection closed")



