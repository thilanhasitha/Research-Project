"""
FastAPI Integration for Plot Retrieval
=======================================
Add this to your existing FastAPI backend to serve plots with RAG responses.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.plot_manager import PlotManager

app = FastAPI()

# Initialize plot manager
plot_manager = PlotManager()

# Mount plots directory for static file serving
plots_dir = Path("data/plots")
if plots_dir.exists():
    app.mount("/plots", StaticFiles(directory=str(plots_dir)), name="plots")


class QueryRequest(BaseModel):
    """Request model for queries."""
    query: str
    max_plots: Optional[int] = 3
    category: Optional[str] = None


class PlotInfo(BaseModel):
    """Plot information model."""
    plot_id: str
    title: str
    description: str
    image_url: str
    relevance_score: int


class QueryResponse(BaseModel):
    """Response model for queries."""
    query: str
    text_response: str
    plots: List[PlotInfo]
    has_plots: bool


@app.get("/api/plots/search")
async def search_plots(query: str, limit: int = 5, category: Optional[str] = None):
    """
    Search for plots based on a query.
    
    Args:
        query: Search query
        limit: Maximum number of results
        category: Filter by category (optional)
    """
    try:
        results = plot_manager.search_plots(query, category=category, limit=limit)
        
        # Convert file paths to URLs
        for result in results:
            filename = Path(result["filepath"]).name
            result["image_url"] = f"/plots/{filename}"
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plots/{plot_id}")
async def get_plot(plot_id: str):
    """Get a specific plot by ID."""
    try:
        plot = plot_manager.get_plot_by_id(plot_id)
        
        if not plot:
            raise HTTPException(status_code=404, detail="Plot not found")
        
        # Add image URL
        filename = Path(plot["filepath"]).name
        plot["image_url"] = f"/plots/{filename}"
        
        return {
            "success": True,
            "plot": plot
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plots/{plot_id}/image")
async def get_plot_image(plot_id: str):
    """Serve the plot image file."""
    try:
        plot = plot_manager.get_plot_by_id(plot_id)
        
        if not plot:
            raise HTTPException(status_code=404, detail="Plot not found")
        
        filepath = Path(plot["filepath"])
        
        if not filepath.exists():
            raise HTTPException(status_code=404, detail="Plot file not found")
        
        return FileResponse(filepath, media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plots/categories")
async def get_categories():
    """Get all available plot categories."""
    try:
        categories = plot_manager.get_categories()
        return {
            "success": True,
            "categories": categories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plots/category/{category}")
async def get_plots_by_category(category: str):
    """Get all plots in a specific category."""
    try:
        plots = plot_manager.get_all_plots(category=category)
        
        # Add image URLs
        for plot in plots:
            filename = Path(plot["filepath"]).name
            plot["image_url"] = f"/plots/{filename}"
        
        return {
            "success": True,
            "category": category,
            "plots": plots,
            "count": len(plots)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plots/stats")
async def get_plot_stats():
    """Get statistics about stored plots."""
    try:
        stats = plot_manager.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query")
async def process_query(request: QueryRequest):
    """
    Process a user query and return both text response and relevant plots.
    
    This endpoint combines your existing RAG system with plot retrieval.
    """
    try:
        # Search for relevant plots
        plot_results = plot_manager.search_plots(
            request.query, 
            category=request.category,
            limit=request.max_plots
        )
        
        # Convert to response format
        plots = []
        for result in plot_results:
            filename = Path(result["filepath"]).name
            plots.append(PlotInfo(
                plot_id=result["plot_id"],
                title=result["title"],
                description=result["description"],
                image_url=f"/plots/{filename}",
                relevance_score=result["relevance_score"]
            ))
        
        # TODO: Integrate with your existing RAG system here
        # text_response = your_rag_system.query(request.query)
        text_response = f"This is where your RAG system response would go for: {request.query}"
        
        return QueryResponse(
            query=request.query,
            text_response=text_response,
            plots=plots,
            has_plots=len(plots) > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Plot Retrieval API",
        "endpoints": {
            "search": "/api/plots/search?query=<query>",
            "get_plot": "/api/plots/{plot_id}",
            "get_image": "/api/plots/{plot_id}/image",
            "categories": "/api/plots/categories",
            "by_category": "/api/plots/category/{category}",
            "stats": "/api/plots/stats",
            "query": "/api/query (POST)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    print("Starting Plot Retrieval API...")
    print("Visit http://localhost:8005/docs for API documentation")
    
    uvicorn.run(app, host="0.0.0.0", port=8005)
