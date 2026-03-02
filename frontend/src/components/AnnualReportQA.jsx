/**
 * Annual Report Q&A Component
 * React component for asking questions about the Annual Report
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AnnualReportQA = () => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [serviceHealth, setServiceHealth] = useState(null);

  const API_BASE_URL = 'http://localhost:8000/api/pdf-rag';

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
      const response = await axios.get(`${API_BASE_URL}/health`);
      setServiceHealth(response.data);
    } catch (err) {
      console.error('Health check failed:', err);
    }
  };

  const askQuestion = async (questionText) => {
    if (!questionText.trim()) {
      setError('Please enter a question');
      return;
    }

    setLoading(true);
    setError(null);
    setAnswer(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/ask`, {
        question: questionText,
        n_results: 5,
        model: 'llama3.2:latest',
        show_context: false,
      });

      setAnswer(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    askQuestion(question);
  };

  const handleExampleClick = (exampleQuestion) => {
    setQuestion(exampleQuestion);
    askQuestion(exampleQuestion);
  };

  return (
    <div className="annual-report-qa">
      <div className="qa-header">
        <h2>📄 Annual Report Q&A</h2>
        <p>Ask questions about the Annual Report and get AI-powered answers</p>
        
        {serviceHealth && (
          <div className={`health-indicator ${serviceHealth.status}`}>
            Status: {serviceHealth.status}
            {serviceHealth.index && ` | ${serviceHealth.index.chunks} chunks loaded`}
          </div>
        )}
      </div>

      {/* Example Questions */}
      <div className="example-questions">
        <h3>💡 Example Questions:</h3>
        <div className="example-buttons">
          {exampleQuestions.map((q, idx) => (
            <button
              key={idx}
              className="example-btn"
              onClick={() => handleExampleClick(q)}
              disabled={loading}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Question Input */}
      <form onSubmit={handleSubmit} className="question-form">
        <div className="input-group">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Type your question here..."
            className="question-input"
            disabled={loading}
          />
          <button
            type="submit"
            className="ask-button"
            disabled={loading || !question.trim()}
          >
            {loading ? 'Generating...' : 'Ask'}
          </button>
        </div>
      </form>

      {/* Loading Indicator */}
      {loading && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>Generating answer...</p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="error-container">
          <h4>❌ Error</h4>
          <p>{error}</p>
        </div>
      )}

      {/* Answer Display */}
      {answer && !loading && (
        <div className="answer-container">
          <div className="question-display">
            <strong>Question:</strong>
            <p>{answer.question}</p>
          </div>

          <div className="answer-display">
            <strong>Answer:</strong>
            <p>{answer.answer}</p>
          </div>

          <div className="metadata">
            <span>📊 Chunks: {answer.chunks_found}</span>
            <span>🤖 Model: {answer.model}</span>
            {answer.duration && <span>⏱️ {answer.duration.toFixed(2)}s</span>}
          </div>
        </div>
      )}

      {/* Styles */}
      <style jsx>{`
        .annual-report-qa {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
        }

        .qa-header {
          text-align: center;
          margin-bottom: 30px;
        }

        .qa-header h2 {
          color: #333;
          margin-bottom: 10px;
        }

        .qa-header p {
          color: #666;
        }

        .health-indicator {
          display: inline-block;
          padding: 5px 15px;
          border-radius: 20px;
          font-size: 12px;
          margin-top: 10px;
        }

        .health-indicator.healthy {
          background: #d4edda;
          color: #155724;
        }

        .health-indicator.degraded {
          background: #fff3cd;
          color: #856404;
        }

        .example-questions {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 10px;
          margin-bottom: 20px;
        }

        .example-questions h3 {
          font-size: 14px;
          color: #667eea;
          margin-bottom: 10px;
        }

        .example-buttons {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .example-btn {
          background: #e9ecef;
          border: none;
          padding: 8px 12px;
          border-radius: 5px;
          cursor: pointer;
          font-size: 13px;
          transition: all 0.3s;
        }

        .example-btn:hover:not(:disabled) {
          background: #667eea;
          color: white;
        }

        .example-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .question-form {
          margin-bottom: 20px;
        }

        .input-group {
          display: flex;
          gap: 10px;
        }

        .question-input {
          flex: 1;
          padding: 15px;
          border: 2px solid #e0e0e0;
          border-radius: 10px;
          font-size: 16px;
        }

        .question-input:focus {
          outline: none;
          border-color: #667eea;
        }

        .ask-button {
          padding: 15px 30px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          border-radius: 10px;
          font-size: 16px;
          font-weight: bold;
          cursor: pointer;
          transition: transform 0.2s;
        }

        .ask-button:hover:not(:disabled) {
          transform: translateY(-2px);
        }

        .ask-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .loading-indicator {
          text-align: center;
          padding: 20px;
        }

        .spinner {
          border: 4px solid #f3f3f3;
          border-top: 4px solid #667eea;
          border-radius: 50%;
          width: 40px;
          height: 40px;
          animation: spin 1s linear infinite;
          margin: 0 auto 10px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .error-container {
          background: #f8d7da;
          border-left: 4px solid #dc3545;
          color: #721c24;
          padding: 15px;
          border-radius: 5px;
          margin-top: 20px;
        }

        .answer-container {
          background: #f8f9fa;
          border-left: 4px solid #667eea;
          padding: 20px;
          border-radius: 10px;
          margin-top: 20px;
        }

        .question-display,
        .answer-display {
          margin-bottom: 15px;
        }

        .question-display strong,
        .answer-display strong {
          color: #667eea;
          display: block;
          margin-bottom: 5px;
        }

        .answer-display p {
          white-space: pre-wrap;
          line-height: 1.6;
          color: #333;
        }

        .metadata {
          margin-top: 15px;
          padding-top: 15px;
          border-top: 1px solid #dee2e6;
          font-size: 13px;
          color: #6c757d;
        }

        .metadata span {
          margin-right: 15px;
        }
      `}</style>
    </div>
  );
};

export default AnnualReportQA;
