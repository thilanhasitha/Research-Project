// index.ts
// Central export file for all utility services

// Export specific items from aiResponseService
export { 
  getConversationId,
  setConversationId,
  clearCurrentConversation,
  startNewConversation,
  initializeConversationState,
  getUserConversations,
  loadConversation,
  deleteConversation,
  confirmCartAddition,
  createMessage,
  generateAIResponse,
  addToCart,
  getResponseDelay,
  getCurrentTimestamp,
  testBackendConnection,
  type Message,
  type Product,
  type VariantData,
  type APIResponse,
  type Conversation,
  type HealthCheckResponse as AIHealthCheckResponse
} from './aiResponseService';

// Export specific items from newsRAGService
export {
  askQuestion,
  searchNews,
  getTrendingNews,
  analyzeSentiment,
  cancelRequest as cancelNewsRequest,
  checkHealth as checkNewsHealth,
  getStats as getNewsStats,
  type NewsArticle,
  type NewsSource,
  type AskQuestionOptions,
  type AskQuestionResponse,
  type SearchNewsOptions,
  type SearchNewsResponse,
  type TrendingNewsResponse,
  type SentimentAnalysisOptions,
  type SentimentAnalysisResponse,
  type HealthCheckResponse as NewsHealthCheckResponse,
  type StatsResponse as NewsStatsResponse
} from './newsRAGService';

// Export specific items from knowledgeBaseService
export {
  queryKnowledgeBase,
  getQuickActionQuestion,
  checkHealth as checkKBHealth,
  getStats as getKBStats,
  cancelRequest as cancelKBRequest,
  clearCache as clearKBCache,
  type QueryKnowledgeBaseOptions,
  type QueryKnowledgeBaseResponse,
  type HealthCheckResponse as KBHealthCheckResponse,
  type StatsResponse as KBStatsResponse
} from './knowledgeBaseService';
export { default as knowledgeBaseService } from './knowledgeBaseService';
