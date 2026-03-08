/**
 * Plot Service
 * Service for searching and retrieving plot visualizations
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api';

export const plotService = {
  /**
   * Search for plots based on a query
   */
  async searchPlots(query, limit = 5) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/plots/search?query=${encodeURIComponent(query)}&limit=${limit}`
      );
      
      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Plot search error:', error);
      return { success: false, plots: [], error: error.message };
    }
  },

  /**
   * Get plot image URL
   */
  getPlotImageUrl(plotId) {
    return `${API_BASE_URL}/plots/${plotId}/image`;
  },

  /**
   * Get plot details
   */
  async getPlotInfo(plotId) {
    try {
      const response = await fetch(`${API_BASE_URL}/plots/${plotId}`);
      if (!response.ok) {
        throw new Error(`Failed to get plot info: ${response.statusText}`);
      }
      const data = await response.json();
      return data.plot;
    } catch (error) {
      console.error('Get plot info error:', error);
      return null;
    }
  },

  /**
   * Check if query is plot-related
   */
  isPlotQuery(query) {
    const plotKeywords = [
      'plot', 'chart', 'graph', 'visualize', 'visualization', 'show',
      'display', 'price', 'volume', 'volatility', 'correlation', 'returns',
      'moving average', 'distribution', 'OHLC', 'candlestick', 'trend',
      'pattern', 'technical', 'indicator'
    ];
    
    const lowerQuery = query.toLowerCase();
    return plotKeywords.some(keyword => lowerQuery.includes(keyword));
  }
};

export default plotService;
