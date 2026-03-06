// Export all types
export * from './chat.types';

// Sentiment-specific types
export interface SentimentData {
  symbol: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  score: number;
  volume: number;
  sources: number;
  timestamp: string;
  keywords?: string[];
}

export interface ChatMessage {
  id: string;
  message: string;
  isUser: boolean;
  timestamp: string;
  sources?: any[];
  metadata?: any;
}

export interface ChatRequest {
  message: string;
  conversationId?: string;
  context?: any;
}
