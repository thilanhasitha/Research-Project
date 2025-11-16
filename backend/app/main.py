from fastapi import FastAPI
from app.routes.ollama_routes import router as ollama_router

app = FastAPI()
app.include_router(ollama_router)

@app.get("/")
def read_root():
    return {"message": "Sentiment Trading Bot API is running "}


