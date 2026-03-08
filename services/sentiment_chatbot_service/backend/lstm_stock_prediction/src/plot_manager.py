"""
Plot Manager Module
===================
Manages saving and retrieving visualization plots for the RAG system.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlotManager:
    """Manage storage and retrieval of visualization plots."""
    
    def __init__(self, plots_dir: str = "data/plots", index_file: str = "data/plots/plot_index.json"):
        """
        Initialize the PlotManager.
        
        Args:
            plots_dir: Directory to store plot images
            index_file: Path to the plot index JSON file
        """
        self.plots_dir = Path(plots_dir)
        self.plots_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = Path(index_file)
        self.plot_index = self._load_index()
        
    def _load_index(self) -> Dict:
        """Load the plot index from file."""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                return json.load(f)
        return {"plots": [], "metadata": {"created": str(datetime.now()), "total_plots": 0}}
    
    def _save_index(self):
        """Save the plot index to file."""
        self.plot_index["metadata"]["total_plots"] = len(self.plot_index["plots"])
        self.plot_index["metadata"]["last_updated"] = str(datetime.now())
        
        with open(self.index_file, 'w') as f:
            json.dump(self.plot_index, indent=2, fp=f)
        logger.info(f"Plot index saved to {self.index_file}")
    
    def save_plot(self, 
                  plot_id: str,
                  title: str,
                  description: str,
                  keywords: List[str],
                  category: str = "general",
                  fig: Optional[plt.Figure] = None,
                  dpi: int = 300) -> str:
        """
        Save a matplotlib plot with metadata.
        
        Args:
            plot_id: Unique identifier for the plot
            title: Plot title
            description: Detailed description of what the plot shows
            keywords: List of keywords for searching
            category: Category of the plot (e.g., "price", "volume", "correlation")
            fig: Matplotlib figure object (if None, uses current figure)
            dpi: Resolution for saved image
            
        Returns:
            Path to the saved plot file
        """
        # Generate filename
        filename = f"{plot_id}.png"
        filepath = self.plots_dir / filename
        
        # Save the plot
        if fig is None:
            plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
        else:
            fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
        
        logger.info(f"Plot saved to {filepath}")
        
        # Add to index
        plot_entry = {
            "plot_id": plot_id,
            "filename": filename,
            "filepath": str(filepath),
            "title": title,
            "description": description,
            "keywords": keywords,
            "category": category,
            "created_at": str(datetime.now()),
            "file_size_kb": round(filepath.stat().st_size / 1024, 2) if filepath.exists() else 0
        }
        
        # Remove existing entry if it exists
        self.plot_index["plots"] = [p for p in self.plot_index["plots"] if p["plot_id"] != plot_id]
        
        # Add new entry
        self.plot_index["plots"].append(plot_entry)
        self._save_index()
        
        return str(filepath)
    
    def search_plots(self, query: str, category: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """
        Search for plots based on a text query.
        
        Args:
            query: Search query
            category: Filter by category (optional)
            limit: Maximum number of results
            
        Returns:
            List of matching plot entries with relevance scores
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        results = []
        
        for plot in self.plot_index["plots"]:
            # Filter by category if specified
            if category and plot.get("category") != category:
                continue
            
            # Calculate relevance score
            score = 0
            
            # Check title (high weight)
            if query_lower in plot["title"].lower():
                score += 10
            
            # Check description (medium weight)
            if query_lower in plot["description"].lower():
                score += 5
            
            # Check keywords (high weight)
            for keyword in plot.get("keywords", []):
                if keyword.lower() in query_lower:
                    score += 7
                if keyword.lower() in query_words:
                    score += 5
            
            # Word matching in title and description
            text = f"{plot['title']} {plot['description']}".lower()
            matching_words = sum(1 for word in query_words if word in text)
            score += matching_words * 2
            
            if score > 0:
                results.append({
                    **plot,
                    "relevance_score": score
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return results[:limit]
    
    def get_plot_by_id(self, plot_id: str) -> Optional[Dict]:
        """
        Get plot entry by ID.
        
        Args:
            plot_id: Plot identifier
            
        Returns:
            Plot entry dictionary or None if not found
        """
        for plot in self.plot_index["plots"]:
            if plot["plot_id"] == plot_id:
                return plot
        return None
    
    def get_all_plots(self, category: Optional[str] = None) -> List[Dict]:
        """
        Get all plots, optionally filtered by category.
        
        Args:
            category: Filter by category (optional)
            
        Returns:
            List of plot entries
        """
        if category:
            return [p for p in self.plot_index["plots"] if p.get("category") == category]
        return self.plot_index["plots"]
    
    def get_categories(self) -> List[str]:
        """Get list of unique categories."""
        return list(set(p.get("category", "general") for p in self.plot_index["plots"]))
    
    def delete_plot(self, plot_id: str) -> bool:
        """
        Delete a plot and its metadata.
        
        Args:
            plot_id: Plot identifier
            
        Returns:
            True if deleted, False if not found
        """
        plot = self.get_plot_by_id(plot_id)
        if not plot:
            return False
        
        # Delete file
        filepath = Path(plot["filepath"])
        if filepath.exists():
            filepath.unlink()
            logger.info(f"Deleted plot file: {filepath}")
        
        # Remove from index
        self.plot_index["plots"] = [p for p in self.plot_index["plots"] if p["plot_id"] != plot_id]
        self._save_index()
        
        return True
    
    def get_stats(self) -> Dict:
        """Get statistics about stored plots."""
        total_plots = len(self.plot_index["plots"])
        categories = self.get_categories()
        total_size_mb = sum(p.get("file_size_kb", 0) for p in self.plot_index["plots"]) / 1024
        
        category_counts = {}
        for cat in categories:
            category_counts[cat] = len([p for p in self.plot_index["plots"] if p.get("category") == cat])
        
        return {
            "total_plots": total_plots,
            "total_size_mb": round(total_size_mb, 2),
            "categories": categories,
            "plots_per_category": category_counts,
            "index_file": str(self.index_file)
        }


# Example usage
if __name__ == "__main__":
    # Initialize plot manager
    pm = PlotManager()
    
    # Example: Search for plots
    results = pm.search_plots("stock price change over time")
    print(f"\nSearch results for 'stock price change over time':")
    for result in results:
        print(f"  - {result['title']} (score: {result['relevance_score']})")
    
    # Get statistics
    stats = pm.get_stats()
    print(f"\nPlot Statistics:")
    print(f"  Total plots: {stats['total_plots']}")
    print(f"  Total size: {stats['total_size_mb']} MB")
    print(f"  Categories: {stats['categories']}")
