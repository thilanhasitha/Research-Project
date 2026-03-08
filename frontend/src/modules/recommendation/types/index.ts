// Recommendation Service Types

export interface StockRecommendation {
  symbol: string;
  companyName: string;
  action: 'buy' | 'sell' | 'hold';
  confidence: number;
  targetPrice: number;
  currentPrice: number;
  potentialReturn: number;
  reasoning: string;
  risks: string[];
  timestamp: string;
}

export interface RecommendationRequest {
  riskTolerance?: 'low' | 'medium' | 'high';
  investmentHorizon?: 'short' | 'medium' | 'long';
  sectors?: string[];
  excludeSymbols?: string[];
}
