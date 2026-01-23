import { useState } from 'react';
import Card from '../../../shared/components/Card';
import Button from '../../../shared/components/Button';

const RecommendationDashboard = () => {
  const [riskLevel, setRiskLevel] = useState<'Low' | 'Medium' | 'High'>('Medium');

  const recommendations = [
    {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      recommendation: 'Strong Buy',
      price: 178.50,
      target: 210.00,
      risk: 'Low',
      score: 92
    },
    {
      symbol: 'GOOGL',
      name: 'Alphabet Inc.',
      recommendation: 'Buy',
      price: 141.80,
      target: 165.00,
      risk: 'Medium',
      score: 85
    },
    {
      symbol: 'TSLA',
      name: 'Tesla Inc.',
      recommendation: 'Hold',
      price: 248.50,
      target: 260.00,
      risk: 'High',
      score: 72
    },
    {
      symbol: 'MSFT',
      name: 'Microsoft Corp.',
      recommendation: 'Strong Buy',
      price: 415.20,
      target: 475.00,
      risk: 'Low',
      score: 90
    }
  ];

  const getRecommendationColor = (rec: string) => {
    const colors: Record<string, string> = {
      'Strong Buy': 'bg-green-100 text-green-800 border-green-200',
      'Buy': 'bg-green-50 text-green-700 border-green-100',
      'Hold': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'Sell': 'bg-red-50 text-red-700 border-red-100',
      'Strong Sell': 'bg-red-100 text-red-800 border-red-200'
    };
    return colors[rec] || colors.Hold;
  };

  const getRiskColor = (risk: string) => {
    const colors: Record<string, string> = {
      'Low': 'text-green-600',
      'Medium': 'text-yellow-600',
      'High': 'text-red-600'
    };
    return colors[risk] || colors.Medium;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Stock Recommendations</h1>
        <p className="text-gray-600">Personalized recommendations based on your risk profile</p>
      </div>

      {/* Risk Profile Selector */}
      <Card className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">Your Risk Profile</h3>
            <p className="text-sm text-gray-600">Select your risk tolerance level</p>
          </div>
          <div className="flex gap-2">
            {(['Low', 'Medium', 'High'] as const).map((level) => (
              <Button
                key={level}
                variant={riskLevel === level ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setRiskLevel(level)}
              >
                {level} Risk
              </Button>
            ))}
          </div>
        </div>
      </Card>

      {/* Recommendations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {recommendations.map((stock) => (
          <Card key={stock.symbol} hover>
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-gray-900">{stock.symbol}</h3>
                <p className="text-sm text-gray-600">{stock.name}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getRecommendationColor(stock.recommendation)}`}>
                {stock.recommendation}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">Current Price</p>
                <p className="text-2xl font-bold text-gray-900">${stock.price}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Target Price</p>
                <p className="text-2xl font-bold text-primary-600">${stock.target}</p>
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
              <div className="flex items-center gap-4">
                <div>
                  <p className="text-xs text-gray-600">Risk Level</p>
                  <p className={`text-sm font-semibold ${getRiskColor(stock.risk)}`}>{stock.risk}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Score</p>
                  <p className="text-sm font-semibold text-gray-900">{stock.score}/100</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button size="sm" variant="outline">Details</Button>
                <Button size="sm" variant="primary">Analyze</Button>
              </div>
            </div>

            <div className="mt-3 text-xs text-gray-600">
              Upside: <span className="font-semibold text-green-600">
                +{((stock.target - stock.price) / stock.price * 100).toFixed(1)}%
              </span>
            </div>
          </Card>
        ))}
      </div>

      <div className="mt-6 text-center">
        <Button variant="outline">Show More Recommendations</Button>
      </div>
    </div>
  );
};

export default RecommendationDashboard;
