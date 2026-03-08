/**
 * Annual Report Q&A Component
 * React component for asking questions about the Annual Report
 * Uses native fetch API - no external dependencies needed
 */

import React, { useState, useEffect } from 'react';

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
      const response = await fetch(`${API_BASE_URL}/health`);
      if (response.ok) {
        const data = await response.json();
        setServiceHealth(data);
      }
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
    } catch (err) {
      setError(err.message || 'An error occurred');
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
          <p>Generating answer... This may take 30-60 seconds.</p>
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
    </div>
  );
};

export default AnnualReportQA;
