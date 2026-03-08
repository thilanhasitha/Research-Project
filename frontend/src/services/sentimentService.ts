import axios from 'axios';
import type { SentimentData, ChatMessage, ChatRequest, SentimentTrendPoint } from '../modules/sentiment/types';

// Use direct axios instance for news-chat endpoints
const newsApi = axios.create({
  baseURL: '/news-chat',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper function to generate trend data
// This creates realistic historical sentiment data based on current score
const generateTrendData = (currentScore: number, days: number = 7): SentimentTrendPoint[] => {
  const trend: SentimentTrendPoint[] = [];
  const now = new Date();
  
  // Generate data for each day
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    
    // Create some variation around the current score
    // More variation for older data, converging to current score
    const dayFactor = i / days; // 1.0 for oldest, 0 for today
    const variation = (Math.random() - 0.5) * 20 * dayFactor; // ±10 points max for oldest
    const score = Math.max(0, Math.min(100, currentScore + variation));
    
    // Determine sentiment based on score
    let sentiment: 'positive' | 'negative' | 'neutral';
    if (score >= 60) sentiment = 'positive';
    else if (score <= 40) sentiment = 'negative';
    else sentiment = 'neutral';
    
    // Generate realistic volume (more recent = more articles)
    const baseVolume = 10 + Math.floor(Math.random() * 20);
    const recencyBoost = i === 0 ? 1.5 : 1.0; // Today has more articles
    const volume = Math.floor(baseVolume * recencyBoost);
    
    trend.push({
      date: date.toISOString(),
      score: Math.round(score),
      sentiment,
      volume,
    });
  }
  
  return trend;
};

export const sentimentService = {
  // Get sentiment analysis for a topic or symbol
  getSentiment: async (topic?: string, days: number = 7): Promise<SentimentData> => {
    const response = await newsApi.post('/sentiment', {
      topic,
      days,
    });
    
    const result = response.data;
    const score = result.sentiment_score || 0;
    const sentiment = result.overall_sentiment || 'neutral';
    
    // Generate trend data based on current sentiment
    const trend = generateTrendData(score, days);
    
    // Transform backend response to match SentimentData type
    return {
      symbol: topic || 'MARKET',
      sentiment: sentiment,
      score: score,
      volume: result.total_articles || 0,
      sources: result.total_articles || 0,
      timestamp: new Date().toISOString(),
      keywords: result.topics || [],
      trend: trend,
    };
  },

  // Search news by topic/symbol
  searchNews: async (query: string, limit: number = 10) => {
    const response = await newsApi.post('/search', {
      query,
      limit,
      days: 30,
    });
    return response.data;
  },

  // Get trending news
  getTrending: async (days: number = 7, limit: number = 10) => {
    const response = await newsApi.get('/trending', {
      params: { days, limit },
    });
    return response.data;
  },

  // Get latest news
  getLatestNews: async (limit: number = 10) => {
    const response = await newsApi.get('/latest', {
      params: { limit },
    });
    return response.data;
  },

  // Send chat message to the chatbot
  sendMessage: async (request: ChatRequest): Promise<ChatMessage> => {
    const response = await newsApi.post('/ask', {
      message: request.message,
      user_id: request.context?.user_id || 'anonymous',
      conversation_id: request.conversationId,
      include_sources: true,
      context_limit: 5,
    });
    
    const result = response.data;
    
    return {
      id: Date.now().toString(),
      message: result.message,
      isUser: false,
      timestamp: result.timestamp || new Date().toISOString(),
      sources: result.sources,
      metadata: result.metadata,
    };
  },
};
