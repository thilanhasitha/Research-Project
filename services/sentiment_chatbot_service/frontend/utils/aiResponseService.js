// utils/aiResponseService.js
import { getUserId } from "./userManagementService";

// API configuration
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

// Use a module-level variable to cache the conversation ID for better state management
let currentConversationId = null;

// Get current conversation ID from cache or session
export const getConversationId = () => {
  if (!currentConversationId) {
    currentConversationId = sessionStorage.getItem('current_chat_id');
  }
  return currentConversationId;
};

// Set conversation ID in cache and session
export const setConversationId = (chatId) => {
  if (chatId) {
    currentConversationId = chatId;
    sessionStorage.setItem('current_chat_id', chatId);
  }
};

// Clear current conversation from cache and session
export const clearCurrentConversation = () => {
  currentConversationId = null;
  sessionStorage.removeItem('current_chat_id');
  console.log('[CONVERSATION] Cleared current conversation ID');
};

// Start a new conversation - properly clears state and gets new ID from backend
export const startNewConversation = async () => {
  try {
    const userId = getUserId();
    if (!userId) {
      // If no user, just clear local state as before
      clearCurrentConversation();
      console.log('[CONVERSATION] Started new conversation locally (no user).');
      return null;
    }

  } catch (error) {
    console.error('[CONVERSATION] Error starting new conversation via API:', error);
    // Fallback to clearing local state if the API call fails
    clearCurrentConversation();
    return null;
  }
};

// Check if we should start fresh (called on component mount)
export const shouldStartFresh = () => {
  // You can add logic here to determine if conversation should persist
  // For now, we'll keep conversations persistent across refreshes
  return false;
};

// Initialize conversation state (call this when app loads)
export const initializeConversationState = () => {
  const existingId = getConversationId();
  if (existingId) {
    console.log('[CONVERSATION] Resuming conversation:', existingId);
    return existingId;
  }
  console.log('[CONVERSATION] No existing conversation');
  return null;
};

// Get all user conversations
export const getUserConversations = async (limit = 20) => {
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

// Load a specific conversation
export const loadConversation = async (chatId) => {
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
    const formattedMessages = rawMessages.map(msg => {
      return {
        id: msg.timestamp,
        message: msg.content,           // <--- Map 'content' to 'message'
        isUser: msg.role === 'user',    // <--- Map 'role' to 'isUser'
        timestamp: msg.timestamp,       // <--- Pass the ISO string
        products: (msg.metadata && msg.metadata.products) ? msg.metadata.products : null // <--- Map 'metadata.products' to 'products'
      };
    });
    
    return formattedMessages;

  } catch (error) {
    console.error('[LOAD_CONVERSATION] Error:', error);
    return [];
  }
};



// Delete a conversation
export const deleteConversation = async (chatId) => {
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

// utils/aiResponseService.js - Add these new functions

// ... existing code ...

// NEW: Confirm cart addition with selected variants
export const confirmCartAddition = async (itemId, variety, color) => {
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
        // Send variant data directly in metadata
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

// Update createMessage to support variantData
export const createMessage = (message, isUser = false, products = null, variantData = null) => {
  return {
    id: Date.now() + Math.random(),
    message: message,
    isUser: isUser,
    timestamp: new Date().toISOString(),
    products: products,
    variantData: variantData  // NEW
  };
};

// Update generateAIResponse to return variantData
export const generateAIResponse = async (userMessage, actionType = null) => {
  try {
    const response = await callBackendAPI(userMessage);

    return {
      message: response.message,
      needsMoreInfo: response.needsMoreInfo,
      products: response.products,
      showAddToCart: response.showAddToCart,
      conversationId: response.conversationId,
      variantData: response.variantData // NEW
    };

  } catch (error) {
    console.error('[CHAT] AI Response Generation Error:', error);
    console.log('[CHAT] Falling back to offline responses...');

    let fallbackMessage;
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
      variantData: null // NEW
    };
  }
};

// Update callBackendAPI to handle variantData
const callBackendAPI = async (message) => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

    const payload = {
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

// Add to cart
export const addToCart = async (productId, quantity = 1) => {
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
const quickActionResponses = {
  track_order: "I'd be happy to help you track your order! Please provide your order number.",
  product_info: "I can help you find detailed information about any product. What are you looking for?",
  payment_help: "I'm here to assist with payment questions. What do you need help with?",
  return_policy: "Our return policy allows returns within 30 days. Would you like to start a return?"
};

const getContextualResponse = (message) => {
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



// Utility functions
export const getResponseDelay = () => {
  return 500 + Math.random() * 1000;
};

export const getCurrentTimestamp = () => {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};


export const testBackendConnection = async () => {
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
  } catch (error) {
    console.error('[HEALTH_CHECK] Error:', error);
    return { status: 'error', message: error.message };
  }
};