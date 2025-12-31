# RAG Pipeline Guide

## Overview
Your RAG (Retrieval-Augmented Generation) pipeline is now fully functional! This document explains how it works.

## Architecture

```
User Query (Frontend)
    ↓
News RAG Service (Backend)
    ↓
1. Query Embedding
2. Weaviate Vector Search
3. Context Retrieval
4. Ollama LLM Generation
    ↓
Contextual Response + Sources
    ↓
Frontend Display
```

## How It Works

### 1. **User Asks a Question** (Frontend)
- User types a question in the chat interface
- Example: "What's the latest news about AI stocks?"

### 2. **Query Processing** (Backend - NewsRAGService)
- The query is sent to `/news-chat/ask` endpoint
- NewsRAGService receives the question

### 3. **Semantic Search** (Weaviate)
- The query is used to search Weaviate's vector database
- Uses **hybrid search** (combines vector similarity + BM25 keyword matching)
- Retrieves the top 5 most relevant news articles (configurable)
- Each article includes:
  - Title
  - Summary
  - Content
  - Sentiment (positive/negative/neutral)
  - Published date
  - Source link

### 4. **Context Building**
- Retrieved articles are formatted into a structured context
- Includes: titles, summaries, sentiment scores, and dates
- This context is prepended to the user's question

### 5. **LLM Generation** (Ollama)
- The context + question is sent to Ollama (llama3)
- LLM generates a response based ONLY on the provided articles
- Includes citations (e.g., "According to Article 1...")
- Highlights relevant sentiment and trends

### 6. **Response with Sources** (Frontend)
- User receives the AI-generated answer
- Can expand to view source articles
- Each source shows:
  - Article title
  - Summary
  - Sentiment badge
  - Link to read more

## API Endpoints

### Chat Endpoint
```http
POST /news-chat/ask
Content-Type: application/json

{
  "message": "What's the latest on tech stocks?",
  "user_id": "anonymous",
  "conversation_id": null,
  "include_sources": true,
  "context_limit": 5
}
```

**Response:**
```json
{
  "message": "Based on recent articles...",
  "sources": [
    {
      "title": "Tech Stocks Surge...",
      "summary": "...",
      "link": "https://...",
      "sentiment": "positive",
      "published": "2025-12-23T06:00:00"
    }
  ],
  "context_used": 5,
  "timestamp": "2025-12-23T06:51:00"
}
```

### Search Endpoint
```http
POST /news-chat/search
{
  "query": "AI companies",
  "limit": 10,
  "sentiment_filter": "positive",
  "days": 7
}
```

### Trending News
```http
GET /news-chat/trending?days=7&limit=10
```

### Sentiment Analysis
```http
POST /news-chat/sentiment
{
  "topic": "AI stocks",
  "days": 7
}
```

### Health Check
```http
GET /news-chat/health
```

## Frontend Components

### AIChat.jsx
- Main chat component
- Handles user interactions
- Manages conversation state
- Calls `askQuestion()` from newsRAGService

### ChatMessage.jsx
- Displays individual messages
- Shows expandable sources
- Sentiment badges for each source
- Links to original articles

### QuickActions.jsx
- Pre-defined query buttons:
  - Latest News
  - Market Trends
  - Sentiment Analysis
  - Stock Performance

### newsRAGService.js
- API client for RAG endpoints
- Handles requests/responses
- Error handling
- Timeout management (30s for LLM)

## Data Flow Example

1. **User Input:** "What's the sentiment around AI companies?"

2. **Weaviate Search:** 
   - Finds 5 articles about AI companies
   - Ranked by semantic similarity

3. **Retrieved Articles:**
   ```
   Article 1: "OpenAI Launches New Model" (positive, 0.85)
   Article 2: "AI Regulations Tighten" (negative, -0.32)
   Article 3: "Tech Giants Invest in AI" (positive, 0.67)
   ...
   ```

4. **Context Sent to LLM:**
   ```
   You are a financial news analyst...
   
   NEWS CONTEXT:
   Article 1: OpenAI Launches New Model...
   Article 2: AI Regulations Tighten...
   
   USER QUESTION:
   What's the sentiment around AI companies?
   
   INSTRUCTIONS:
   Answer based ONLY on provided articles...
   ```

5. **LLM Response:**
   ```
   "Based on recent articles, sentiment around AI companies 
   is mixed but generally positive. According to Article 1, 
   OpenAI's new model launch has generated positive market 
   response. However, Article 2 mentions regulatory concerns..."
   ```

6. **Frontend Display:**
   - Shows the answer with markdown formatting
   - "Show 5 sources" button reveals the articles
   - Each source has sentiment badge and read more link

## Configuration

### Modify Context Size
In `frontend/utils/newsRAGService.js`:
```javascript
contextLimit: 5  // Change to 3-10
```

### Change Ollama Model
In `backend/app/llm/OllamaProvider.py`:
```python
model: str = "llama3:latest"  # or "mistral", "codellama", etc.
```

### Adjust Search Settings
In `backend/app/services/news_rag_service.py`:
```python
response = collection.query.hybrid(
    query=query,
    limit=limit,  # Number of results
    filters=filters,  # Sentiment, date filters
    return_metadata=["score"]
)
```

## Testing the RAG Pipeline

### 1. Health Check
```bash
curl http://localhost:8001/news-chat/health
```

### 2. Ask a Question
```bash
curl -X POST http://localhost:8001/news-chat/ask \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the latest tech trends?"}'
```

### 3. Frontend Test
1. Open http://localhost:3001
2. Click the chat button
3. Ask: "Tell me about recent market trends"
4. Wait for response (20-30 seconds)
5. Click "Show sources" to see articles used

## Quick Action Examples

- **"Latest News"** → Shows most recent articles
- **"Market Trends"** → Analyzes trending topics
- **"Sentiment Analysis"** → Overall market sentiment
- **"Stock Performance"** → Recent stock movements

## Troubleshooting

### No Results Found
- Check if Weaviate has data: `GET /news-chat/stats`
- Verify RSS feeds are being collected
- Check MongoDB has articles

### Slow Responses
- Ollama is processing (30s normal for long answers)
- Reduce `context_limit` from 5 to 3
- Check Ollama container: `docker logs ollama_new`

### Connection Errors
- Verify backend is running: `docker ps`
- Check Weaviate health: `GET /news-chat/health`
- Ensure proxy is configured in vite.config.js

## Database Statistics

Check current data:
```http
GET /news-chat/stats
```

Response shows:
- Total articles in database
- Last 30 days statistics
- Sentiment distribution

## Future Enhancements

1. **Conversation Memory** - Track conversation history
2. **Multi-turn Dialog** - Context-aware follow-up questions
3. **Custom Filters** - Filter by date range, source, sentiment
4. **Export Chat** - Save conversations
5. **Voice Input** - Speak questions
6. **Chart Visualization** - Show sentiment trends





**Try it now!** Ask the chatbot about financial news! 🚀
