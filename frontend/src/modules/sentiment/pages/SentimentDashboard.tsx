import { useState, useEffect } from 'react';
import Card from '../../../shared/components/Card';
import AIChat from '../components/chat/AIChat';
import { LoadingWrapper } from '../../../shared/components/LoadingSpinner';
import { sentimentService } from '../../../services/sentimentService';
import type { LoadingState } from '../../../shared/types/common';
import type { SentimentData } from '../types';

const SentimentDashboard = () => {
  const [symbol, setSymbol] = useState('tech stocks');
  const [searchInput, setSearchInput] = useState('tech stocks');
  const [sentimentData, setSentimentData] = useState<SentimentData | null>(null);
  const [loadingState, setLoadingState] = useState<LoadingState>('idle');
  const [error, setError] = useState('');

  // Fetch sentiment data
  const fetchSentiment = async (topic: string) => {
    if (!topic.trim()) return;
    
    setLoadingState('loading');
    setError('');
    
    try {
      const data = await sentimentService.getSentiment(topic);
      setSentimentData(data);
      setLoadingState('success');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch sentiment data');
      setLoadingState('error');
      console.error('Error fetching sentiment:', err);
    }
  };

  // Initial load
  useEffect(() => {
    fetchSentiment(symbol);
  }, []);

  // Handle search
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSymbol(searchInput);
    fetchSentiment(searchInput);
  };

  // Get sentiment color and label
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-600' };
      case 'negative':
        return { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-600' };
      default:
        return { bg: 'bg-gray-50', border: 'border-gray-200', text: 'text-gray-600' };
    }
  };

  const sentimentColors = sentimentData ? getSentimentColor(sentimentData.sentiment) : getSentimentColor('neutral');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Sentiment Analysis</h1>
        <p className="text-gray-600">AI-powered market sentiment and chatbot</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sentiment Overview */}
        <div className="lg:col-span-1">
          <Card title="Market Sentiment">
            <LoadingWrapper loadingState={loadingState} error={error}>
              <form onSubmit={handleSearch} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Topic or Symbol
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={searchInput}
                      onChange={(e) => setSearchInput(e.target.value)}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                      placeholder="e.g., AAPL, tech stocks"
                    />
                    <button
                      type="submit"
                      disabled={loadingState === 'loading'}
                      className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-400"
                    >
                      Search
                    </button>
                  </div>
                </div>

                {error && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                    {error}
                  </div>
                )}

                {sentimentData && (
                  <>
                    <div className={`${sentimentColors.bg} border ${sentimentColors.border} rounded-lg p-4 text-center`}>
                      <p className="text-sm text-gray-600 mb-1">Overall Sentiment</p>
                      <p className={`text-3xl font-bold ${sentimentColors.text} capitalize`}>
                        {sentimentData.sentiment}
                      </p>
                      <p className="text-sm text-gray-500 mt-2">
                        Score: {Math.round(sentimentData.score)}/100
                      </p>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Total Articles</span>
                        <span className="font-semibold text-gray-900">{sentimentData.volume}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Sources</span>
                        <span className="font-semibold text-gray-900">{sentimentData.sources}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Last Updated</span>
                        <span className="font-semibold text-gray-900">
                          {new Date(sentimentData.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>

                    {sentimentData.keywords && sentimentData.keywords.length > 0 && (
                      <div className="mt-4">
                        <p className="text-sm font-medium text-gray-700 mb-2">Top Topics</p>
                        <div className="flex flex-wrap gap-2">
                          {sentimentData.keywords.slice(0, 5).map((keyword, index) => (
                            <span
                              key={index}
                              className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full"
                            >
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </form>
            </LoadingWrapper>
          </Card>
        </div>
      </div>

      {/* AI Chat Floating Button & Panel */}
      <AIChat />
    </div>
  );
};

export default SentimentDashboard;
