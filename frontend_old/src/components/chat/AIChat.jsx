import React, { useState, useEffect } from 'react';
import ChatFloatingButton from './ChatFloatingButton';
import ChatPanel from './ChatPanel';
import { askQuestion, checkHealth } from '../../../utils/newsRAGService';

// Create a message object
const createMessage = (text, isUser = false, sources = null, metadata = null) => ({
  message: text,
  isUser,
  sources,
  metadata,
  timestamp: Date.now(),
});

const AIChat = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    createMessage("Hi! I'm your financial news assistant. I can help you with the latest news, market trends, and sentiment analysis. How can I help you today?", false)
  ]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [error, setError] = useState(null);

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
    setMessages([
      createMessage("Hi! I'm your financial news assistant. I can help you with the latest news, market trends, and sentiment analysis. How can I help you today?", false)
    ]);
    setError(null);
  };

  const toggleChat = () => setIsOpen(!isOpen);
  const handleClose = () => setIsOpen(false);

  return (
    <>
      {!isOpen && (
        <ChatFloatingButton
          onClick={toggleChat}
          unreadCount={unreadCount}
          connectionStatus={connectionStatus} 
        />
      )}

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
        connectionStatus={connectionStatus}
        error={error}
      />
    </>
  );
};

export default AIChat;
