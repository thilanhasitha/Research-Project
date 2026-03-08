// knowledgeBaseService.ts
// Service for interacting with the Knowledge Base API (CSE Annual Report)

// Types and Interfaces
export interface QueryKnowledgeBaseOptions {
  userId?: string;
  useCache?: boolean;
  requestId?: string | null;
}

export interface QueryKnowledgeBaseResponse {
  success: boolean;
  answer?: string;
  confidence?: number;
  contexts?: string[];
  timestamp?: number;
  error?: string;
}

export interface HealthCheckResponse {
  success: boolean;
  status?: string;
  knowledgeBaseStatus?: string;
  timestamp?: number;
  error?: string;
}

export interface StatsResponse {
  success: boolean;
  stats?: {
    status: string;
    totalChunks: number;
    model: string;
  };
  timestamp?: number;
  error?: string;
}

// API Configuration
const API_CONFIG = {
  baseURL: '/api',
  endpoints: {
    query: '/knowledge/query',
    health: '/knowledge/health',
    stats: '/knowledge/stats'
  },
  timeout: 30000
};

// Cache configuration
interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

const cache = new Map<string, CacheEntry<any>>();
const CACHE_TTL = 300000; // 5 minutes (knowledge base data changes less frequently)

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
 * Query the knowledge base (CSE Annual Report)
 */
export const queryKnowledgeBase = async (
  question: string,
  options: QueryKnowledgeBaseOptions = {}
): Promise<QueryKnowledgeBaseResponse> => {
  try {
    const {
      userId = 'anonymous',
      useCache = true,
      requestId = null
    } = options;

    // Check cache first
    const cacheKey = `kb:${question}`;
    if (useCache) {
      const cached = getFromCache<QueryKnowledgeBaseResponse>(cacheKey);
      if (cached) {
        console.log('[KNOWLEDGE BASE] Cache hit for question');
        return cached;
      }
    }

    // Create abort controller for this request
    const controller = new AbortController();
    if (requestId) {
      activeRequests.set(requestId, controller);
    }

    const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.query}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        user_id: userId
      }),
      signal: controller.signal
    });

    // Cleanup request tracker
    if (requestId) {
      activeRequests.delete(requestId);
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Transform response to match expected format
    const result: QueryKnowledgeBaseResponse = {
      success: true,
      answer: data.answer || 'No answer available',
      confidence: data.confidence || 0,
      contexts: data.contexts || [],
      timestamp: Date.now()
    };

    // Store in cache
    if (useCache) {
      setCache(cacheKey, result);
    }

    console.log('[KNOWLEDGE BASE] Query successful', {
      question: question.substring(0, 50),
      confidence: result.confidence
    });

    return result;
  } catch (error: any) {
    if (error.name === 'AbortError') {
      console.log('[KNOWLEDGE BASE] Request cancelled');
      return {
        success: false,
        error: 'Request was cancelled'
      };
    }

    console.error('[KNOWLEDGE BASE] Query error:', error);
    return {
      success: false,
      error: error.message || 'Failed to query knowledge base'
    };
  }
};

/**
 * Get predefined answer for quick actions
 */
export const getQuickActionQuestion = (action: string): string => {
  const questions: { [key: string]: string } = {
    cse_highlights: "What are the key highlights from the CSE Annual Report?",
    financial_overview: "Provide a financial overview from the CSE Annual Report.",
    trading_stats: "What are the trading statistics from the CSE Annual Report?",
    risk_analysis: "What are the key risks mentioned in the CSE Annual Report?"
  };
  return questions[action] || action;
};

/**
 * Check if knowledge base service is healthy
 */
export const checkHealth = async (): Promise<HealthCheckResponse> => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.health}`, {
      method: 'GET',
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: true,
      status: data.status,
      knowledgeBaseStatus: data.knowledge_base_status,
      timestamp: Date.now()
    };
  } catch (error: any) {
    console.error('[KNOWLEDGE BASE] Health check error:', error);
    return {
      success: false,
      status: 'unhealthy',
      error: error.message
    };
  }
};

/**
 * Get knowledge base statistics
 */
export const getStats = async (): Promise<StatsResponse> => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.stats}`, {
      method: 'GET',
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`Stats request failed: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: true,
      stats: {
        status: data.status,
        totalChunks: data.total_chunks,
        model: data.model
      },
      timestamp: Date.now()
    };
  } catch (error: any) {
    console.error('[KNOWLEDGE BASE] Stats error:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

/**
 * Clear the cache
 */
export const clearCache = (): void => {
  cache.clear();
  console.log('[KNOWLEDGE BASE] Cache cleared');
};

export default {
  queryKnowledgeBase,
  getQuickActionQuestion,
  checkHealth,
  getStats,
  cancelRequest,
  clearCache
};
