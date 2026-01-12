"""
Simple cleanup endpoint - add to routes
"""
from fastapi import APIRouter, HTTPException
from app.Database.repositories.rss_repository import RSSRepository

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.delete("/cleanup-fake-news")
async def cleanup_fake_news():
    """Delete sample/fake news articles from database"""
    try:
        repo = RSSRepository()
        
        fake_titles = [
            'Bitcoin Surges Past Record High',
            'Breaking News',
            'Tech Innovation',
            'Real-time Test',
            'Innovation in AI'
        ]
        
        deleted_count = 0
        
        # Delete by title
        for title in fake_titles:
            result = await repo.collection.delete_many({"title": title})
            deleted_count += result.deleted_count
        
        # Delete by URL pattern
        fake_url_patterns = ['crypto.com', 'tech.com', 'news.com', 'test.com']
        for pattern in fake_url_patterns:
            result = await repo.collection.delete_many({"link": {"$regex": pattern}})
            deleted_count += result.deleted_count
        
        remaining = await repo.collection.count_documents({})
        
        return {
            "success": True,
            "deleted": deleted_count,
            "remaining": remaining,
            "message": f"Deleted {deleted_count} fake articles. {remaining} articles remaining."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
