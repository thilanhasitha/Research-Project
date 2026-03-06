import React, { useState } from 'react';
import { testAllEndpoints, displayConnectionResults, type ConnectionTestResult } from './utils/connectionTest';

const ConnectionTestPanel: React.FC = () => {
  const [testing, setTesting] = useState(false);
  const [results, setResults] = useState<{
    newsChat?: ConnectionTestResult;
    knowledgeBase?: ConnectionTestResult;
  } | null>(null);

  const runTests = async () => {
    setTesting(true);
    setResults(null);
    
    try {
      const testResults = await testAllEndpoints();
      displayConnectionResults(testResults);
      setResults(testResults);
    } catch (error) {
      console.error('Test failed:', error);
    } finally {
      setTesting(false);
    }
  };

  const ResultCard = ({ title, result }: { title: string; result?: ConnectionTestResult }) => {
    if (!result) return null;

    return (
      <div className={`p-4 rounded-lg border-2 ${result.success ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'}`}>
        <h3 className="font-bold text-lg mb-2 flex items-center gap-2">
          {result.success ? '✅' : '❌'} {title}
        </h3>
        
        <div className="space-y-2 text-sm">
          <div>
            <span className="font-semibold">Endpoint:</span> {result.endpoint}
          </div>
          <div>
            <span className="font-semibold">Status:</span> {result.status || 'N/A'}
          </div>
          <div>
            <span className="font-semibold">Response Time:</span> {result.responseTime}ms
          </div>
          
          {result.error && (
            <div className="mt-2 p-2 bg-red-100 border border-red-300 rounded text-red-800">
              <span className="font-semibold">Error:</span> {result.error}
            </div>
          )}
          
          {result.data && (
            <div className="mt-2">
              <div className="font-semibold mb-1">Response Data:</div>
              <pre className="p-2 bg-gray-100 rounded text-xs overflow-auto max-h-40">
                {JSON.stringify(result.data, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="fixed top-4 right-4 z-50 w-96 max-h-[90vh] overflow-auto bg-white rounded-lg shadow-2xl border-2 border-purple-500">
      <div className="sticky top-0 bg-linear-to-r from-purple-600 to-pink-600 text-white p-4 rounded-t-lg">
        <h2 className="text-xl font-bold">🔌 Backend Connection Test</h2>
        <p className="text-sm opacity-90">Test API endpoints and view responses</p>
      </div>
      
      <div className="p-4 space-y-4">
        <button
          onClick={runTests}
          disabled={testing}
          className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white font-bold py-3 px-4 rounded-lg transition-colors"
        >
          {testing ? '🔄 Testing...' : '▶️ Run Connection Tests'}
        </button>

        {results && (
          <div className="space-y-4">
            <ResultCard title="News Chat API" result={results.newsChat} />
            <ResultCard title="Knowledge Base API" result={results.knowledgeBase} />
            
            <div className="mt-4 p-3 bg-blue-50 border border-blue-300 rounded">
              <p className="text-sm text-blue-800">
                <strong>Summary:</strong> {
                  [results.newsChat, results.knowledgeBase]
                    .filter(r => r?.success).length
                } / 2 endpoints working
              </p>
            </div>
          </div>
        )}

        {!results && !testing && (
          <div className="text-center text-gray-500 py-8">
            <p>Click the button to test backend connections</p>
            <p className="text-xs mt-2">Make sure backend is running on port 8001</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConnectionTestPanel;
