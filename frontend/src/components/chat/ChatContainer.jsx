import React, { useState, useEffect } from 'react';
import ChatFloatingButton from './ChatFloatingButton';
import ChatPanel from './ChatPanel';
import {
  generateAIResponse,
  testBackendConnection,
  getCurrentTimestamp,
  startNewConversation,
  getConversationId,
  clearCurrentConversation,
  loadConversation as loadConversationFromAPI
} from '../../utils/aiResponseService';

const ChatContainer = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      message: "Hello! I'm your stock market assistant. How can I help you today?",
      isUser: false,
      timestamp: getCurrentTimestamp(),
      products: null
    }
  ]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('unknown');
  const [error, setError] = useState(null);
  const [currentConversationId, setCurrentConversationId] = useState(null);

  useEffect(() => {
    checkConnection();
  }, []);

  useEffect(() => {
    const existingConversationId = getConversationId();
    if (existingConversationId) {
      setCurrentConversationId(existingConversationId);
      console.log('[CHAT] Resuming conversation:', existingConversationId);
    }
  }, []);

  const checkConnection = async () => {
    try {
      const result = await testBackendConnection();
      setConnectionStatus(result.status === 'connected' ? 'connected' : 'disconnected');
    } catch (error) {
      setConnectionStatus('disconnected');
    }
  };

  const handleSendMessage = async () => {
    if (newMessage.trim() === '' || isTyping) return;

    const userMessage = {
      id: Date.now(),
      message: newMessage,
      isUser: true,
      timestamp: getCurrentTimestamp(),
      products: null
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = newMessage;
    setNewMessage('');
    setIsTyping(true);
    setError(null);

    try {
      const response = await generateAIResponse(messageToSend);
      
      if (response.conversationId) {
        setCurrentConversationId(response.conversationId);
      }

      const aiMessage = {
        id: Date.now() + 1,
        message: response.message,
        isUser: false,
        timestamp: getCurrentTimestamp(),
        products: response.products
      };

      setMessages(prev => [...prev, aiMessage]);
      setConnectionStatus('connected');
    } catch (error) {
      console.error('[CHAT] Error:', error);
      setError(error.message || 'Failed to send message');
      setConnectionStatus('disconnected');
      
      const errorMessage = {
        id: Date.now() + 1,
        message: "I'm having trouble connecting right now. Please try again.",
        isUser: false,
        timestamp: getCurrentTimestamp(),
        products: null
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleQuickAction = async (actionType, actionLabel) => {
    const quickMessages = {
      track_order: "I need help tracking my order",
      product_info: "Can you tell me more about your products?",
      payment_help: "I have a question about payment",
      return_policy: "What's your return policy?"
    };

    const message = quickMessages[actionType] || actionLabel;
    setNewMessage(message);
    
    setTimeout(() => {
      if (message) {
        setNewMessage(message);
        setTimeout(handleSendMessage, 100);
      }
    }, 100);
  };

 

const handleNewConversation = async () => {
    try {
        const newConversationId = await startNewConversation();
        setCurrentConversationId(newConversationId);
        setMessages([
          {
            id: Date.now(),
            message: "Hello! I'm your stock market assistant. How can I help you today?",
            isUser: false,
            timestamp: getCurrentTimestamp(),
            products: null
          }
        ]);
        setError(null);
        console.log('[CHAT] Started new conversation with ID:', newConversationId);
    } catch (error) {
        console.error("Failed to start new conversation", error);
        setError("Could not start a new chat session.");
    }
  };

  const handleLoadConversation = async (chatId, conversationMessages) => {
    try {
      setCurrentConversationId(chatId);
      
      if (conversationMessages && conversationMessages.length > 0) {
        const formattedMessages = conversationMessages.map((msg, idx) => ({
          id: idx,
          message: msg.content,
          isUser: msg.role === 'user',
          timestamp: msg.timestamp 
            ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            : getCurrentTimestamp(),
          products: msg.metadata?.product_ids ? [] : null
        }));
        setMessages(formattedMessages);
      } else {
        const loadedMessages = await loadConversationFromAPI(chatId);
        const formattedMessages = loadedMessages.map((msg, idx) => ({
          id: idx,
          message: msg.content,
          isUser: msg.role === 'user',
          timestamp: msg.timestamp 
            ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            : getCurrentTimestamp(),
          products: msg.metadata?.product_ids ? [] : null
        }));
        setMessages(formattedMessages);
      }
      
      console.log('[CHAT] Loaded conversation:', chatId);
    } catch (error) {
      console.error('[CHAT] Error loading conversation:', error);
      setError('Failed to load conversation');
    }
  };

  const handleRetry = () => {
    setError(null);
    checkConnection();
  };

  return (
    <>
      <ChatFloatingButton
        onClick={() => setIsChatOpen(true)}
        isVisible={!isChatOpen}
        connectionStatus={connectionStatus}
      />

      <ChatPanel
        isOpen={isChatOpen}
        messages={messages}
        newMessage={newMessage}
        setNewMessage={setNewMessage}
        isTyping={isTyping}
        onClose={() => setIsChatOpen(false)}
        onSendMessage={handleSendMessage}
        onQuickAction={handleQuickAction}
        onNewConversation={handleNewConversation}
        connectionStatus={connectionStatus}
        error={error}
        onRetry={handleRetry}
        currentConversationId={currentConversationId}
        onLoadConversation={handleLoadConversation}
      />
    </>
  );
};

export default ChatContainer;