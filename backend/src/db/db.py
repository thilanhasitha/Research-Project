from motor.motor_asyncio import AsyncIOMotorClient

# Database name added here
MONGO_URI = "mongodb+srv://ravi:ravi@cluster0.sc4zaj7.mongodb.net/pumpdumpdb?appName=Cluster0"

# Now, the motor client will default to this database:
client = AsyncIOMotorClient(MONGO_URI)

# This line now formally selects the database defined in the URI path:
db = client["pumpdumpdb"]