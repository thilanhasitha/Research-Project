import { fraudApi } from './api';
import { FraudAlert, TradingPattern } from '../modules/fraud/types';
import { ApiResponse, PaginatedResponse } from '../shared/types/common';

export const fraudService = {
  // Get active fraud alerts
  getAlerts: async (page = 1, limit = 10): Promise<PaginatedResponse<FraudAlert>> => {
    const response = await fraudApi.get<ApiResponse<PaginatedResponse<FraudAlert>>>(
      `/alerts?page=${page}&limit=${limit}`
    );
    return response.data.data;
  },

  // Get fraud alerts for specific stock
  getAlertsBySymbol: async (symbol: string): Promise<FraudAlert[]> => {
    const response = await fraudApi.get<ApiResponse<FraudAlert[]>>(`/alerts/${symbol}`);
    return response.data.data;
  },

  // Get trading patterns
  getTradingPatterns: async (symbol: string): Promise<TradingPattern[]> => {
    const response = await fraudApi.get<ApiResponse<TradingPattern[]>>(`/patterns/${symbol}`);
    return response.data.data;
  },

  // Update alert status
  updateAlertStatus: async (alertId: string, status: string): Promise<void> => {
    await fraudApi.patch(`/alerts/${alertId}`, { status });
  },
};
