/**
 * Annual Report Q&A Component (Fetch API Version)
 * React component for asking questions about the Annual Report
 * TypeScript version
 */

import React, { useState, useEffect } from 'react';
import type { ServiceHealth } from '../types';

interface Answer {
  answer: string;
  question: string;
  context?: string[];
  confidence?: number;
}

const AnnualReportQAFetch: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [serviceHealth, setServiceHealth] = useState<ServiceHealth | null>(null);

  const API_BASE_URL = import.meta.env.VITE_SENTIMENT_API_URL || 'http://localhost:8000/api/pdf-rag';

  // Example questions
  const exampleQuestions = [
    'What was the total revenue in 2024?',
    'What are the strategic objectives?',
    'How many employees does the company have?',
    'What are the main risk factors?',
    'What are the future growth plans?',
  ];

  // Check service health on mount
  useEffect(() => {
    checkServiceHealth();
  }, []);

  const checkServiceHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (response.ok) {
        const data = await response.json();
        setServiceHealth(data);
      }
    } catch (err) {
      console.error('Health check failed:', err);
    }
  };

  const askQuestion = async (questionText: string) => {
    if (!questionText.trim()) {
      setError('Please enter a question');
      return;
    }

    setLoading(true);
    setError(null);
    setAnswer(null);

    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: questionText,
          n_results: 5,
          model: 'llama3.2:latest',
          show_context: false,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Request failed');
      }

      const data = await response.json();
      setAnswer(data);
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    askQuestion(question);
  };

  const handleExampleClick = (exampleQuestion: string) => {
    setQuestion(exampleQuestion);
    askQuestion(exampleQuestion);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">📄 Annual Report Q&A</h2>
          <p className="text-gray-600">Ask questions about the Annual Report and get AI-powered answers (Fetch API Version)</p>
          
          {serviceHealth && (
            <div className={`mt-3 inline-flex items-center px-3 py-1 rounded-full text-sm ${
              serviceHealth.status === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              Status: {serviceHealth.status}
              {serviceHealth.index && ` | ${serviceHealth.index.chunks} chunks loaded`}
            </div>
          )}
        </div>

        {/* Example Questions */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">💡 Example Questions:</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {exampleQuestions.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleExampleClick(q)}
                disabled={loading}
                className="text-left px-4 py-2 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Question Input */}
        <form onSubmit={handleSubmit} className="mb-6">
          <div className="flex gap-2">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Type your question here..."
              disabled={loading}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="px-6 py-3 bg-linear-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {loading ? 'Generating...' : 'Ask'}
            </button>
          </div>
        </form>

        {/* Loading Indicator */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mb-4"></div>
            <p className="text-gray-600">Generating answer... This may take 30-60 seconds.</p>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Answer Display */}
        {answer && !loading && (
          <div className="bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Answer:</h3>
            <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">{answer.answer}</p>
            
            {answer.confidence && (
              <div className="mt-4 text-sm text-gray-600">
                Confidence: {(answer.confidence * 100).toFixed(1)}%
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AnnualReportQAFetch;
