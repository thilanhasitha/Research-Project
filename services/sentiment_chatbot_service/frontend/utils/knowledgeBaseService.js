// utils/knowledgeBaseService.js
// Service for interacting with the Knowledge Base API (CSE Annual Report)

const API_CONFIG = {
  baseURL: '/api',  // Proxied through nginx to backend
  endpoints: {
    query: '/knowledge/query',
    health: '/knowledge/health',
    stats: '/knowledge/stats'
  },
  timeout: 30000 // 30 seconds
};

// Simple in-memory cache for faster repeated queries
const cache = new Map();
const CACHE_TTL = 300000; // 5 minutes cache (knowledge base data changes less frequently)

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
 * Query the knowledge base (CSE Annual Report)
 * @param {string} question - User's question
 * @param {Object} options - Optional parameters
 * @returns {Promise<Object>} Response with answer and metadata
 */
export const queryKnowledgeBase = async (question, options = {}) => {
  try {
    const {
      userId = 'anonymous',
      useCache = true,
      requestId = null
    } = options;

    // Check cache first
    const cacheKey = `kb:${question}`;
    if (useCache) {
      const cached = getFromCache(cacheKey);
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
      signal: controller.signal,
      timeout: API_CONFIG.timeout
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
    const result = {
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

  } catch (error) {
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
 * @param {string} action - Quick action type
 * @returns {string} Corresponding question
 */
export const getQuickActionQuestion = (action) => {
  const questions = {
    cse_highlights: "What are the key highlights from the CSE Annual Report?",
    financial_overview: "Provide a financial overview from the CSE Annual Report.",
    trading_stats: "What are the trading statistics from the CSE Annual Report?",
    risk_analysis: "What are the key risks mentioned in the CSE Annual Report?"
  };
  return questions[action] || action;
};

/**
 * Check if knowledge base service is healthy
 * @returns {Promise<Object>} Health status
 */
export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.health}`, {
      method: 'GET',
      timeout: 5000
    });

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
  } catch (error) {
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
 * @returns {Promise<Object>} Statistics about the knowledge base
 */
export const getStats = async () => {
  try {
    const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.stats}`, {
      method: 'GET',
      timeout: 5000
    });

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
  } catch (error) {
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
export const clearCache = () => {
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
