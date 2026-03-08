/**
 * Plot Service
 * Service for searching and retrieving plot visualizations
 */

// Define types for the Plot objects
export interface PlotInfo {
  id: string;
  title: string;
  type: string;
  description?: string;
  url?: string;
  created_at?: string;
}

export interface PlotSearchResponse {
  success: boolean;
  plots: PlotInfo[];
  error?: string;
}

const API_BASE_URL: string = (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8001/api';

export const plotService = {
  /**
   * Search for plots based on a query
   */
  async searchPlots(query: string, limit: number = 5): Promise<PlotSearchResponse> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/plots/search?query=${encodeURIComponent(query)}&limit=${limit}`
      );
      
      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }
      
      const data: PlotSearchResponse = await response.json();
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('Plot search error:', error);
      return { success: false, plots: [], error: errorMessage };
    }
  },

  /**
   * Get plot image URL
   */
  getPlotImageUrl(plotId: string): string {
    return `${API_BASE_URL}/plots/${plotId}/image`;
  },

  /**
   * Get plot details
   */
  async getPlotInfo(plotId: string): Promise<PlotInfo | null> {
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
  isPlotQuery(query: string): boolean {
    const plotKeywords: string[] = [
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