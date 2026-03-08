import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://ravi:ravi@cluster0.sc4zaj7.mongodb.net/pumpdumpdb?appName=Cluster0")

client = AsyncIOMotorClient(MONGO_URI)
db = client["pumpdumpdb"]