import { useState, useEffect } from 'react';
import Card from '../../../shared/components/Card';
import Button from '../../../shared/components/Button';
import { LoadingWrapper } from '../../../shared/components/LoadingSpinner';
import { StockValuation } from '../types';
import { valuationService } from '../../../services/valuationService';
import { LoadingState } from '../../../shared/types/common';

const ValuationDashboard = () => {
  const [symbol, setSymbol] = useState('AAPL');
  const [searchSymbol, setSearchSymbol] = useState('');
  const [valuation, setValuation] = useState<StockValuation | null>(null);
  const [loadingState, setLoadingState] = useState<LoadingState>('idle');
  const [error, setError] = useState('');

  // Fetch valuation data
  const fetchValuation = async (stockSymbol: string) => {
    setLoadingState('loading');
    setError('');
    try {
      const data = await valuationService.getValuation(stockSymbol);
      setValuation(data);
      setLoadingState('success');
    } catch (err) {
      setError('Failed to fetch valuation data. Please try again.');
      setLoadingState('error');
      console.error('Error fetching valuation:', err);
    }
  };

  // Load initial data
  useEffect(() => {
    fetchValuation(symbol);
  }, [symbol]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchSymbol.trim()) {
      setSymbol(searchSymbol.toUpperCase());
    }
  };

  const getValuationBadge = (val: string) => {
    const badges = {
      'Undervalued': 'bg-green-100 text-green-800',
      'Overvalued': 'bg-red-100 text-red-800',
      'Fair Value': 'bg-yellow-100 text-yellow-800',
    };
    return badges[val as keyof typeof badges] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Stock Valuation</h1>
        <p className="text-gray-600">DCF-based intrinsic value analysis</p>
      </div>

      {/* Search Form */}
      <Card className="mb-6">
        <form onSubmit={handleSearch} className="flex gap-4">
          <input
            type="text"
            placeholder="Enter stock symbol (e.g., AAPL, TSLA)"
            value={searchSymbol}
            onChange={(e) => setSearchSymbol(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <Button type="submit">Search</Button>
        </form>
      </Card>

      {/* Valuation Data */}
      <LoadingWrapper loadingState={loadingState} error={error}>
        {valuation && (
          <>
            {/* Main Info Card */}
            <Card className="mb-6">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{valuation.companyName}</h2>
                  <p className="text-gray-600">{valuation.symbol}</p>
                </div>
                <span className={`px-4 py-2 rounded-full font-semibold text-sm ${getValuationBadge(valuation.valuation)}`}>
                  {valuation.valuation}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Current Price</p>
                  <p className="text-2xl font-bold text-gray-900">${valuation.currentPrice.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Intrinsic Value</p>
                  <p className="text-2xl font-bold text-primary-600">${valuation.intrinsicValue.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Discount Rate</p>
                  <p className="text-2xl font-bold text-gray-900">{(valuation.discountRate * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Growth Rate</p>
                  <p className="text-2xl font-bold text-gray-900">{(valuation.growthRate * 100).toFixed(1)}%</p>
                </div>
              </div>
            </Card>

            {/* Additional Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Financial Metrics</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Free Cash Flow</span>
                    <span className="font-semibold text-gray-900">${(valuation.fcf / 1e9).toFixed(2)}B</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Last Updated</span>
                    <span className="font-semibold text-gray-900">
                      {new Date(valuation.lastUpdated).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </Card>

              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Valuation Analysis</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Upside/Downside</span>
                    <span className={`font-semibold ${
                      valuation.intrinsicValue > valuation.currentPrice ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {((valuation.intrinsicValue - valuation.currentPrice) / valuation.currentPrice * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Price/Intrinsic</span>
                    <span className="font-semibold text-gray-900">
                      {(valuation.currentPrice / valuation.intrinsicValue).toFixed(2)}x
                    </span>
                  </div>
                </div>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card className="mt-6 bg-primary-50">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">Need More Insights?</h3>
                  <p className="text-sm text-gray-600">
                    Check sentiment analysis or get personalized recommendations
                  </p>
                </div>
                <div className="flex gap-3">
                  <Button variant="primary" size="sm">View Sentiment</Button>
                  <Button variant="outline" size="sm">Get Recommendations</Button>
                </div>
              </div>
            </Card>
          </>
        )}
      </LoadingWrapper>
    </div>
  );
};

export default ValuationDashboard;
