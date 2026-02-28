# News Chat API Documentation

## Overview

The News Chat API provides conversational AI capabilities for querying financial news using Retrieval-Augmented Generation (RAG). The system combines semantic search with LLM-powered responses to provide intelligent, context-aware answers about market news and sentiment.

## Architecture

```
MongoDB → Kafka (CDC) → Consumer → Weaviate (Vector DB) → RAG Service → LLM → User
```

# Data Flow
1. **News articles** are stored in MongoDB (`research_db.rss_news`)
2. **Change Data Capture (CDC)** via Debezium detects changes
3. **Kafka** streams events to the consumer
4. **Consumer** processes and syncs to Weaviate with embeddings
5. **RAG Service** queries Weaviate and generates responses using Ollama LLM

## Base URL

```
http://localhost:8001/news-chat
```

## Endpoints

### 1. Ask Questions (RAG Chat)

**POST** `/news-chat/ask`

Chat with the AI assistant about financial news. The system retrieves relevant articles and generates contextual answers.

**Request Body:**
```json
{
  "message": "What's happening with Bitcoin?",
  "user_id": "test_user",
  "include_sources": true,
  "context_limit": 5
}
```

**Parameters:**
- `message` (required): Your question or query
- `user_id` (optional): User identifier (default: "anonymous")
- `include_sources` (optional): Include source articles (default: true)
- `context_limit` (optional): Number of articles to use as context (1-20, default: 5)

**Response:**
```json
{
  "message": "Based on the provided news articles...",
  "sources": [
    {
      "title": "Bitcoin Surges Past Record High",
      "summary": "Cryptocurrency market rallies...",
      "link": "http://crypto.com/btc-surge",
      "published": "2025-12-22T06:32:59.959Z",
      "sentiment": "positive",
      "relevance_score": 0.92
    }
  ],
  "context_used": 2,
  "conversation_id": null,
  "timestamp": "2025-12-22T14:06:29.186762"
}
```

**Example:**
```powershell
$body = @{
    message = "What are the latest news about technology?"
    user_id = "user123"
    context_limit = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/news-chat/ask" `
    -Method Post -Body $body -ContentType "application/json"
```

### 2. Search News

**POST** `/news-chat/search`

Search for news articles using semantic search without generating an AI response.

**Request Body:**
```json
{
  "query": "artificial intelligence",
  "limit": 10,
  "sentiment_filter": "positive",
  "days": 7
}
```

**Parameters:**
- `query` (required): Search query
- `limit` (optional): Maximum results (1-50, default: 10)
- `sentiment_filter` (optional): Filter by sentiment ("positive", "negative", "neutral")
- `days` (optional): Only return news from last N days (1-90)

**Example:**
```powershell
$body = @{
    query = "stock market"
    limit = 5
    sentiment_filter = "positive"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/news-chat/search" `
    -Method Post -Body $body -ContentType "application/json"
```

### 3. Get Trending News

**GET** `/news-chat/trending?days=7&limit=10`

Get trending news articles sorted by sentiment score.

**Query Parameters:**
- `days` (optional): Number of days to look back (default: 7)
- `limit` (optional): Maximum results (default: 10)

**Response:**
```json
{
  "trending": [
    {
      "id": "22e74882-426a-4377-a362-8361ee6f87de",
      "title": "Real-time Test",
      "summary": "Final updated summary",
      "sentiment": "positive",
      "score": 0.95
    }
  ],
  "period_days": 7,
  "count": 4,
  "timestamp": "2025-12-22T14:06:41.143027"
}
```

**Example:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/news-chat/trending?days=7&limit=5"
```

### 4. Analyze Sentiment

**POST** `/news-chat/sentiment`

Get sentiment analysis summary for a specific topic or overall market.

**Request Body:**
```json
{
  "topic": "technology",
  "days": 7
}
```

**Parameters:**
- `topic` (optional): Topic to analyze (uses semantic search)
- `days` (optional): Number of days to analyze (1-90, default: 7)

**Response:**
```json
{
  "topic": "technology",
  "period_days": 7,
  "total_articles": 4,
  "sentiment_distribution": {
    "positive": 3,
    "neutral": 1
  },
  "average_score": 0.787,
  "dominant_sentiment": "positive",
  "summary": "Over the last 7 days for 'technology', the overall sentiment is **positive** with an average score of 0.79. Analyzed 4 articles."
}
```

**Example:**
```powershell
$body = @{ topic = "AI stocks"; days = 30 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8001/news-chat/sentiment" `
    -Method Post -Body $body -ContentType "application/json"
```

### 5. Get Statistics

**GET** `/news-chat/stats`

Get general statistics about the news database.

**Response:**
```json
{
  "total_articles": 4,
  "last_30_days": {
    "sentiment_distribution": {
      "neutral": 1,
      "positive": 3
    },
    "average_score": 0.788,
    "dominant_sentiment": "positive"
  },
  "timestamp": "2025-12-22T14:06:49.817919"
}
```

### 6. Health Check

**GET** `/news-chat/health`

Check if the news chat service is healthy and can connect to Weaviate.

**Response:**
```json
{
  "status": "healthy",
  "weaviate_connected": true,
  "collection": "RSSNews",
  "sample_count": 1,
  "timestamp": "2025-12-22T14:06:03.227346"
}
```

## Testing the Complete Pipeline

### 1. Insert News into MongoDB
```powershell
docker exec research_mongo mongosh -u research -p user `
  --authenticationDatabase research_db research_db `
  --eval 'db.rss_news.insertOne({
    title: "New AI Breakthrough",
    link: "http://tech.com/ai-news",
    content: "Revolutionary AI technology announced",
    clean_text: "AI breakthrough announced",
    published: new Date(),
    summary: "Major advancement in artificial intelligence",
    sentiment: "positive",
    score: 0.88
  })'
```

### 2. Wait for CDC Processing (2-3 seconds)
The system automatically:
- Captures the change via Debezium
- Sends to Kafka topic
- Consumer processes and syncs to Weaviate
- Creates vector embeddings via Ollama

### 3. Query the News
```powershell
$body = @{
    message = "Tell me about AI breakthroughs"
    context_limit = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/news-chat/ask" `
    -Method Post -Body $body -ContentType "application/json"
```

## Data Model

### News Article Schema (MongoDB)
```javascript
{
  _id: ObjectId,
  title: String,
  link: String,
  content: String,
  clean_text: String,
  published: Date,
  summary: String,
  sentiment: String,  // "positive", "negative", "neutral"
  score: Number       // 0.0 to 1.0
}
```

### Weaviate Collection: RSSNews
- **Vectorizer**: text2vec-ollama (nomic-embed-text)
- **Vectorized Fields**: title, content, clean_text, summary
- **Properties**: mongoId, title, link, content, clean_text, published, summary, sentiment, score

## Configuration

### Environment Variables
```env
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3.2
WEAVIATE_HOST=weaviate
WEAVIATE_PORT=8080
```

## Pipeline Status

Check all components:
```powershell
# MongoDB documents
docker exec research_mongo mongosh -u research -p user `
  --authenticationDatabase research_db research_db `
  --eval 'db.rss_news.countDocuments({})'

# Weaviate objects
(Invoke-RestMethod -Uri 'http://localhost:8080/v1/objects?class=RSSNews&limit=1').totalResults

# API health
Invoke-RestMethod -Uri "http://localhost:8001/news-chat/health"
```

## Error Handling

All endpoints return standard HTTP status codes:
- **200**: Success
- **400**: Bad Request (invalid parameters)
- **500**: Internal Server Error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Performance Considerations

- **Context Limit**: Higher values (>10) may slow down response time
- **Search Limit**: Keep under 50 for optimal performance
- **Caching**: Responses are not cached; each request triggers fresh retrieval
- **Vector Search**: Weaviate handles embedding generation automatically

## Future Enhancements

- [ ] Conversation history/context
- [ ] Multi-turn dialogue support
- [ ] Citation linking in responses
- [ ] Real-time streaming responses
- [ ] Custom sentiment thresholds
- [ ] Date range filtering
- [ ] Bookmark/favorite articles
- [ ] Export capabilities

## Support

For issues or questions:
1. Check service health: `/news-chat/health`
2. Review backend logs: `docker logs research_backend`
3. Verify Weaviate connection: `docker logs research_consumer`
4. Check Kafka messages: `docker logs kafka-connect_new`
