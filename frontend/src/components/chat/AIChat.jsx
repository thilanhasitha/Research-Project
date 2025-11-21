import React, { useState, useEffect } from 'react';
import ChatFloatingButton from './ChatFloatingButton';
import ChatPanel from './ChatPanel';



// Create a message object
const createMessage = (text, isUser = false, products = null, variantData = null) => ({
  message: text,
  isUser,
  products,
  variantData,
  timestamp: Date.now(),
});

// Random delay for typing effect
const getResponseDelay = () => Math.floor(Math.random() * 700) + 500;

// Generate fake AI responses (frontend only)
const generateFakeResponse = async (text) => {
  const responses = [
    "Sure! Let me help you with that.",
    "Great choice! Would you like to see more similar products?",
    "I’m here to assist you with anything you need!",
    "That’s interesting! Tell me more.",
    "I understand. Let me guide you further."
  ];

  return {
    message: responses[Math.floor(Math.random() * responses.length)],
    products: null,
    variantData: null,
  };
};

const AIChat = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    createMessage("Hi! I'm your shopping assistant. How can I help you today?", false)
  ]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  /* Remove backend connection status */
  const [connectionStatus, setConnectionStatus] = useState('connected');
  const [error, setError] = useState(null);

  // Reset unread count when chat opens
  useEffect(() => {
    if (isOpen) {
      setUnreadCount(0);
      setError(null);
    }
  }, [isOpen]);

 
  const simulateAIResponse = async (userMessage) => {
    setIsTyping(true);

    const delay = getResponseDelay();

    const [aiResponse] = await Promise.all([
      generateFakeResponse(userMessage),
      new Promise(resolve => setTimeout(resolve, delay))
    ]);

    setIsTyping(false);

    const aiMessage = createMessage(
      aiResponse.message,
      false,
      aiResponse.products,
      aiResponse.variantData
    );

    setMessages(prev => [...prev, aiMessage]);

    if (!isOpen) {
      setUnreadCount(prev => prev + 1);
    }
  };

 
  const handleSendMessage = () => {
    if (newMessage.trim() === '' || isTyping) return;

    const userMessage = createMessage(newMessage, true);
    setMessages(prev => [...prev, userMessage]);

    const text = newMessage;
    setNewMessage('');

    simulateAIResponse(text);
  };

  /* Quick actions (frontend only) */
  const handleQuickAction = (action, label) => {
    if (isTyping) return;

    const userMessage = createMessage(label, true);
    setMessages(prev => [...prev, userMessage]);

    simulateAIResponse(label);
  };

  /* Start new conversation */
  const handleNewConversation = () => {
    setMessages([
      createMessage("Hi! I'm your shopping assistant. How can I help you today?", false)
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
