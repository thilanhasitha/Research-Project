// aiResponseService.ts
// Service for managing AI chat conversations and message handling

// Types and Interfaces
export interface Message {
  id: number;
  message: string;
  isUser: boolean;
  timestamp: string;
  products?: Product[] | null;
  variantData?: VariantData | null;
}

export interface Product {
  id: string;
  name: string;
  price?: number;
  description?: string;
  [key: string]: any;
}

export interface VariantData {
  itemId: string;
  variety?: string;
  color?: string;
  [key: string]: any;
}

export interface APIResponse {
  message: string;
  conversationId?: string;
  products?: Product[] | null;
  needsMoreInfo?: boolean;
  showAddToCart?: boolean;
  variantData?: VariantData | null;
  reply?: string;
  response?: string;
  conversation_id?: string;
  variant_data?: VariantData | null;
}

export interface Conversation {
  id: string;
  title: string;
  lastMessage?: string;
  timestamp: number;
  userId: string;
}

export interface HealthCheckResponse {
  status: string;
  message: string;
}

// API Configuration
const API_CONFIG = {
  baseURL: '',
  endpoints: {
    chat: '/chat/message',
    conversations: '/chat/conversations',
    history: '/chat/history',
    deleteConversation: '/chat/conversation',
    health: '/health'
  },
  timeout: 15000
};

// Module-level variable to cache the conversation ID
let currentConversationId: string | null = null;

/**
 * Generate a unique user ID (fallback if no user management system)
 */
const getUserId = (): string => {
  let userId = sessionStorage.getItem('user_id');
  if (!userId) {
    userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('user_id', userId);
  }
  return userId;
};

/**
 * Get current conversation ID from cache or session
 */
export const getConversationId = (): string | null => {
  if (!currentConversationId) {
    currentConversationId = sessionStorage.getItem('current_chat_id');
  }
  return currentConversationId;
};

/**
 * Set conversation ID in cache and session
 */
export const setConversationId = (chatId: string | null): void => {
  if (chatId) {
    currentConversationId = chatId;
    sessionStorage.setItem('current_chat_id', chatId);
  }
};

/**
 * Clear current conversation from cache and session
 */
export const clearCurrentConversation = (): void => {
  currentConversationId = null;
  sessionStorage.removeItem('current_chat_id');
  console.log('[CONVERSATION] Cleared current conversation ID');
};

/**
 * Start a new conversation
 */
export const startNewConversation = async (): Promise<string | null> => {
  try {
    const userId = getUserId();
    if (!userId) {
      clearCurrentConversation();
      console.log('[CONVERSATION] Started new conversation locally (no user).');
      return null;
    }
    
    clearCurrentConversation();
    return null;
  } catch (error) {
    console.error('[CONVERSATION] Error starting new conversation via API:', error);
    clearCurrentConversation();
    return null;
  }
};

/**
 * Initialize conversation state (call when app loads)
 */
export const initializeConversationState = (): string | null => {
  const existingId = getConversationId();
  if (existingId) {
    console.log('[CONVERSATION] Resuming conversation:', existingId);
    return existingId;
  }
  console.log('[CONVERSATION] No existing conversation');
  return null;
};

/**
 * Get all user conversations
 */
export const getUserConversations = async (limit: number = 20): Promise<Conversation[]> => {
  try {
    const userId = getUserId();
    const response = await fetch(
      `${API_CONFIG.baseURL}${API_CONFIG.endpoints.conversations}/${userId}?limit=${limit}`
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.conversations || [];
  } catch (error) {
    console.error('[CONVERSATIONS] Error:', error);
    return [];
  }
};

/**
 * Load a specific conversation
 */
export const loadConversation = async (chatId: string): Promise<Message[]> => {
  try {
    const userId = getUserId();
    const response = await fetch(
      `${API_CONFIG.baseURL}${API_CONFIG.endpoints.history}/${chatId}?user_id=${userId}`
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    const rawMessages = data.messages || [];

    // Map backend format to frontend format
    const formattedMessages: Message[] = rawMessages.map((msg: any) => ({
      id: msg.timestamp,
      message: msg.content,
      isUser: msg.role === 'user',
      timestamp: msg.timestamp,
      products: msg.metadata?.products || null
    }));
    
    return formattedMessages;
  } catch (error) {
    console.error('[LOAD_CONVERSATION] Error:', error);
    return [];
  }
};

/**
 * Delete a conversation
 */
export const deleteConversation = async (chatId: string): Promise<any> => {
  try {
    const userId = getUserId();
    const response = await fetch(
      `${API_CONFIG.baseURL}${API_CONFIG.endpoints.deleteConversation}/${chatId}?user_id=${userId}`,
      { method: 'DELETE' }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // If we deleted the current conversation, clear it
    if (getConversationId() === chatId) {
      clearCurrentConversation();
    }

    return await response.json();
  } catch (error) {
    console.error('[DELETE_CONVERSATION] Error:', error);
    throw error;
  }
};

/**
 * Confirm cart addition with selected variants
 */
export const confirmCartAddition = async (
  itemId: string,
  variety: string,
  color: string
): Promise<{ success: boolean; message: string }> => {
  try {
    const userId = getUserId();
    const conversationId = getConversationId();

    const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.chat}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: `Confirm add to cart: ${variety}, ${color}`,
        user_id: userId,
        conversation_id: conversationId,
        metadata: {
          action: 'confirm_cart_addition',
          item_id: itemId,
          variety: variety,
          color: color
        }
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    return {
      success: true,
      message: data.reply || "Item added to cart successfully!"
    };
  } catch (error) {
    console.error('[CONFIRM_CART] Error:', error);
    throw error;
  }
};

/**
 * Create a message object
 */
export const createMessage = (
  message: string,
  isUser: boolean = false,
  products: Product[] | null = null,
  variantData: VariantData | null = null
): Message => {
  return {
    id: Date.now() + Math.random(),
    message: message,
    isUser: isUser,
    timestamp: new Date().toISOString(),
    products: products,
    variantData: variantData
  };
};

/**
 * Call backend API
 */
const callBackendAPI = async (message: string): Promise<APIResponse> => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

    const payload: any = {
      message: message,
      user_id: getUserId()
    };

    const conversationId = getConversationId();
    if (conversationId) {
      payload.conversation_id = conversationId;
    }
    
    console.log('[CHAT] Sending message:', payload);

    const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.chat}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.conversation_id) {
      setConversationId(data.conversation_id);
    }

    console.log('[CHAT] Received response:', data);

    return {
      message: data.response || data.reply || "I received your message but couldn't process it properly.",
      conversationId: data.conversation_id,
      products: data.products || null,
      needsMoreInfo: data.needsMoreInfo || false,
      showAddToCart: data.showAddToCart || false,
      variantData: data.variant_data || null
    };
  } catch (error) {
    console.error('[CHAT] Backend API Error:', error);
    throw error;
  }
};

/**
 * Generate AI response
 */
export const generateAIResponse = async (
  userMessage: string,
  actionType: string | null = null
): Promise<APIResponse> => {
  try {
    const response = await callBackendAPI(userMessage);
    return response;
  } catch (error) {
    console.error('[CHAT] AI Response Generation Error:', error);
    console.log('[CHAT] Falling back to offline responses...');

    let fallbackMessage: string;
    if (actionType && quickActionResponses[actionType]) {
      fallbackMessage = quickActionResponses[actionType];
    } else {
      fallbackMessage = getContextualResponse(userMessage);
    }

    return {
      message: fallbackMessage,
      needsMoreInfo: false,
      products: null,
      showAddToCart: false,
      variantData: null
    };
  }
};

/**
 * Add to cart
 */
export const addToCart = async (
  productId: string,
  quantity: number = 1
): Promise<{ success: boolean; message: string }> => {
  try {
    const userId = getUserId();

    const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.chat}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: `Add item ${productId} to cart with quantity ${quantity}`,
        user_id: userId,
        conversation_id: getConversationId()
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: true,
      message: data.reply
    };
  } catch (error) {
    console.error('[ADD_TO_CART] Error:', error);
    return {
      success: false,
      message: 'Failed to add item to cart'
    };
  }
};

// Fallback responses
const quickActionResponses: { [key: string]: string } = {
  track_order: "I'd be happy to help you track your order! Please provide your order number.",
  product_info: "I can help you find detailed information about any product. What are you looking for?",
  payment_help: "I'm here to assist with payment questions. What do you need help with?",
  return_policy: "Our return policy allows returns within 30 days. Would you like to start a return?"
};

const getContextualResponse = (message: string): string => {
  const lowerMessage = message.toLowerCase();

  if (lowerMessage.includes('price') || lowerMessage.includes('cost')) {
    return "I can help you find pricing information! Which product are you interested in?";
  }

  if (lowerMessage.includes('shipping') || lowerMessage.includes('delivery')) {
    return "We offer free shipping on orders over $50! Standard delivery takes 3-5 business days.";
  }

  if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
    return "Hello! I'm here to help with any questions. How can I assist you today?";
  }

  return "I'm here to help! Can you tell me more about what you're looking for?";
};

/**
 * Utility functions
 */
export const getResponseDelay = (): number => {
  return 500 + Math.random() * 1000;
};

export const getCurrentTimestamp = (): string => {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

/**
 * Test backend connection
 */
export const testBackendConnection = async (): Promise<HealthCheckResponse> => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

    const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.health}`, {
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`Health check failed with status: ${response.status}`);
    }

    const data = await response.json();
    if (data.status === 'ok') {
      return { status: 'connected', message: 'Backend is reachable' };
    } else {
      throw new Error('Backend health check returned an invalid status.');
    }
  } catch (error: any) {
    console.error('[HEALTH_CHECK] Error:', error);
    return { status: 'error', message: error.message };
  }
};

export default {
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
  testBackendConnection
};
