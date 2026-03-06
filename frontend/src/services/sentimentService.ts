import axios from 'axios';
import type { SentimentData, ChatMessage, ChatRequest } from '../modules/sentiment/types';

// Use direct axios instance for news-chat endpoints
const newsApi = axios.create({
  baseURL: '/news-chat',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const sentimentService = {
  // Get sentiment analysis for a topic or symbol
  getSentiment: async (topic?: string, days: number = 7): Promise<SentimentData> => {
    const response = await newsApi.post('/sentiment', {
      topic,
      days,
    });
    
    const result = response.data;
    
    // Transform backend response to match SentimentData type
    return {
      symbol: topic || 'MARKET',
      sentiment: result.overall_sentiment || 'neutral',
      score: result.sentiment_score || 0,
      volume: result.total_articles || 0,
      sources: result.total_articles || 0,
      timestamp: new Date().toISOString(),
      keywords: result.topics || [],
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
