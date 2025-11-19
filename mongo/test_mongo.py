from pymongo import MongoClient

#uri = "mongodb://yasanjithbgth_db_user:GpFfDZnVGFfJPOeF@localhost:27017/research_db?authSource=admin"

uri = "mongodb+srv://research_user:user@cluster0.ovskpg3.mongodb.net/MyNewDB?appName=Cluster0"

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    print("Connected!")
    print(client.server_info())
except Exception as e:
    print("Connection failed!")
    print(e)