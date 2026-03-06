// Fraud Detection Service Types

export interface FraudAlert {
  id: string;
  symbol: string;
  alertType: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  detectedAt: string;
  status: 'active' | 'resolved' | 'investigating';
  confidence: number;
  patterns?: TradingPattern[];
}

export interface TradingPattern {
  id: string;
  symbol: string;
  patternType: string;
  description: string;
  detectedAt: string;
  indicators: Record<string, any>;
  riskLevel: 'low' | 'medium' | 'high';
}
