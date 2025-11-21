import React from 'react';
import { BotIcon, Wifi, WifiOff } from 'lucide-react';

const ChatFloatingButton = ({ 
  onClick, 
  unreadCount = 0, 
  connectionStatus = 'unknown' 
}) => {

  // Connection indicator
  const getConnectionIndicator = () => {
    switch (connectionStatus) {
      case 'connected':
        return (
          <div className="absolute -top-1 -left-1 w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
            <Wifi className="w-2 h-2 text-white" />
          </div>
        );
      case 'disconnected':
        return (
          <div className="absolute -top-1 -left-1 w-4 h-4 bg-yellow-500 rounded-full flex items-center justify-center">
            <WifiOff className="w-2 h-2 text-white" />
          </div>
        );
      default:
        return null;
    }
  };

  // Button styles
  const buttonClass = `
    relative
    bg-blue-600
    text-white
    p-4
    rounded-full
    shadow-lg
    hover:shadow-xl
    transition-all
    duration-300
    hover:scale-110
  `;

  // Tooltip text
  const tooltip = connectionStatus === 'connected'
    ? 'Chat with AI Assistant (Online)'
    : connectionStatus === 'disconnected'
    ? 'Chat with AI Assistant (Offline)'
    : 'Chat with AI Assistant';

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <button
        onClick={onClick}
        className={buttonClass}
        title={tooltip}
      >
        {/* Bot Icon */}
        <BotIcon className="w-6 h-6" />

        {/* Connection Indicator */}
        {getConnectionIndicator()}

        {/* Unread Badge */}
        {unreadCount > 0 && (
          <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-bold">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}

        {/* Connected Ping */}
        {connectionStatus === 'connected' && (
          <div className="absolute inset-0 rounded-full bg-blue-400 opacity-20 scale-110 animate-ping"></div>
        )}

        {/* Disconnected Pulse */}
        {connectionStatus === 'disconnected' && (
          <div className="absolute inset-0 rounded-full bg-yellow-300 opacity-30 scale-110 animate-pulse"></div>
        )}
      </button>
    </div>
  );
};

export default ChatFloatingButton;
