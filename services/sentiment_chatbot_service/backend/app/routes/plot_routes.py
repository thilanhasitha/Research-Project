"""
Plot Retrieval Routes
=====================
API routes for retrieving visualization plots based on user queries.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
import sys
from pathlib import Path

# Add LSTM prediction path to sys.path
lstm_path = Path(__file__).parent.parent.parent / "lstm_stock_prediction"
sys.path.append(str(lstm_path))

try:
    from src.plot_manager import PlotManager
except ImportError as e:
    logging.error(f"Failed to import PlotManager: {e}")
    PlotManager = None

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize PlotManager
if PlotManager:
    plot_manager = PlotManager(
        plots_dir=str(lstm_path / "data" / "plots"),
        index_file=str(lstm_path / "data" / "plots" / "plot_index.json")
    )
else:
    plot_manager = None
    logger.warning("PlotManager not available - plot routes will not work")


class PlotSearchRequest(BaseModel):
    """Request model for plot search."""
    query: str
    category: Optional[str] = None
    limit: Optional[int] = 5


class PlotInfo(BaseModel):
    """Plot information model."""
    plot_id: str
    title: str
    description: str
    image_url: str
    category: str
    keywords: List[str]
    relevance_score: int


class PlotSearchResponse(BaseModel):
    """Response model for plot search."""
    success: bool
    query: str
    plots: List[PlotInfo]
    count: int


@router.get("/plots/health")
async def check_plot_service_health():
    """Check if plot service is healthy."""
    if not plot_manager:
        raise HTTPException(
            status_code=503,
            detail="Plot service not initialized"
        )
    
    try:
        stats = plot_manager.get_stats()
        return {
            "status": "healthy",
            "total_plots": stats["total_plots"],
            "categories": stats["categories"],
            "storage_mb": stats["total_size_mb"]
        }
    except Exception as e:
        logger.error(f"Plot service health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Plot service error: {str(e)}"
        )


@router.post("/plots/search")
async def search_plots(request: PlotSearchRequest):
    """
    Search for plots based on a query.
    
    Args:
        request: PlotSearchRequest with query, optional category, and limit
        
    Returns:
        PlotSearchResponse with matching plots
    """
    if not plot_manager:
        raise HTTPException(
            status_code=503,
            detail="Plot service not available"
        )
    
    try:
        results = plot_manager.search_plots(
            query=request.query,
            category=request.category,
            limit=request.limit
        )
        
        # Convert results to response format
        plots = []
        for result in results:
            plots.append(PlotInfo(
                plot_id=result["plot_id"],
                title=result["title"],
                description=result["description"],
                image_url=f"/api/plots/{result['plot_id']}/image",
                category=result.get("category", "general"),
                keywords=result.get("keywords", []),
                relevance_score=result["relevance_score"]
            ))
        
        return PlotSearchResponse(
            success=True,
            query=request.query,
            plots=plots,
            count=len(plots)
        )
    except Exception as e:
        logger.error(f"Plot search failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Plot search error: {str(e)}"
        )


@router.get("/plots/search")
async def search_plots_get(
    query: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(5, description="Maximum number of results", ge=1, le=20)
):
    """
    Search for plots based on a query (GET version).
    
    Args:
        query: Search query string
        category: Optional category filter
        limit: Maximum number of results (1-20)
        
    Returns:
        PlotSearchResponse with matching plots
    """
    request = PlotSearchRequest(query=query, category=category, limit=limit)
    return await search_plots(request)


@router.get("/plots/{plot_id}")
async def get_plot_info(plot_id: str):
    """Get detailed information about a specific plot."""
    if not plot_manager:
        raise HTTPException(
            status_code=503,
            detail="Plot service not available"
        )
    
    try:
        plot = plot_manager.get_plot_by_id(plot_id)
        
        if not plot:
            raise HTTPException(
                status_code=404,
                detail=f"Plot '{plot_id}' not found"
            )
        
        return {
            "success": True,
            "plot": {
                **plot,
                "image_url": f"/api/plots/{plot_id}/image"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching plot info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching plot: {str(e)}"
        )


@router.get("/plots/{plot_id}/image")
async def get_plot_image(plot_id: str):
    """
    Serve the plot image file.
    
    Args:
        plot_id: Unique plot identifier
        
    Returns:
        Image file
    """
    if not plot_manager:
        raise HTTPException(
            status_code=503,
            detail="Plot service not available"
        )
    
    try:
        plot = plot_manager.get_plot_by_id(plot_id)
        
        if not plot:
            raise HTTPException(
                status_code=404,
                detail=f"Plot '{plot_id}' not found"
            )
        
        filepath = Path(plot["filepath"])
        
        if not filepath.exists():
            raise HTTPException(
                status_code=404,
                detail="Plot file not found on disk"
            )
        
        return FileResponse(
            filepath,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Content-Disposition": f'inline; filename="{plot_id}.png"'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving plot image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error serving image: {str(e)}"
        )


@router.get("/plots/categories")
async def get_categories():
    """Get all available plot categories."""
    if not plot_manager:
        raise HTTPException(
            status_code=503,
            detail="Plot service not available"
        )
    
    try:
        categories = plot_manager.get_categories()
        plots_per_category = {}
        
        for category in categories:
            plots = plot_manager.get_all_plots(category=category)
            plots_per_category[category] = len(plots)
        
        return {
            "success": True,
            "categories": categories,
            "plots_per_category": plots_per_category
        }
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching categories: {str(e)}"
        )


@router.get("/plots/category/{category}")
async def get_plots_by_category(category: str):
    """Get all plots in a specific category."""
    if not plot_manager:
        raise HTTPException(
            status_code=503,
            detail="Plot service not available"
        )
    
    try:
        plots = plot_manager.get_all_plots(category=category)
        
        # Add image URLs
        for plot in plots:
            plot["image_url"] = f"/api/plots/{plot['plot_id']}/image"
        
        return {
            "success": True,
            "category": category,
            "plots": plots,
            "count": len(plots)
        }
    except Exception as e:
        logger.error(f"Error fetching plots by category: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching plots: {str(e)}"
        )


@router.get("/plots/stats")
async def get_plot_stats():
    """Get statistics about stored plots."""
    if not plot_manager:
        raise HTTPException(
            status_code=503,
            detail="Plot service not available"
        )
    
    try:
        stats = plot_manager.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error fetching plot stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching stats: {str(e)}"
        )
