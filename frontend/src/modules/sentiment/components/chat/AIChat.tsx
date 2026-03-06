import React, { useState, useEffect } from 'react';
import ChatFloatingButton from './ChatFloatingButton';
import ChatPanel from './ChatPanel';
import ChatHistory from './ChatHistory';
import type { Message, Conversation, ConnectionStatus } from '../../types';

// Create a message object
const createMessage = (
  text: string, 
  isUser = false, 
  sources: any = null, 
  metadata: any = null, 
  plots: any = null
): Message => ({
  id: Date.now() + Math.random(),
  message: text,
  isUser,
  sources,
  metadata,
  plots,
  timestamp: Date.now(),
});

// Generate unique ID for conversations
const generateId = (): string => `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

const AIChat: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    createMessage("Hi! I'm your financial news assistant. I can help you with the latest news, market trends, and sentiment analysis. How can I help you today?", false)
  ]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('checking');
  const [error, setError] = useState<string | null>(null);

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
        // TODO: Replace with actual health check API call
        // const health = await checkHealth();
        // For now, simulate connection check
        setConnectionStatus('connected');
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
  const getAIResponse = async (userMessage: string) => {
    setIsTyping(true);
    setError(null);

    try {
      // TODO: Replace with actual API calls
      // const response = await askQuestion(userMessage, {...});
      
      // Simulate API response
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const aiMessage = createMessage(
        `This is a simulated response to: "${userMessage}". Please connect the sentiment service APIs to get real responses.`,
        false,
        null, // sources
        { contextUsed: true, timestamp: new Date().toISOString() }
      );

      setMessages(prev => [...prev, aiMessage]);

      if (!isOpen) {
        setUnreadCount(prev => prev + 1);
      }

      setIsTyping(false);
    } catch (err: any) {
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
  const handleQuickAction = (_action: string, label: string, question?: string) => {
    if (isTyping) return;

    // Use the provided question if available, otherwise use label
    const message = question || label;

    // Create user message with the label or question
    const userMessage = createMessage(message, true);
    setMessages(prev => [...prev, userMessage]);

    // Get AI response
    getAIResponse(message);
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
  const handleSelectConversation = (conversationId: string) => {
    const conversation = conversations.find(c => c.id === conversationId);
    if (conversation) {
      setCurrentConversationId(conversationId);
      setMessages(conversation.messages);
      setError(null);
      setIsHistoryOpen(false);
    }
  };

  /* Delete conversation */
  const handleDeleteConversation = (conversationId: string) => {
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
        onToggleHistory={handleToggleHistory}
        isHistoryOpen={isHistoryOpen}
        connectionStatus={connectionStatus}
        error={error}
      />
    </>
  );
};

export default AIChat;
