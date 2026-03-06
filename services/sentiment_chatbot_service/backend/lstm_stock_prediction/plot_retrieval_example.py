"""
Plot Retrieval Example
======================
Example of how to integrate plot retrieval with your RAG chatbot.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.plot_manager import PlotManager
from typing import List, Dict, Optional
import json


class PlotRetrievalService:
    """Service for retrieving plots based on user queries."""
    
    def __init__(self):
        self.plot_manager = PlotManager()
        
    def get_relevant_plots(self, user_query: str, max_plots: int = 3) -> List[Dict]:
        """
        Get relevant plots for a user query.
        
        Args:
            user_query: User's question or query
            max_plots: Maximum number of plots to return
            
        Returns:
            List of plot information dictionaries
        """
        # Search for relevant plots
        results = self.plot_manager.search_plots(user_query, limit=max_plots)
        
        # Format results for response
        formatted_results = []
        for result in results:
            formatted_results.append({
                "plot_id": result["plot_id"],
                "title": result["title"],
                "description": result["description"],
                "image_path": result["filepath"],
                "relevance_score": result["relevance_score"]
            })
        
        return formatted_results
    
    def format_plot_response(self, plots: List[Dict]) -> str:
        """
        Format plot results for chatbot response.
        
        Args:
            plots: List of plot dictionaries
            
        Returns:
            Formatted response text
        """
        if not plots:
            return "I couldn't find any relevant visualizations for your query."
        
        response = "Here are relevant visualizations:\n\n"
        
        for i, plot in enumerate(plots, 1):
            response += f"{i}. **{plot['title']}**\n"
            response += f"   {plot['description']}\n"
            response += f"   📊 Image: {plot['image_path']}\n\n"
        
        return response
    
    def handle_query(self, user_query: str) -> Dict:
        """
        Main handler for user queries - returns both text and plots.
        
        Args:
            user_query: User's question
            
        Returns:
            Dictionary with response text and plot information
        """
        # Get relevant plots
        plots = self.get_relevant_plots(user_query, max_plots=3)
        
        # Format response
        response_text = self.format_plot_response(plots)
        
        return {
            "query": user_query,
            "response_text": response_text,
            "plots": plots,
            "has_plots": len(plots) > 0,
            "plot_count": len(plots)
        }


def demo_queries():
    """Demonstrate plot retrieval for common queries."""
    
    service = PlotRetrievalService()
    
    # Example queries users might ask
    example_queries = [
        "How has the stock price changed over the past 20 years?",
        "Show me the trading volume patterns",
        "What is the price volatility?",
        "Can you show me the price distribution?",
        "How do the moving averages look?",
        "What are the daily returns?",
        "Show me correlation between features"
    ]
    
    print("=" * 80)
    print("PLOT RETRIEVAL DEMONSTRATION")
    print("=" * 80)
    
    for query in example_queries:
        print(f"\n{'='*80}")
        print(f"USER QUERY: {query}")
        print('='*80)
        
        result = service.handle_query(query)
        
        print(f"\nResponse:")
        print(result["response_text"])
        
        if result["has_plots"]:
            print(f"\nReturned {result['plot_count']} plot(s)")
            for plot in result["plots"]:
                print(f"  - {plot['title']} (relevance: {plot['relevance_score']})")
        
        print()


def integration_example():
    """Example of how to integrate with your existing RAG chatbot."""
    
    print("\n" + "=" * 80)
    print("INTEGRATION WITH RAG CHATBOT")
    print("=" * 80)
    
    print("""
To integrate plot retrieval with your existing RAG chatbot:

1. Add PlotRetrievalService to your chatbot backend:

   from plot_retrieval_example import PlotRetrievalService
   
   plot_service = PlotRetrievalService()

2. When processing user queries, check for visualization requests:

   def process_query(user_query):
       # Get text response from RAG system
       rag_response = your_rag_system.query(user_query)
       
       # Check for relevant plots
       plot_result = plot_service.handle_query(user_query)
       
       # Combine results
       response = {
           "text": rag_response,
           "plots": plot_result["plots"],
           "has_visuals": plot_result["has_plots"]
       }
       
       return response

3. In your frontend, display both text and images:

   - Show text response from RAG
   - Display plot images if available
   - Add captions with plot descriptions

4. Query patterns that trigger plot retrieval:
   - "show me...", "display...", "visualize..."
   - "how has X changed", "what is the trend"
   - "price", "volume", "volatility", "distribution"
   - "graph", "chart", "plot"
    """)


if __name__ == "__main__":
    # Run demonstration
    demo_queries()
    
    # Show integration example
    integration_example()
    
    print("\n" + "=" * 80)
    print("✓ Plot retrieval system ready!")
    print("=" * 80)
