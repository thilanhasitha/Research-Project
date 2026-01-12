"""
Quick script to check MongoDB for latest news articles
"""
from pymongo import MongoClient
from datetime import datetime

try:
    # Connect to MongoDB
    client = MongoClient('mongodb+srv://research:user@cluster0.sc4zaj7.mongodb.net/research_db?appName=Cluster0')
    db = client['research_db']
    collection = db['rss_news']
    
    # Get total count
    total = collection.count_documents({})
    print(f"\n{'='*60}")
    print(f"MONGODB NEWS STATUS")
    print(f"{'='*60}")
    print(f"Total articles in database: {total}")
    
    # Get latest articles
    print(f"\n{'='*60}")
    print(f"LATEST 5 ARTICLES")
    print(f"{'='*60}\n")
    
    latest = collection.find().sort("published", -1).limit(5)
    
    for idx, article in enumerate(latest, 1):
        print(f"{idx}. {article.get('title', 'No title')}")
        print(f"   Published: {article.get('published', 'No date')}")
        print(f"   Link: {article.get('link', 'No link')}")
        if 'created_at' in article:
            print(f"   Added to DB: {article['created_at']}")
        print()
    
    # Get articles from last 24 hours
    from datetime import timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_count = collection.count_documents({"created_at": {"$gte": yesterday}})
    print(f"{'='*60}")
    print(f"Articles added in last 24 hours: {recent_count}")
    print(f"{'='*60}\n")
    
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
