import React, { useState } from 'react';
import { TrendingUp, BarChart3, Heart, Newspaper, FileText, DollarSign, Activity, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { ConnectionStatus } from '../../types';

interface QuickAction {
  icon: LucideIcon;
  label: string;
  action: string;
  category: 'news' | 'knowledge';
  question?: string;
}

interface QuickActionsProps {
  onActionClick: (action: string, label: string, question?: string) => void;
  disabled?: boolean;
  connectionStatus?: ConnectionStatus;
}

const QuickActions: React.FC<QuickActionsProps> = ({ 
  onActionClick, 
  disabled = false, 
  connectionStatus = 'unknown' 
}) => {
  const [showNewsActions, setShowNewsActions] = useState(false);
  const [showReportActions, setShowReportActions] = useState(false);
  
  const actions: QuickAction[] = [
    // News RAG Actions
    { icon: Newspaper, label: 'Latest News', action: 'latest_news', category: 'news' },
    { icon: TrendingUp, label: 'Market Trends', action: 'market_trends', category: 'news' },
    { icon: Heart, label: 'Sentiment Analysis', action: 'sentiment_analysis', category: 'news' },
    { icon: BarChart3, label: 'Stock Performance', action: 'stock_performance', category: 'news' },

    // Knowledge Base Actions (CSE Annual Report 2024)
    { icon: DollarSign, label: 'Financial Highlights', action: 'financial_highlights', category: 'knowledge' },
    { icon: Activity, label: 'Trading Statistics', action: 'trading_stats', category: 'knowledge' },
    { icon: TrendingUp, label: 'Growth Metrics', action: 'growth_metrics', category: 'knowledge' },
    { icon: AlertTriangle, label: 'Challenges & Risks', action: 'challenges', category: 'knowledge' }
  ];

  const getButtonStyle = (): string => {
    if (disabled) {
      return "flex items-center gap-2 p-2 bg-gray-100 rounded-lg text-xs text-gray-400 cursor-not-allowed";
    }
    
    return "flex items-center gap-2 p-2 bg-gray-50 hover:bg-purple-50 rounded-lg transition-colors duration-200 text-xs text-gray-700 hover:text-purple-700 cursor-pointer";
  };

  const newsActions = actions.filter(a => a.category === 'news');
  const knowledgeActions = actions.filter(a => a.category === 'knowledge');

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
      
      {/* News RAG Actions - Collapsible */}
      <div className="mb-2">
        <button
          onClick={() => setShowNewsActions(!showNewsActions)}
          className="w-full flex items-center justify-between p-2 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors duration-200 text-xs font-medium text-gray-700"
        >
          <div className="flex items-center gap-2">
            <Newspaper className="w-3.5 h-3.5" />
            <span>Market News</span>
          </div>
          {showNewsActions ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
        
        {showNewsActions && (
          <div className="grid grid-cols-2 gap-2 mt-2 pl-1">
            {newsActions.map((action, index) => {
              const Icon = action.icon;
              return (
                <button
                  key={index}
                  onClick={() => {
                    if (!disabled) {
                      onActionClick(action.action, action.label);
                      setShowNewsActions(false);
                    }
                  }}
                  disabled={disabled}
                  className={getButtonStyle()}
                  title={disabled ? "Please wait for the current response" : `Get help with ${action.label.toLowerCase()}`}
                >
                  <Icon className="w-3 h-3" />
                  <span>{action.label}</span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Knowledge Base Actions - Collapsible */}
      <div>
        <button
          onClick={() => setShowReportActions(!showReportActions)}
          className="w-full flex items-center justify-between p-2 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors duration-200 text-xs font-medium text-gray-700"
        >
          <div className="flex items-center gap-2">
            <FileText className="w-3.5 h-3.5" />
            <span>CSE Statistical predictions</span>
          </div>
          {showReportActions ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
        
        {showReportActions && (
          <div className="grid grid-cols-2 gap-2 mt-2 pl-1">
            {knowledgeActions.map((action, index) => {
              const Icon = action.icon;
              return (
                <button
                  key={index}
                  onClick={() => {
                    if (!disabled) {
                      onActionClick(action.action, action.label, action.question);
                      setShowReportActions(false);
                    }
                  }}
                  disabled={disabled}
                  className={getButtonStyle()}
                  title={disabled ? "Please wait for the current response" : `Query from CSE Annual Report: ${action.label.toLowerCase()}`}
                >
                  <Icon className="w-3 h-3" />
                  <span>{action.label}</span>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default QuickActions;
