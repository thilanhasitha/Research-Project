// Valuation Service Types

export interface StockValuation {
  symbol: string;
  companyName: string;
  currentPrice: number;
  intrinsicValue: number;
  valuation: 'Undervalued' | 'Overvalued' | 'Fair Value';
  discountRate: number;
  growthRate: number;
  fcf: number;
  lastUpdated: string;
}

export interface ValuationRequest {
  symbol: string;
  discountRate?: number;
  growthRate?: number;
}
