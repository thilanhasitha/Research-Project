// newsRAGService.ts
// Service for interacting with the News RAG API

// Types and Interfaces
export interface NewsArticle {
  id?: string;
  title: string;
  content: string;
  url?: string;
  source?: string;
  published_date?: string;
  sentiment?: number;
  [key: string]: any;
}

export interface NewsSource {
  title: string;
  url?: string;
  source?: string;
  published_date?: string;
  relevance_score?: number;
}

export interface AskQuestionOptions {
  userId?: string;
  conversationId?: string | null;
  includeSources?: boolean;
  contextLimit?: number;
  useCache?: boolean;
  requestId?: string | null;
}

export interface AskQuestionResponse {
  success: boolean;
  answer?: string;
  sources?: NewsSource[];
  contextUsed?: number;
  timestamp?: string;
  metadata?: any;
  error?: string;
}

export interface SearchNewsOptions {
  limit?: number;
  sentimentFilter?: number | null;
  days?: number | null;
  useCache?: boolean;
}

export interface SearchNewsResponse {
  success: boolean;
  articles?: NewsArticle[];
  error?: string;
}

export interface TrendingNewsResponse {
  success: boolean;
  trending?: NewsArticle[];
  periodDays?: number;
  count?: number;
  error?: string;
}

export interface SentimentAnalysisOptions {
  topic?: string | null;
  days?: number;
}

export interface SentimentAnalysisResponse {
  success: boolean;
  topic?: string;
  totalArticles?: number;
  averageSentiment?: number;
  sentimentDistribution?: any;
  error?: string;
  [key: string]: any;
}

export interface HealthCheckResponse {
  success: boolean;
  status?: string;
  weaviateConnected?: boolean;
  healthy?: boolean;
  error?: string;
}

export interface StatsResponse {
  success: boolean;
  totalArticles?: number;
  last30Days?: number;
  error?: string;
}

// API Configuration
const API_CONFIG = {
  baseURL: '',
  endpoints: {
    ask: '/news-chat/ask',
    search: '/news-chat/search',
    trending: '/news-chat/trending',
    sentiment: '/news-chat/sentiment',
    health: '/news-chat/health',
    stats: '/news-chat/stats',
    latest: '/news-chat/latest'
  },
  timeout: 30000
};

// Cache configuration
interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

const cache = new Map<string, CacheEntry<any>>();
const CACHE_TTL = 60000; // 1 minute

// Active request tracking
const activeRequests = new Map<string, AbortController>();

/**
 * Get cached data if available and not expired
 */
const getFromCache = <T>(key: string): T | null => {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data as T;
  }
  cache.delete(key);
  return null;
};

/**
 * Store data in cache
 */
const setCache = <T>(key: string, data: T): void => {
  cache.set(key, { data, timestamp: Date.now() });
  // Auto-cleanup old cache entries
  if (cache.size > 50) {
    const firstKey = cache.keys().next().value;
    if (firstKey) {
      cache.delete(firstKey);
    }
  }
};

/**
 * Cancel an active request
 */
export const cancelRequest = (requestId: string): void => {
  const controller = activeRequests.get(requestId);
  if (controller) {
    controller.abort();
    activeRequests.delete(requestId);
  }
};

/**
 * Ask a question using RAG - retrieves relevant news and generates contextual answer
 */
export const askQuestion = async (
  message: string,
  options: AskQuestionOptions = {}
): Promise<AskQuestionResponse> => {
  try {
    const {
      userId = 'anonymous',
      conversationId = null,
      includeSources = true,
      contextLimit = 3,
      useCache = true,
      requestId = null
    } = options;

    // Check cache first
    const cacheKey = `ask:${message}:${contextLimit}`;
    if (useCache) {
      const cached = getFromCache<AskQuestionResponse>(cacheKey);
      if (cached) {
        console.log('[NEWS RAG] Cache hit for question');
        return cached;
      }
    }

    // Create abort controller for this request
    const controller = new AbortController();
    if (requestId) {
      activeRequests.set(requestId, controller);
    }

    const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.ask}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        user_id: userId,
        conversation_id: conversationId,
        include_sources: includeSources,
        context_limit: contextLimit
      }),
      signal: controller.signal
    });

    // Cleanup request tracking
    if (requestId) {
      activeRequests.delete(requestId);
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    console.log('[NEWS RAG] Question answered:', {
      contextUsed: data.context_used,
      sourcesCount: data.sources?.length || 0
    });

    const result: AskQuestionResponse = {
      success: true,
      answer: data.message,
      sources: data.sources || [],
      contextUsed: data.context_used,
      timestamp: data.timestamp,
      metadata: data.metadata
    };

    // Cache successful response
    if (useCache) {
      setCache(cacheKey, result);
    }

    return result;
  } catch (error: any) {
    console.error('[NEWS RAG] Error asking question:', error);
    
    // Cleanup on error
    if (options.requestId) {
      activeRequests.delete(options.requestId);
    }
    
    if (error.name === 'AbortError') {
      return {
        success: false,
        error: 'Request was cancelled or timed out. Please try again.',
        answer: undefined
      };
    }

    return {
      success: false,
      error: error.message || 'Failed to get answer from RAG service',
      answer: undefined
    };
  }
};

/**
 * Search for news articles using semantic search
 */
export const searchNews = async (
  query: string,
  options: SearchNewsOptions = {}
): Promise<SearchNewsResponse> => {
  try {
    const {
      limit = 10,
      sentimentFilter = null,
      days = null,
      useCache = true
    } = options;

    // Check cache first
    const cacheKey = `search:${query}:${limit}:${sentimentFilter}:${days}`;
    if (useCache) {
      const cached = getFromCache<SearchNewsResponse>(cacheKey);
      if (cached) {
        console.log('[NEWS RAG] Cache hit for search');
        return cached;
      }
    }

    const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.search}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        limit,
        sentiment_filter: sentimentFilter,
        days
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const articles: NewsArticle[] = await response.json();
    console.log('[NEWS RAG] Search completed:', { resultsCount: articles.length });
    
    const result: SearchNewsResponse = {
      success: true,
      articles
    };

    // Cache successful search
    if (useCache) {
      setCache(cacheKey, result);
    }

    return result;
  } catch (error: any) {
    console.error('[NEWS RAG] Error searching news:', error);
    return {
      success: false,
      error: error.message,
      articles: []
    };
  }
};

/**
 * Get trending news articles
 */
export const getTrendingNews = async (
  days: number = 7,
  limit: number = 10
): Promise<TrendingNewsResponse> => {
  try {
    const response = await fetch(
      `${API_CONFIG.baseURL}${API_CONFIG.endpoints.trending}?days=${days}&limit=${limit}`
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('[NEWS RAG] Trending news fetched:', { count: data.count });
    
    return {
      success: true,
      trending: data.trending,
      periodDays: data.period_days,
      count: data.count
    };
  } catch (error: any) {
    console.error('[NEWS RAG] Error getting trending news:', error);
    return {
      success: false,
      error: error.message,
      trending: []
    };
  }
};

/**
 * Get sentiment analysis for a topic or overall market
 */
export const analyzeSentiment = async (
  options: SentimentAnalysisOptions = {}
): Promise<SentimentAnalysisResponse> => {
  try {
    const {
      topic = null,
      days = 7
    } = options;

    const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.sentiment}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        topic,
        days
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('[NEWS RAG] Sentiment analysis completed:', {
      topic: data.topic,
      totalArticles: data.total_articles
    });
    
    return {
      success: true,
      ...data
    };
  } catch (error: any) {
    console.error('[NEWS RAG] Error analyzing sentiment:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

/**
 * Check health status of the news RAG service
 */
export const checkHealth = async (): Promise<HealthCheckResponse> => {
  try {
    const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.health}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: true,
      status: data.status,
      weaviateConnected: data.weaviate_connected,
      healthy: data.status === 'healthy'
    };
  } catch (error: any) {
    console.error('[NEWS RAG] Health check failed:', error);
    return {
      success: false,
      healthy: false,
      error: error.message
    };
  }
};

/**
 * Get statistics about the news database
 */
export const getStats = async (): Promise<StatsResponse> => {
  try {
    const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.stats}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: true,
      totalArticles: data.total_articles,
      last30Days: data.last_30_days
    };
  } catch (error: any) {
    console.error('[NEWS RAG] Error getting stats:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

/**
 * Get latest news articles
 */
export const getLatestNews = async (limit: number = 10): Promise<SearchNewsResponse> => {
  try {
    const response = await fetch(
      `${API_CONFIG.baseURL}${API_CONFIG.endpoints.latest}?limit=${limit}`
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('[NEWS RAG] Latest news fetched:', { count: data.count });
    
    return {
      success: true,
      articles: data.results || []
    };
  } catch (error: any) {
    console.error('[NEWS RAG] Error getting latest news:', error);
    return {
      success: false,
      error: error.message,
      articles: []
    };
  }
};

export default {
  askQuestion,
  searchNews,
  getTrendingNews,
  getLatestNews,
  analyzeSentiment,
  checkHealth,
  getStats,
  cancelRequest
};
