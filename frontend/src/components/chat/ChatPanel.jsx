import React, { useRef, useEffect, useState } from 'react';
import { X, Bot, Send, Wifi, WifiOff, AlertCircle } from 'lucide-react';
import ChatMessage from './ChatMessage';
import QuickActions from './QuickActions';

const ChatPanel = ({
  isOpen,
  messages,
  newMessage,
  setNewMessage,
  isTyping,
  onClose,
  onSendMessage,
  onQuickAction,
  onAddToCart,
  onViewProduct,
  connectionStatus = 'unknown',
  error = null,
  onRetry,
  onVariantConfirm = () => {},
  onVariantCancel = () => {}
}) => {
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSendMessage();
    }
  };

  const getConnectionIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <Wifi className="w-3 h-3 text-green-400" />;
      case 'disconnected':
        return <WifiOff className="w-3 h-3 text-red-400" />;
      default:
        return <Wifi className="w-3 h-3 text-gray-400" />;
    }
  };

  const getConnectionText = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'Online';
      case 'disconnected':
        return 'Offline Mode';
      default:
        return 'Connecting...';
    }
  };

  const getConnectionColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'text-green-100';
      case 'disconnected':
        return 'text-red-100';
      default:
        return 'text-gray-100';
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="
        fixed bottom-8 right-6 z-40
        w-[35rem] max-w-[calc(100vw-3rem)]
        animate-fadeIn
        sm:h-[80vh] h-[90vh]
        sm:rounded-2xl rounded-none
        sm:bottom-8 bottom-0
        sm:right-6 right-0
        sm:left-auto left-0
      "
    >
      <div
        className="
          relative bg-white
          sm:rounded-2xl rounded-none
          shadow-2xl border border-gray-200
          flex flex-col overflow-hidden
          w-full h-full
        "
      >

        {/* Chat Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-t-2xl">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-semibold text-sm">Shopping Assistant</h3>
              <div className={`flex items-center gap-1 text-xs ${getConnectionColor()}`}>
                {getConnectionIcon()}
                <span>{getConnectionText()}</span>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-white hover:bg-opacity-20 rounded-md transition-colors"
            aria-label="Close chat"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="bg-red-50 border-b border-red-200 p-2">
            <div className="flex items-center gap-2 text-red-800">
              <AlertCircle className="w-4 h-4" />
              <span className="text-xs">{error}</span>
              {onRetry && (
                <button
                  onClick={onRetry}
                  className="ml-auto text-xs text-red-700 hover:text-red-900 flex items-center gap-1"
                >
                  Retry
                </button>
              )}
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <QuickActions
          onActionClick={onQuickAction}
          disabled={isTyping}
          connectionStatus={connectionStatus}
        />

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4" style={{ scrollbarWidth: 'thin' }}>
          {messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              message={msg.message}
              isUser={msg.isUser}
              timestamp={msg.timestamp}
              products={msg.products}
              variantData={msg.variantData}
              onAddToCart={onAddToCart}
              onViewProduct={onViewProduct}
              onVariantConfirm={(selection) => {
                if (msg.variantData) {
                  onVariantConfirm(
                    selection,
                    msg.variantData.item_id,
                    msg.variantData.item_name
                  );
                }
              }}
              onVariantCancel={onVariantCancel}
            />
          ))}

          {isTyping && (
            <ChatMessage
              message=""
              isUser={false}
              timestamp=""
              isTyping={true}
            />
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-3 border-t border-gray-200 bg-gray-50">
          <div className="flex gap-2">
            <input
              ref={inputRef}
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={isTyping ? "AI is typing..." : "Ask me anything..."}
              disabled={isTyping}
              className="flex-1 p-3 border border-gray-300 rounded-xl text-black focus:ring-2 focus:ring-purple-500 text-sm"
            />
            <button
              onClick={onSendMessage}
              disabled={newMessage.trim() === '' || isTyping}
              className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-3 rounded-xl hover:opacity-90 disabled:opacity-50"
              aria-label="Send message"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>

          <p className="text-xs text-gray-500 mt-2">
            Press Enter to send • Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
