#  Setup Guide: RSS News Collection with LLM Summary & Sentiment

This guide will help you set up and troubleshoot the RSS news collection system with Ollama LLM for summary and sentiment generation.

---

##  Prerequisites

1. **Docker & Docker Compose** installed
2. **Python 3.11+** (for local testing)
3. **Git** (for version control)

---

##  Step-by-Step Setup

### 1. Start All Services

```bash
# From project root directory
cd c:\Users\USER\OneDrive\Documents\GitHub\Research-Project

# Start all containers
docker-compose up -d

# Check if all services are running
docker-compose ps
```

Expected services:
-  `research_backend` (port 8001)
-  `ollama_new` (port 11434)
-  `research_mongo` (port 27017)
-  `weaviate` (port 8080)
-  `kafka_new` (port 9092)
-  `kafka-connect_new` (port 8083)

---

### 2. Pull Ollama Model

The LLM model needs to be downloaded inside the Ollama container:

```bash
# Check available models
docker exec ollama_new ollama list

# Pull the required model (llama3.2 or llama3)
docker exec ollama_new ollama pull llama3.2

# If llama3.2 is not available, use llama3
docker exec ollama_new ollama pull llama3

# Verify the model is ready
docker exec ollama_new ollama list
```

**Update `.env` file** if you're using a different model:
```env
OLLAMA_MODEL=llama3.2  # or llama3, or mistral, etc.
```

---

### 3. Configure Environment Variables

#### For Docker (Production):
Edit `backend/.env`:
```env
MONGO_URI=mongodb://research:user@mongo:27017/research_db?authSource=admin
DB_NAME=research_db
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3.2
OLLAMA_TEMPERATURE=0.2
```

#### For Local Development:
Edit `backend/.env.local`:
```env
MONGO_URI=mongodb://localhost:27017  # or your MongoDB Atlas URI
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

---

### 4. Restart Backend Service

After configuring environment variables:

```bash
# Restart backend to load new .env
docker-compose restart backend

# Check logs
docker-compose logs -f backend
```

---

### 5. Test the System

#### Option A: Using the Test Script

```bash
# Enter backend container
docker exec -it research_backend bash

# Run the test script
python test_rss_flow.py

# Exit container
exit
```

The test will check:
1. MongoDB connection 
2. Ollama LLM availability 
3. RSS feed fetching 
4. Summary generation 
5. Sentiment analysis 
6. Complete flow (save to MongoDB) 

#### Option B: Using API Endpoints

```bash
# Collect RSS news (this triggers LLM processing)
curl http://localhost:8001/rss/collect

# Get latest news from database
curl http://localhost:8001/rss/latest?limit=5
```

---

### 6. Verify in MongoDB

```bash
# Connect to MongoDB container
docker exec -it research_mongo mongosh -u research -p user --authenticationDatabase admin

# Switch to database
use research_db

# Check stored news
db.rss_news.find().limit(1).pretty()

# Count documents
db.rss_news.countDocuments()

# Check if summary and sentiment exist
db.rss_news.find(
  { summary: { $exists: true }, sentiment: { $exists: true } }
).limit(3).pretty()

# Exit
exit
```

---

##  Troubleshooting

### Issue 1: "Ollama connection refused"

**Symptoms:**
```
 Ollama test failed: Connection refused
```

**Solutions:**
1. Check if Ollama container is running:
   ```bash
   docker ps | grep ollama
   ```

2. Check Ollama logs:
   ```bash
   docker logs ollama_new
   ```

3. Test Ollama directly:
   ```bash
   curl http://localhost:11434/api/tags
   ```

4. Restart Ollama:
   ```bash
   docker-compose restart ollama
   ```

---

### Issue 2: "Model not found"

**Symptoms:**
```
 model 'llama3.2' not found
```

**Solutions:**
1. Pull the model:
   ```bash
   docker exec ollama_new ollama pull llama3.2
   ```

2. Or use a different model:
   ```bash
   docker exec ollama_new ollama pull mistral
   # Update .env: OLLAMA_MODEL=mistral
   docker-compose restart backend
   ```

---

### Issue 3: "MongoDB connection failed"

**Symptoms:**
```
 MongoDB connection failed: Authentication failed
```

**Solutions:**
1. Check MongoDB is running:
   ```bash
   docker logs research_mongo
   ```

2. Verify credentials in `docker-compose.yml`:
   ```yaml
   MONGO_INITDB_ROOT_USERNAME: research
   MONGO_INITDB_ROOT_PASSWORD: user
   ```

3. Check `.env` matches credentials:
   ```env
   MONGO_URI=mongodb://research:user@mongo:27017/research_db?authSource=admin
   ```

---

### Issue 4: "Summary/Sentiment not saving"

**Symptoms:**
- API returns success but no summary/sentiment in database

**Solutions:**
1. Check backend logs:
   ```bash
   docker-compose logs backend | grep -i error
   ```

2. Verify LLM response format:
   ```bash
   docker exec -it research_backend python
   >>> from app.llm.LLMFactory import LLMFactory
   >>> from app.llm.client.ollama_client import OllamaClient
   >>> import asyncio
   >>> LLMFactory.register_provider("ollama", OllamaClient)
   >>> provider = LLMFactory.get_provider("ollama")
   >>> asyncio.run(provider.generate("Say hello"))
   ```

3. Check Ollama response time (slow responses may timeout):
   ```bash
   time docker exec ollama_new ollama run llama3.2 "Hello"
   ```

---

### Issue 5: "JSON parsing error in sentiment"

**Symptoms:**
```
 JSONDecodeError: Expecting value
```

**Cause:** LLM returns text instead of JSON

**Solution:** Update prompt in `rss_service.py` to be more explicit:

```python
async def analyze_sentiment(self, text: str):
    if not self.llm:
        return {"sentiment": "neutral", "score": 0}
    try:
        prompt = f"""
Analyze the sentiment of this financial news.
You MUST respond with ONLY valid JSON, no other text.

Format:
{{"sentiment": "positive", "score": 0.8, "reason": "brief explanation"}}

Sentiment options: positive, neutral, negative
Score range: -1 (very negative) to 1 (very positive)

Text to analyze: {text[:500]}

JSON response:
"""
        result = await self.llm.generate([prompt])
        
        # Try to extract JSON if there's extra text
        import re
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            result = json_match.group()
        
        return json.loads(result)
    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        return {"sentiment": "neutral", "score": 0, "reason": "parsing failed"}
```

---

##  Expected Output

When everything works correctly:

### API Response (`/rss/collect`):
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

### MongoDB Document:
```json
{
  "_id": ObjectId("..."),
  "title": "Sri Lanka's economy shows signs of recovery",
  "link": "https://economynext.com/article/...",
  "content": "Full HTML content...",
  "clean_text": "Cleaned text version...",
  "published": ISODate("2025-12-15T10:30:00Z"),
  "summary": "Sri Lanka's economy is showing positive signs with GDP growth of 4.5% in Q3 2025. Tourism and exports are the main drivers.",
  "sentiment": "positive",
  "score": 0.75,
  "created_at": ISODate("2025-12-15T12:00:00Z")
}
```

---

##  Quick Health Check Commands

```bash
# 1. Check all services
docker-compose ps

# 2. Test Ollama
curl http://localhost:11434/api/tags

# 3. Test Backend API
curl http://localhost:8001/

# 4. Test MongoDB
docker exec research_mongo mongosh -u research -p user --eval "db.adminCommand('ping')"

# 5. View backend logs
docker-compose logs -f backend

# 6. Run complete test
docker exec -it research_backend python test_rss_flow.py
```

---

##  Common Workflow

### Daily Usage:

```bash
# 1. Start services
docker-compose up -d

# 2. Collect news (manual trigger)
curl http://localhost:8001/rss/collect

# 3. View latest news
curl http://localhost:8001/rss/latest?limit=10 | jq

# 4. Check logs if issues
docker-compose logs backend ollama mongo
```

### Development Workflow:

```bash
# 1. Make code changes
code backend/app/services/news/rss_service.py

# 2. Restart backend only (fast)
docker-compose restart backend

# 3. Test
curl http://localhost:8001/rss/collect

# 4. Check logs
docker-compose logs -f backend
```

---

##  Additional Resources

- **Ollama Models**: https://ollama.com/library
- **FastAPI Docs**: http://localhost:8001/docs
- **MongoDB Compass**: mongodb://research:user@localhost:27017
- **Docker Compose Docs**: https://docs.docker.com/compose/

---

##  Still Having Issues?

1. Check all logs:
   ```bash
   docker-compose logs --tail=100
   ```

2. Restart everything:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

3. Check disk space:
   ```bash
   docker system df
   ```

4. Clean up and rebuild:
   ```bash
   docker-compose down -v
   docker-compose build --no-cache backend
   docker-compose up -d
   ```

---

**Good luck! 🚀**
