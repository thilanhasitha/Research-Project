"""
Run this inside the backend container to clean fake news
Save as: /tmp/clean_news.py
"""
from pymongo import MongoClient

# Connect to MongoDB with correct credentials
client = MongoClient('mongodb://mongo:27017/', username='research', password='user', authSource='admin')
db = client['research_db']
collection = db['rss_news']

print("="*60)
print("CLEANING FAKE NEWS FROM MONGODB")
print("="*60)

# Fake titles to delete
fake_titles = [
    'Bitcoin Surges Past Record High',
    'Breaking News',
    'Tech Innovation',
    'Real-time Test',
    'Innovation in AI'
]

# Fake URL patterns
fake_urls = ['crypto.com', 'tech.com', 'news.com', 'test.com']

total_deleted = 0

print("\n1. Deleting by title...")
for title in fake_titles:
    result = collection.delete_many({'title': title})
    if result.deleted_count > 0:
        print(f"   ✓ Deleted {result.deleted_count} x '{title}'")
    total_deleted += result.deleted_count

print("\n2. Deleting by URL pattern...")
for pattern in fake_urls:
    result = collection.delete_many({'link': {'$regex': pattern}})
    if result.deleted_count > 0:
        print(f"   ✓ Deleted {result.deleted_count} articles with '{pattern}'")
    total_deleted += result.deleted_count

remaining = collection.count_documents({})

print(f"\n{'='*60}")
print(f"RESULTS:")
print(f"  - Total deleted: {total_deleted}")
print(f"  - Remaining articles: {remaining}")
print(f"{'='*60}")

# Show sample
print("\nSample of remaining articles:")
for i, article in enumerate(collection.find().sort('created_at', -1).limit(3), 1):
    print(f"  {i}. {article.get('title', 'No title')}")
    print(f"     {article.get('link', 'No link')[:60]}...")

client.close()
