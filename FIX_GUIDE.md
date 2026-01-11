# 🔧 Quick Fix Guide: RSS Summary & Sentiment Not Working

## Problem
Summary and sentiment generation with Ollama LLM is not working or not saving to MongoDB.

##  Complete Solution

### Step 1: Update Docker Compose Configuration

The backend needs proper environment variables to connect to Ollama. Your docker-compose.yml has been updated with:

```yaml
backend:
  environment:
    - MONGO_URI=mongodb://research:user@mongo:27017/research_db?authSource=admin
    - DB_NAME=research_db
    - OLLAMA_HOST=http://ollama:11434
    - OLLAMA_MODEL=llama3.2
    - OLLAMA_TEMPERATURE=0.2
  depends_on:
    - mongo
    - ollama  # Added this dependency
```

### Step 2: Pull the Ollama Model

The model must be downloaded before it can be used:

```powershell
# Check if model exists
docker exec ollama_new ollama list

# Pull the model (one-time setup)
docker exec ollama_new ollama pull llama3.2

# Alternative models if llama3.2 doesn't work:
docker exec ollama_new ollama pull llama3
docker exec ollama_new ollama pull mistral
```

### Step 3: Restart Services

```powershell
# Restart backend to load new environment variables
docker-compose restart backend

# Or restart everything
docker-compose down
docker-compose up -d
```

### Step 4: Test the System

Run the automated test script:

```powershell
# Enter backend container
docker exec -it research_backend bash

# Run test
python test_rss_flow.py

# Exit
exit
```

### Step 5: Use the API

```powershell
# Collect news with LLM processing
Invoke-WebRequest -Uri http://localhost:8001/rss/collect

# View stored news
Invoke-WebRequest -Uri http://localhost:8001/rss/latest?limit=5
```

### Step 6: Verify in MongoDB

```powershell
# Connect to MongoDB
docker exec -it research_mongo mongosh -u research -p user --authenticationDatabase admin

# In MongoDB shell:
use research_db
db.rss_news.find().limit(1).pretty()
exit
```

---

##  What Was Fixed

### 1. Environment Variables
**Before:** Backend had no OLLAMA_HOST configuration
**After:** Added complete Ollama configuration to docker-compose.yml

### 2. RSS Service Improvements
**Before:** JSON parsing could fail with unclear errors
**After:** 
- Added robust JSON extraction from LLM responses
- Better error handling
- Text length limiting to avoid token limits
- Response validation

### 3. Sentiment Analysis
**Before:** Could fail silently or return invalid JSON
**After:**
- Explicit JSON format instructions
- Regex-based JSON extraction
- Field validation
- Default fallback values

### 4. Summary Generation
**Before:** Could include unwanted prefixes
**After:**
- Cleaner prompt
- Automatic prefix removal
- Length validation

### 5. Test Infrastructure
**Created:**
- `test_rss_flow.py` - Complete system test
- `quick-start.ps1` - Automated setup script
- `SETUP_GUIDE.md` - Comprehensive documentation

---

##  Automated Quick Start

Simply run:

```powershell
.\quick-start.ps1
```

This script will:
1.  Check Docker installation
2.  Start all services
3.  Verify service health
4.  Pull Ollama model if needed
5.  Test backend connectivity
6.  Run complete system test

---

##  Common Issues & Fixes

### Issue: "Connection refused to Ollama"
```powershell
# Fix: Restart Ollama container
docker-compose restart ollama

# Check logs
docker logs ollama_new

# Test directly
curl http://localhost:11434/api/tags
```

### Issue: "Model not found"
```powershell
# Fix: Pull the model
docker exec ollama_new ollama pull llama3.2

# Verify
docker exec ollama_new ollama list
```

### Issue: "MongoDB authentication failed"
```powershell
# Fix: Check credentials match in docker-compose.yml
# Username: research
# Password: user

# Restart MongoDB
docker-compose restart mongo
```

### Issue: "Summary/Sentiment still null in database"
```powershell
# Check backend logs for errors
docker-compose logs backend | Select-String -Pattern "error"

# Run diagnostic test
docker exec -it research_backend python test_rss_flow.py
```

---

##  Expected Results

### Successful API Response:
```json
{
  "status": "success",
  "message": "RSS collection completed",
  "feeds": [
    {
      "feed": "https://economynext.com/feed/",
      "result": {
        "status": "success",
        "new_articles": 5
      }
    }
  ]
}
```

### MongoDB Document with Summary & Sentiment:
```json
{
  "_id": ObjectId("..."),
  "title": "Sri Lanka's economy shows recovery signs",
  "summary": "The article discusses positive economic indicators...",
  "sentiment": "positive",
  "score": 0.75,
  "created_at": ISODate("2025-12-15T...")
}
```

---

##  Verification Checklist

- [ ] Docker containers are running: `docker-compose ps`
- [ ] Ollama model is pulled: `docker exec ollama_new ollama list`
- [ ] Backend is responding: `curl http://localhost:8001/`
- [ ] MongoDB is accessible: `docker exec research_mongo mongosh --eval "db.version()"`
- [ ] Test script passes: `docker exec -it research_backend python test_rss_flow.py`
- [ ] API returns success: `curl http://localhost:8001/rss/collect`
- [ ] Database has documents: `db.rss_news.countDocuments()`
- [ ] Documents have summary field: `db.rss_news.find({summary: {$exists: true}})`
- [ ] Documents have sentiment field: `db.rss_news.find({sentiment: {$exists: true}})`

---

##  Support

If you still have issues after following this guide:

1. **Collect diagnostic info:**
   ```powershell
   docker-compose ps > logs.txt
   docker-compose logs >> logs.txt
   ```

2. **Check these files:**
   - [SETUP_GUIDE.md](./SETUP_GUIDE.md) - Detailed troubleshooting
   - [docker-compose.yml](./docker-compose.yml) - Service configuration
   - [backend/.env](./backend/.env) - Environment variables

3. **Restart from scratch:**
   ```powershell
   docker-compose down -v
   docker-compose up -d
   .\quick-start.ps1
   ```

---

**Status:**  Your system is now configured correctly!
**Next:** Run `.\quick-start.ps1` to start everything.
