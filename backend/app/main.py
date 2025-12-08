from fastapi import FastAPI
import logging
import sys
from app.Database.mongo_client import MongoClient
from app.routes.rss_routes import router as rss_router
# from app.routes.rag_routes import router as rag_router
from app.llm.client.ollama_client import OllamaClient
from app.llm.LLMFactory import LLMFactory


app = FastAPI(title="Trading Sentiment Bot")

logger = logging.getLogger(__name__)

@app.get("/")
def read_root():
    return {"message": "Sentiment Trading Bot API is running"}



# Register providers
LLMFactory.register_provider("ollama", OllamaClient)

# Use one LLM for routing (can choose Gemini or Ollama)
router_llm = LLMFactory.get_llm("ollama")

# MongoDB Singleton Instance
mongo_client = MongoClient()

# Register all Routers
app.include_router(rss_router)
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