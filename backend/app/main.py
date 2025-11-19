from fastapi import FastAPI
from app.Database.mongo_client import MongoClient

app = FastAPI()
mongo_client = MongoClient()



@app.get("/")
def read_root():
    return {"message": "Sentiment Trading Bot API is running "}


@app.on_event("startup")
async def startup():
    await mongo_client.connect()

@app.on_event("shutdown")
async def shutdown():
    await mongo_client.close()

@app.get("/users")
async def get_users():
    db = mongo_client.get_db
    users = await db["users"].find().to_list(100)
    return users


