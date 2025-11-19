from fastapi import FastAPI
import logging
import sys
from app.Database.mongo_client import MongoClient

app = FastAPI()

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     handlers=[
#         logging.StreamHandler(sys.stdout),
#         logging.FileHandler("./app/logs/api.log") if "/app/logs" else logging.StreamHandler()
#     ]
# )

logger = logging.getLogger(__name__)


@app.get("/")
def read_root():
    return {"message": "Sentiment Trading Bot API is running "}

mongo_client = MongoClient()

@app.on_event("startup")
async def startup():
    await mongo_client.connect()

@app.on_event("shutdown")
async def shutdown():
    await mongo_client.close()


