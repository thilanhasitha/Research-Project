import React, { useState } from 'react';
import { Bot, User, ExternalLink, ChevronDown, ChevronUp, BarChart3, Maximize2 } from 'lucide-react';
import type { Plot, NewsSource } from '../../types';

const formatTimestamp = (isoString: string | number): string => {
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

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp: string | number;
  isTyping?: boolean;
  sources?: NewsSource[] | null;
  plots?: Plot[] | null;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ 
  message, 
  isUser, 
  timestamp, 
  isTyping = false,
  sources = null,
  plots = null
}) => {
  const [showSources, setShowSources] = useState(false);
  const [showPlots, setShowPlots] = useState(true);
  const [expandedPlot, setExpandedPlot] = useState<Plot | null>(null);

  return (
    <div className={`flex gap-3 mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      
      {/* Bot Avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-linear-to-br from-purple-500 to-pink-500 flex items-center justify-center shrink-0">
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}
      
      <div className={`max-w-[85%] ${isUser ? 'order-first' : ''}`}>
        <div
          className={`p-3 rounded-2xl ${
            isUser
              ? 'bg-linear-to-r from-purple-600 to-pink-600 text-white rounded-br-md'
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
              
              {/* Plots toggle button */}
              {!isUser && plots && plots.length > 0 && (
                <button
                  onClick={() => setShowPlots(!showPlots)}
                  className="mt-2 flex items-center gap-1 text-xs text-purple-600 hover:text-purple-800 transition-colors"
                >
                  <BarChart3 className="w-3 h-3" />
                  {showPlots ? 'Hide' : 'Show'} {plots.length} visualization{plots.length !== 1 ? 's' : ''}
                </button>
              )}
              
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

        {/* Plots display */}
        {!isUser && showPlots && plots && plots.length > 0 && (
          <div className="mt-2 space-y-2">
            {plots.map((plot, idx) => (
              <div key={idx} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div className="p-2 bg-gray-50 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-gray-900">{plot.title}</span>
                    <button
                      onClick={() => setExpandedPlot(plot)}
                      className="text-gray-600 hover:text-gray-900 transition-colors"
                      title="Expand plot"
                    >
                      <Maximize2 className="w-3 h-3" />
                    </button>
                  </div>
                </div>
                <div className="p-2">
                  <img
                    src={plot.image_url}
                    alt={plot.title}
                    className="w-full h-auto rounded cursor-pointer hover:opacity-90 transition-opacity"
                    onClick={() => setExpandedPlot(plot)}
                    loading="lazy"
                  />
                </div>
                <div className="px-2 pb-2">
                  <p className="text-xs text-gray-600">{plot.description}</p>
                  {plot.relevance_score && (
                    <div className="mt-1 flex justify-end">
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
                        {plot.relevance_score}% relevant
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

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
                  {source.sentiment && (
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      source.sentiment === 'positive' ? 'bg-green-100 text-green-700' :
                      source.sentiment === 'negative' ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {source.sentiment}
                    </span>
                  )}
                  {(source.link || source.url) && (
                    <a
                      href={source.link || source.url}
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
        <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center shrink-0">
          <User className="w-4 h-4 text-gray-600" />
        </div>
      )}

      {/* Expanded Plot Modal */}
      {expandedPlot && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4"
          onClick={() => setExpandedPlot(null)}
        >
          <div 
            className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex justify-between items-center">
              <h3 className="font-semibold text-gray-900">{expandedPlot.title}</h3>
              <button
                onClick={() => setExpandedPlot(null)}
                className="text-gray-600 hover:text-gray-900 text-2xl leading-none"
              >
                ×
              </button>
            </div>
            <div className="p-4">
              <img
                src={expandedPlot.image_url}
                alt={expandedPlot.title}
                className="w-full h-auto rounded"
              />
              <p className="mt-4 text-sm text-gray-600">{expandedPlot.description}</p>
              {expandedPlot.keywords && expandedPlot.keywords.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {expandedPlot.keywords.map((keyword, i) => (
                    <span key={i} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                      {keyword}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
