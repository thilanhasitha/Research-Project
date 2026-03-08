import { valuationApi } from './api';
import type { StockValuation, ValuationRequest } from '../modules/valuation/types';
import type { ApiResponse } from '../shared/types/common';

export const valuationService = {
  // Get stock valuation by symbol
  getValuation: async (symbol: string): Promise<StockValuation> => {
    const response = await valuationApi.get<ApiResponse<StockValuation>>(`/valuation/${symbol}`);
    return response.data.data;
  },

  // Calculate intrinsic value with custom parameters
  calculateValuation: async (request: ValuationRequest): Promise<StockValuation> => {
    const response = await valuationApi.post<ApiResponse<StockValuation>>('/valuation/calculate', request);
    return response.data.data;
  },

  // Get multiple stock valuations
  getMultipleValuations: async (symbols: string[]): Promise<StockValuation[]> => {
    const response = await valuationApi.post<ApiResponse<StockValuation[]>>('/valuation/batch', { symbols });
    return response.data.data;
  },
};
