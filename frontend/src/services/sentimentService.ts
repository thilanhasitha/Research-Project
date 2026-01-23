import { sentimentApi } from './api';
import { SentimentData, ChatMessage, ChatRequest } from '../modules/sentiment/types';
import { ApiResponse } from '../shared/types/common';

export const sentimentService = {
  // Get sentiment data for a stock
  getSentiment: async (symbol: string): Promise<SentimentData> => {
    const response = await sentimentApi.get<ApiResponse<SentimentData>>(`/sentiment/${symbol}`);
    return response.data.data;
  },

  // Send chat message to the chatbot
  sendMessage: async (request: ChatRequest): Promise<ChatMessage> => {
    const response = await sentimentApi.post<ApiResponse<ChatMessage>>('/chat', request);
    return response.data.data;
  },

  // Get chat history
  getChatHistory: async (conversationId: string): Promise<ChatMessage[]> => {
    const response = await sentimentApi.get<ApiResponse<ChatMessage[]>>(`/chat/${conversationId}`);
    return response.data.data;
  },
};
