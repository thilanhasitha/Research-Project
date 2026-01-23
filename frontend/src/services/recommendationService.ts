import { recommendationApi } from './api';
import { StockRecommendation, RecommendationRequest } from '../modules/recommendation/types';
import { ApiResponse } from '../shared/types/common';

export const recommendationService = {
  // Get personalized recommendations
  getRecommendations: async (request?: RecommendationRequest): Promise<StockRecommendation[]> => {
    const response = await recommendationApi.post<ApiResponse<StockRecommendation[]>>(
      '/recommendations',
      request || {}
    );
    return response.data.data;
  },

  // Get recommendation for specific stock
  getStockRecommendation: async (symbol: string): Promise<StockRecommendation> => {
    const response = await recommendationApi.get<ApiResponse<StockRecommendation>>(
      `/recommendations/${symbol}`
    );
    return response.data.data;
  },

  // Get top recommendations
  getTopRecommendations: async (limit = 5): Promise<StockRecommendation[]> => {
    const response = await recommendationApi.get<ApiResponse<StockRecommendation[]>>(
      `/recommendations/top?limit=${limit}`
    );
    return response.data.data;
  },
};
