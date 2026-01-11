# Testing Guide - General Responder

## Prerequisites

1. **Start all services:**
   ```powershell
   docker compose up -d
   ```

2. **Verify services are running:**
   ```powershell
   docker ps
   ```
   You should see: `research_backend`, `research_mongo`, `ollama_new`, `research-project-weaviate-1`

3. **Wait for services to be ready (~15 seconds)**

---

## Testing Methods

### Option 1: Quick PowerShell Test (Easiest)

```powershell
.\test_simple.ps1
```

This will test:
- ✓ API health check
- ✓ Simple greeting (no tools)
- ✓ News search query (with tools)

---

### Option 2: Python Test

```powershell
python test_simple.py
```

---

### Option 3: Manual API Testing

#### Test 1: Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/" -Method Get
```

#### Test 2: Simple Greeting
```powershell
$body = @{ message = "Hello!"; user_id = "test" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8001/chat/message" -Method Post -ContentType "application/json" -Body $body
```

#### Test 3: News Search
```powershell
$body = @{ message = "Find me news about technology"; user_id = "test" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8001/chat/message" -Method Post -ContentType "application/json" -Body $body
```

---

### Option 4: Using curl

#### Health Check
```bash
curl http://localhost:8001/
```

#### Send Message
```bash
curl -X POST http://localhost:8001/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "user_id": "test"}'
```

---

### Option 5: Postman / Insomnia

1. **Create POST request to:** `http://localhost:8001/chat/message`

2. **Headers:**
   ```
   Content-Type: application/json
   ```

3. **Body (raw JSON):**
   ```json
   {
     "message": "Hello!",
     "user_id": "test_user"
   }
   ```

4. **Send** and check response

---

## Expected Responses

### Success Response Format:
```json
{
  "status": "success",
  "message": "Hello!",
  "response": "Hi! How can I help you today?",
  "intent": "general",
  "used_tools": false,
  "tool_calls": []
}
```

### When Tools Are Used:
```json
{
  "status": "success",
  "message": "Find news about tech",
  "response": "Here are the latest tech news...",
  "intent": "general",
  "used_tools": true,
  "tool_calls": [
    {
      "name": "mongo_find_by_filter",
      "args": {"filter_dict": {...}, "limit": 10}
    }
  ]
}
```

---

## Troubleshooting

### API Not Responding

1. **Check if backend is running:**
   ```powershell
   docker ps | Select-String "research_backend"
   ```

2. **Check backend logs:**
   ```powershell
   docker logs research_backend --tail 50
   ```

3. **Restart backend:**
   ```powershell
   docker compose restart backend
   ```

### LLM Errors

If you see errors like "model not found" or "tools not supported":

1. **Check Ollama is running:**
   ```powershell
   docker ps | Select-String "ollama"
   ```

2. **Check which model is configured:**
   ```powershell
   docker logs research_backend | Select-String "model"
   ```

3. **The system should fallback gracefully** - you'll still get responses, just without tool usage

### MongoDB Connection Issues

1. **Check MongoDB is running:**
   ```powershell
   docker ps | Select-String "mongo"
   ```

2. **Test MongoDB connection:**
   ```powershell
   docker exec research_mongo mongosh --eval "db.adminCommand('ping')"
   ```

---

## Understanding Test Results

### ✅ What Success Looks Like:

**Test 1 (Greeting):**
- Intent: `general`
- Used Tools: `false`
- Gets a conversational response

**Test 2 (News Search):**
- Intent: `general`
- Used Tools: `true` (if model supports it) or `false` (fallback)
- Gets response with news information

### ⚠️ Common Issues:

1. **"NoneType has no attribute 'ainvoke'"**
   - Fixed ✓ (lazy initialization implemented)

2. **"model does not support tools"**
   - Expected for llama3.2
   - System falls back to no-tool mode
   - Still provides responses

3. **Connection timeout**
   - LLM taking too long to respond
   - Normal for first request (model loading)
   - Wait 30-60 seconds and retry

---

## Quick Debug Commands

```powershell
# View all logs
docker logs research_backend

# Follow logs in real-time
docker logs research_backend -f

# Check recent errors
docker logs research_backend --tail 100 | Select-String "error"

# Restart everything
docker compose restart

# Rebuild and restart
docker compose up --build -d
```

---

## Test Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `http://localhost:8001/` | GET | Health check |
| `http://localhost:8001/chat/message` | POST | Send message to general responder |
| `http://localhost:8001/chat/test` | GET | Automated test suite |
| `http://localhost:8001/rss/latest` | GET | View latest RSS news in database |

---

## Next Steps

Once tests pass:
1. ✓ General responder is working
2. ✓ Tool integration is functional
3. Try different queries to see tool usage
4. Check logs to see tool execution flow
5. Add more tools as needed

---

## Support

If tests fail, provide:
1. Output of `docker ps`
2. Output of `docker logs research_backend --tail 100`
3. The test command you ran
4. The error message received
