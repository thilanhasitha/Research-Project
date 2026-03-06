import { useState } from 'react';
import Card from '../../../shared/components/Card';
import AIChat from '../components/chat/AIChat';

const SentimentDashboard = () => {
  const [symbol, setSymbol] = useState('AAPL');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Sentiment Analysis</h1>
        <p className="text-gray-600">AI-powered market sentiment and chatbot</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sentiment Overview */}
        <div className="lg:col-span-1">
          <Card title="Stock Sentiment">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stock Symbol
                </label>
                <input
                  type="text"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  placeholder="AAPL"
                />
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-600 mb-1">Overall Sentiment</p>
                <p className="text-3xl font-bold text-green-600">Positive</p>
                <p className="text-sm text-gray-500 mt-2">Score: 75/100</p>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">News</span>
                  <span className="font-semibold text-green-600">+68</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Social Media</span>
                  <span className="font-semibold text-green-600">+82</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Reports</span>
                  <span className="font-semibold text-yellow-600">+70</span>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* AI Chat Floating Button & Panel */}
      <AIChat />
    </div>
  );
};

export default SentimentDashboard;
