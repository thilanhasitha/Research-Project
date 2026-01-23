// utils/newsRAGService.js
// Service for interacting with the News RAG API

const API_CONFIG = {
  baseURL: '/api',  // Proxied through nginx to backend
  endpoints: {
    ask: '/news-chat/ask',
    search: '/news-chat/search',
    trending: '/news-chat/trending',
    sentiment: '/news-chat/sentiment',
    health: '/news-chat/health',
    stats: '/news-chat/stats'
  },
  timeout: 30000 // 30 seconds - faster timeout for better UX
};

// Simple in-memory cache for faster repeated queries
const cache = new Map();
const CACHE_TTL = 60000; // 1 minute cache

// Active request tracking for cancellation
const activeRequests = new Map();

/**
 * Get cached data if available and not expired
 */
const getFromCache = (key) => {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }
  cache.delete(key);
  return null;
};

/**
 * Store data in cache
 */
const setCache = (key, data) => {
  cache.set(key, { data, timestamp: Date.now() });
  // Auto-cleanup old cache entries
  if (cache.size > 50) {
    const firstKey = cache.keys().next().value;
    cache.delete(firstKey);
  }
};

/**
 * Cancel an active request
 */
export const cancelRequest = (requestId) => {
  const controller = activeRequests.get(requestId);
  if (controller) {
    controller.abort();
    activeRequests.delete(requestId);
  }
};

/**
 * Ask a question using RAG - retrieves relevant news and generates contextual answer
 * @param {string} message - User's question
 * @param {Object} options - Optional parameters
 * @returns {Promise<Object>} Response with answer, sources, and metadata
 */
export const askQuestion = async (message, options = {}) => {
  try {
    const {
      userId = 'anonymous',
      conversationId = null,
      includeSources = true,
      contextLimit = 3, // Reduced from 5 for faster response
      useCache = true,
      requestId = null
    } = options;

    // Check cache first
    const cacheKey = `ask:${message}:${contextLimit}`;
    if (useCache) {
      const cached = getFromCache(cacheKey);
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

    // Set timeout separately
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    clearTimeout(timeoutId);
    
    console.log('[NEWS RAG] Question answered:', {
      contextUsed: data.context_used,
      sourcesCount: data.sources?.length || 0
    });

    const result = {
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

  } catch (error) {
    console.error('[NEWS RAG] Error asking question:', error);
    
    // Cleanup on error
    if (options.requestId) {
      activeRequests.delete(options.requestId);
    }
    
    if (error.name === 'AbortError') {
      return {
        success: false,
        error: 'Request was cancelled or timed out. Please try again.',
        answer: null
      };
    }

    return {
      success: false,
      error: error.message || 'Failed to get answer from RAG service',
      answer: null
    };
  }
};

/**
 * Search for news articles using semantic search
 * @param {string} query - Search query
 * @param {Object} options - Optional filters
 * @returns {Promise<Array>} Array of news articles
 */
export const searchNews = async (query, options = {}) => {
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
      const cached = getFromCache(cacheKey);
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

    const articles = await response.json();
    console.log('[NEWS RAG] Search completed:', { resultsCount: articles.length });
    
    const result = {
      success: true,
      articles
    };

    // Cache successful search
    if (useCache) {
      setCache(cacheKey, result);
    }

    return result;

  } catch (error) {
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
 * @param {number} days - Number of days to look back (default: 7)
 * @param {number} limit - Maximum results (default: 10)
 * @returns {Promise<Object>} Trending news data
 */
export const getTrendingNews = async (days = 7, limit = 10) => {
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

  } catch (error) {
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
 * @param {Object} options - Analysis options
 * @returns {Promise<Object>} Sentiment analysis results
 */
export const analyzeSentiment = async (options = {}) => {
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

  } catch (error) {
    console.error('[NEWS RAG] Error analyzing sentiment:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

/**
 * Check health status of the news RAG service
 * @returns {Promise<Object>} Health status
 */
export const checkHealth = async () => {
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

  } catch (error) {
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
 * @returns {Promise<Object>} Database statistics
 */
export const getStats = async () => {
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

  } catch (error) {
    console.error('[NEWS RAG] Error getting stats:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

export default {
  askQuestion,
  searchNews,
  getTrendingNews,
  analyzeSentiment,
  checkHealth,
  getStats
};
