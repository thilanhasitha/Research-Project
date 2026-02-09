import React, { useState, useEffect } from 'react';
import ChatFloatingButton from './ChatFloatingButton';
import ChatPanel from './ChatPanel';
import ChatHistory from './ChatHistory';
import { askQuestion, checkHealth } from '../../../utils/newsRAGService';

// Create a message object
const createMessage = (text, isUser = false, sources = null, metadata = null) => ({
  message: text,
  isUser,
  sources,
  metadata,
  timestamp: Date.now(),
});

// Generate unique ID for conversations
const generateId = () => `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

const AIChat = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [messages, setMessages] = useState([
    createMessage("Hi! I'm your financial news assistant. I can help you with the latest news, market trends, and sentiment analysis. How can I help you today?", false)
  ]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [error, setError] = useState(null);

  // Load conversations from localStorage on mount
  useEffect(() => {
    const savedConversations = localStorage.getItem('chatConversations');
    if (savedConversations) {
      try {
        const parsed = JSON.parse(savedConversations);
        setConversations(parsed);
      } catch (err) {
        console.error('Failed to parse saved conversations:', err);
      }
    }
  }, []);

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('chatConversations', JSON.stringify(conversations));
    }
  }, [conversations]);

  // Save current conversation when messages change
  useEffect(() => {
    if (currentConversationId && messages.length > 0) {
      setConversations(prev => {
        const existing = prev.find(c => c.id === currentConversationId);
        if (existing) {
          return prev.map(c => 
            c.id === currentConversationId 
              ? { ...c, messages, updatedAt: Date.now() }
              : c
          );
        } else {
          // Create new conversation
          return [...prev, {
            id: currentConversationId,
            messages,
            createdAt: Date.now(),
            updatedAt: Date.now()
          }];
        }
      });
    }
  }, [messages, currentConversationId]);

  // Check backend connection on mount
  useEffect(() => {
    const verifyConnection = async () => {
      try {
        const health = await checkHealth();
        if (health.success && health.healthy) {
          setConnectionStatus('connected');
        } else {
          setConnectionStatus('disconnected');
          setError('Unable to connect to the news service');
        }
      } catch (err) {
        setConnectionStatus('disconnected');
        setError('News service is offline');
      }
    };

    verifyConnection();
  }, []);

  // Reset unread count when chat opens
  useEffect(() => {
    if (isOpen) {
      setUnreadCount(0);
      setError(null);
    }
  }, [isOpen]);

 
  // Get AI response using RAG pipeline
  const getAIResponse = async (userMessage) => {
    setIsTyping(true);
    setError(null);

    try {
      // Call the RAG API
      const response = await askQuestion(userMessage, {
        userId: 'anonymous',
        includeSources: true,
        contextLimit: 3  // Reduced from 5 to 3 for faster responses
      });

      setIsTyping(false);

      if (response.success) {
        const aiMessage = createMessage(
          response.answer,
          false,
          response.sources,
          {
            contextUsed: response.contextUsed,
            timestamp: response.timestamp
          }
        );

        setMessages(prev => [...prev, aiMessage]);

        if (!isOpen) {
          setUnreadCount(prev => prev + 1);
        }
      } else {
        // Handle error
        const errorMessage = createMessage(
          response.error || "Sorry, I couldn't process your request. Please try again.",
          false
        );
        setMessages(prev => [...prev, errorMessage]);
        setError(response.error);
      }

    } catch (err) {
      setIsTyping(false);
      const errorMessage = createMessage(
        "I'm having trouble connecting to the news service. Please try again later.",
        false
      );
      setMessages(prev => [...prev, errorMessage]);
      setError(err.message);
      console.error('[AIChat] Error:', err);
    }
  };

 
  const handleSendMessage = () => {
    if (newMessage.trim() === '' || isTyping) return;

    const userMessage = createMessage(newMessage, true);
    setMessages(prev => [...prev, userMessage]);

    const text = newMessage;
    setNewMessage('');

    getAIResponse(text);
  };

  /* Quick actions for common queries */
  const handleQuickAction = (action, label) => {
    if (isTyping) return;

    const userMessage = createMessage(label, true);
    setMessages(prev => [...prev, userMessage]);

    getAIResponse(label);
  };

  /* Start new conversation */
  const handleNewConversation = () => {
    const newConvId = generateId();
    setCurrentConversationId(newConvId);
    setMessages([
      createMessage("Hi! I'm your financial news assistant. I can help you with the latest news, market trends, and sentiment analysis. How can I help you today?", false)
    ]);
    setError(null);
    setIsHistoryOpen(false);
  };

  /* Select existing conversation */
  const handleSelectConversation = (conversationId) => {
    const conversation = conversations.find(c => c.id === conversationId);
    if (conversation) {
      setCurrentConversationId(conversationId);
      setMessages(conversation.messages);
      setError(null);
      setIsHistoryOpen(false);
    }
  };

  /* Delete conversation */
  const handleDeleteConversation = (conversationId) => {
    setConversations(prev => prev.filter(c => c.id !== conversationId));
    
    // If deleting current conversation, start a new one
    if (conversationId === currentConversationId) {
      handleNewConversation();
    }
  };

  /* Toggle chat history sidebar */
  const handleToggleHistory = () => {
    setIsHistoryOpen(!isHistoryOpen);
  };

  const toggleChat = () => setIsOpen(!isOpen);
  const handleClose = () => {
    setIsOpen(false);
    setIsHistoryOpen(false);
  };

  // Initialize first conversation if none exists
  useEffect(() => {
    if (!currentConversationId) {
      const newConvId = generateId();
      setCurrentConversationId(newConvId);
    }
  }, [currentConversationId]);

  return (
    <>
      {!isOpen && (
        <ChatFloatingButton
          onClick={toggleChat}
          unreadCount={unreadCount}
          connectionStatus={connectionStatus} 
        />
      )}

      <ChatHistory
        isOpen={isHistoryOpen}
        conversations={conversations.sort((a, b) => b.updatedAt - a.updatedAt)}
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
      />

      <ChatPanel
        isOpen={isOpen}
        messages={messages}
        newMessage={newMessage}
        setNewMessage={setNewMessage}
        isTyping={isTyping}
        onClose={handleClose}
        onSendMessage={handleSendMessage}
        onQuickAction={handleQuickAction}
        onNewConversation={handleNewConversation}
        onToggleHistory={handleToggleHistory}
        isHistoryOpen={isHistoryOpen}
        connectionStatus={connectionStatus}
        error={error}
      />
    </>
  );
};

export default AIChat;
