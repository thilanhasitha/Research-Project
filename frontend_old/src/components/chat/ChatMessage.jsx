import React, { useState } from 'react';
import { Bot, User, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';

const formatTimestamp = (isoString) => {
  if (!isoString) return '';
  try {
    return new Date(isoString).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    console.error("Invalid timestamp:", isoString, error);
    return "Invalid Date";
  }
};

const ChatMessage = ({ 
  message, 
  isUser, 
  timestamp, 
  isTyping = false,
  sources = null
}) => {
  const [showSources, setShowSources] = useState(false);

  return (
    <div className={`flex gap-3 mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      
      {/* Bot Avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}
      
      <div className={`max-w-[85%] ${isUser ? 'order-first' : ''}`}>
        <div
          className={`p-3 rounded-2xl ${
            isUser
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-br-md'
              : 'bg-gray-100 text-gray-900 rounded-bl-md'
          }`}
        >
          {isTyping ? (
            <div className="flex items-center gap-1">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          ) : (
            <>
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{message}</p>
              
              {/* Sources toggle button */}
              {!isUser && sources && sources.length > 0 && (
                <button
                  onClick={() => setShowSources(!showSources)}
                  className="mt-2 flex items-center gap-1 text-xs text-purple-600 hover:text-purple-800 transition-colors"
                >
                  {showSources ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                  {showSources ? 'Hide' : 'Show'} {sources.length} source{sources.length !== 1 ? 's' : ''}
                </button>
              )}
            </>
          )}
        </div>

        {/* Sources display */}
        {!isUser && showSources && sources && sources.length > 0 && (
          <div className="mt-2 space-y-2">
            {sources.map((source, idx) => (
              <div key={idx} className="bg-white border border-gray-200 rounded-lg p-2 text-xs">
                <div className="font-medium text-gray-900 mb-1">{source.title}</div>
                {source.summary && (
                  <p className="text-gray-600 text-xs mb-1 line-clamp-2">{source.summary}</p>
                )}
                <div className="flex items-center justify-between mt-1">
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    source.sentiment === 'positive' ? 'bg-green-100 text-green-700' :
                    source.sentiment === 'negative' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {source.sentiment}
                  </span>
                  {source.link && (
                    <a
                      href={source.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-purple-600 hover:text-purple-800"
                    >
                      <span>Read more</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <p className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {!isTyping ? formatTimestamp(timestamp) : ''}
        </p>
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
          <User className="w-4 h-4 text-gray-600" />
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
