import React from 'react';
import { TrendingUp, BarChart3, Heart, Newspaper } from 'lucide-react';

const QuickActions = ({ onActionClick, disabled = false, connectionStatus = 'unknown' }) => {
  const actions = [
    { icon: Newspaper, label: 'Latest News', action: 'latest_news' },
    { icon: TrendingUp, label: 'Market Trends', action: 'market_trends' },
    { icon: Heart, label: 'Sentiment Analysis', action: 'sentiment_analysis' },
    { icon: BarChart3, label: 'Stock Performance', action: 'stock_performance' }
  ];

  const getButtonStyle = () => {
    if (disabled) {
      return "flex items-center gap-2 p-2 bg-gray-100 rounded-lg text-xs text-gray-400 cursor-not-allowed";
    }
    
    return "flex items-center gap-2 p-2 bg-gray-50 hover:bg-purple-50 rounded-lg transition-colors duration-200 text-xs text-gray-700 hover:text-purple-700 cursor-pointer";
  };

  return (
    <div className="p-3 border-b border-gray-200">
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs text-gray-500 font-medium">Quick Actions</p>
        {connectionStatus === 'disconnected' && (
          <span className="text-xs text-yellow-600 bg-yellow-100 px-2 py-1 rounded-full">
            Limited
          </span>
        )}
      </div>
      <div className="grid grid-cols-2 gap-2">
        {actions.map((action, index) => (
          <button
            key={index}
            onClick={() => !disabled && onActionClick(action.action, action.label)}
            disabled={disabled}
            className={getButtonStyle()}
            title={disabled ? "Please wait for the current response" : `Get help with ${action.label.toLowerCase()}`}
          >
            <action.icon className="w-3 h-3" />
            <span>{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickActions;