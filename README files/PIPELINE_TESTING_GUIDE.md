# Knowledge Base Pipeline Testing Guide

## Overview
This guide helps you test the complete pipeline:
- **Frontend** (React) → **Backend** (FastAPI) → **Ollama** (LLM) → **ChromaDB** (Knowledge Base) / **Weaviate** (News)

## Quick Start

### 1. Check All Services Are Running
```powershell
python quick_health_check.py
```

This verifies all services are responding (no actual queries).

### 2. Test Backend APIs Directly

#### Test Knowledge Base Status
```powershell
curl http://localhost:8001/api/knowledge/stats
```

Expected response:
```json
{
  "status": "ready" or "active",
  "total_chunks": <number>,
  "model": "llama3.2",
  "embedding_model": "nomic-embed-text"
}
```

#### Test Knowledge Base Query
```powershell
curl -X POST http://localhost:8001/api/knowledge/query ^
  -H "Content-Type: application/json" ^
  -d "{\"question\": \"What are the key highlights?\", \"n_results\": 3}"
```

**Note**: This will take 10-30 seconds as Ollama generates the response.

#### Test News RAG Health
```powershell
curl http://localhost:8001/news-chat/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "vector_db": "connected"
}
```

#### Test News Query
```powershell
curl -X POST http://localhost:8001/news-chat/ask ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"What is the latest news?\", \"use_rag\": true}"
```

**Note**: This also takes time for LLM response generation.

### 3. Test Frontend Integration

1. **Open Browser**: Navigate to http://localhost:3001

2. **Test News Quick Actions**:
   - Click "Latest News" button
   - Click "Market Trends" button
   - Click "Sentiment Analysis" button
   
3. **Test Knowledge Base Quick Actions**:
   - Click "CSE Report Highlights" button
   - Click "Financial Overview" button
   - Click "Trading Statistics" button

4. **Test Custom Queries**:
   - Type a custom question in the chat box
   - Verify response appears after ~10-30 seconds

### 4. Verify Data Flow

#### Check Weaviate has News Data
```powershell
curl http://localhost:8080/v1/objects?class=RSSNews^&limit=1
```

Should return news articles. If empty, run:
```powershell
python backend/sync_to_weaviate.py
```

#### Check ChromaDB has Knowledge Base Data
```powershell
cd backend
python -c "from app.services.knowledge_base_service import KnowledgeBaseService; kb = KnowledgeBaseService(); print(kb.get_stats())"
```

If not initialized, run:
```powershell
cd backend
python setup_knowledge_base.py
```

## Troubleshooting

### Issue: Queries Timeout
**Cause**: Ollama is generating responses slowly
**Solution**: 
- First query after startup is always slow (model loading)
- Subsequent queries should be faster
- Check Ollama logs: `docker logs ollama_new`

### Issue: Empty Responses
**Cause**: No data in ChromaDB or Weaviate
**Solutions**:
- For Knowledge Base: `python backend/setup_knowledge_base.py`
- For News: `python backend/sync_to_weaviate.py`

### Issue: Connection Errors
**Cause**: Services not running
**Solution**: `docker compose up -d`

### Issue: "Knowledge Base Not Ready"
**Cause**: ChromaDB not initialized
**Solution**:
```powershell
cd backend
python setup_knowledge_base.py
```

## Complete End-to-End Test Flow

1. **Run health check**:
   ```powershell
   python quick_health_check.py
   ```

2. **Test Backend Knowledge Base API**:
   ```powershell
   # Check status
   curl http://localhost:8001/api/knowledge/stats
   
   # Test query (wait ~20 seconds)
   curl -X POST http://localhost:8001/api/knowledge/query ^
     -H "Content-Type: application/json" ^
     -d "{\"question\": \"What are the key financial highlights?\"}"
   ```

3. **Test Backend News API**:
   ```powershell
   # Check health
   curl http://localhost:8001/news-chat/health
   
   # Test query (wait ~20 seconds)
   curl -X POST http://localhost:8001/news-chat/ask ^
     -H "Content-Type: application/json" ^
     -d "{\"message\": \"What is the latest market news?\"}"
   ```

4. **Test Frontend**:
   - Open http://localhost:3001
   - Click various Quick Action buttons
   - Type custom queries
   - Verify responses appear

## Expected Response Times

- **Health checks**: < 1 second
- **Stats/Status**: < 1 second
- **First query after startup**: 20-60 seconds (model loading)
- **Subsequent queries**: 10-30 seconds
- **Simple queries**: 10-15 seconds
- **Complex queries**: 20-30 seconds

## Success Criteria

✅ **All services respond to health checks**
✅ **Knowledge Base stats show chunks loaded**
✅ **News RAG health shows "healthy"**
✅ **Backend queries return answers (not errors)**
✅ **Frontend buttons trigger backend queries**
✅ **Responses display in frontend UI**

## Full Automated Test (Takes 3-5 minutes)

```powershell
python test_full_pipeline.py
```

This runs comprehensive tests but takes longer due to LLM query timeouts.

## Docker Services Check

```powershell
docker ps
```

Should show all services running:
- research_backend
- research_frontend
- ollama_new
- research-project-weaviate-1
- research_mongo

## Logs for Debugging

```powershell
# Backend logs
docker logs research_backend --tail 50 -f

# Ollama logs
docker logs ollama_new --tail 50 -f

# Weaviate logs
docker logs research-project-weaviate-1 --tail 50 -f
```

## Quick Manual Test Checklist

- [ ] Services running: `docker ps`
- [ ] Quick health: `python quick_health_check.py`
- [ ] Backend root: http://localhost:8001/
- [ ] Frontend loads: http://localhost:3001/
- [ ] Knowledge stats: `curl http://localhost:8001/api/knowledge/stats`
- [ ] News health: `curl http://localhost:8001/news-chat/health`
- [ ] Test KB query via curl (wait ~20s)
- [ ] Test news query via curl (wait ~20s)
- [ ] Test frontend Quick Actions
- [ ] Verify responses appear in frontend

## Notes

- **First query is always slow** - Ollama loads models on first use
- **Timeouts are normal** for the first request after container restart
- **ChromaDB data** persists in `backend/data/knowledge_base/`
- **Weaviate data** persists in `weaviate_data/`
- **Temperature settings** affect response generation time
