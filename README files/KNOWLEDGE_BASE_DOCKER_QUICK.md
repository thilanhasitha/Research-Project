# Knowledge Base + Docker - Quick Reference

## 🚀 Quick Start (First Time)

```powershell
# 1. Place PDF in uploads directory
New-Item -ItemType Directory -Force -Path "backend/data/uploads"
Copy-Item "path/to/your/Annual-Report-2024.pdf" -Destination "backend/data/uploads/"

# 2. Start Docker services
docker compose up --build -d

# 3. Wait for Ollama models (this takes 5-10 minutes first time)
docker logs ollama_new -f
# Press Ctrl+C when you see "All models ready"

# 4. Build knowledge base
docker exec -it research_backend python setup_knowledge_base.py

# 5. Test it
docker exec -it research_backend python test_knowledge_api.py
```

## 📌 Essential Commands

### Start/Stop Docker
```powershell
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Rebuild and restart
docker compose up --build -d

# View all logs
docker compose logs -f

# View specific service logs
docker logs research_backend -f
docker logs ollama_new -f
```

### Knowledge Base Management
```powershell
# Build/rebuild knowledge base
docker exec -it research_backend python setup_knowledge_base.py

# Validate system
docker exec -it research_backend python validate_knowledge_base.py

# Test API
docker exec -it research_backend python test_knowledge_api.py

# Interactive test
docker exec -it research_backend python test_knowledge_base.py

# View knowledge base stats
docker exec -it research_backend python -c "from app.services.knowledge_base_service import KnowledgeBaseService; kb = KnowledgeBaseService(); print(kb.get_stats())"
```

### Ollama Commands
```powershell
# List models
docker exec ollama_new ollama list

# Pull a model
docker exec ollama_new ollama pull llama3.2

# Test model
docker exec ollama_new ollama run llama3.2 "Hello, how are you?"
```

### Access Container
```powershell
# Backend shell
docker exec -it research_backend bash

# Ollama shell
docker exec -it ollama_new bash

# Inside container, you can run:
# cd /app
# python setup_knowledge_base.py
# python test_knowledge_api.py
```

### File Management
```powershell
# Add new PDF
Copy-Item "new-report.pdf" -Destination "backend/data/uploads/"

# List uploaded PDFs
Get-ChildItem backend\data\uploads\

# View knowledge base files
Get-ChildItem backend\data\knowledge_base\

# Clear knowledge base (requires rebuild)
Remove-Item -Recurse -Force backend\data\knowledge_base\*
```

## 🌐 API Endpoints

After starting Docker, access these URLs:

- **API Documentation**: http://localhost:8001/docs
- **Main API**: http://localhost:8001
- **Frontend**: http://localhost:3001
- **Weaviate**: http://localhost:8080

### Test Query (PowerShell)
```powershell
$body = @{
    question = "What are the key financial highlights?"
    n_results = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/knowledge/query" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

### Test Query (cURL)
```bash
curl -X POST "http://localhost:8001/api/knowledge/query" \
  -H "Content-Type: application/json" \
  -d '{"question":"What was the revenue?","n_results":5}'
```

## 🔧 Troubleshooting

### Problem: "Ollama not ready"
```powershell
# Check Ollama status
docker logs ollama_new -f

# Restart Ollama
docker restart ollama_new

# Wait for it to be ready (check logs)
```

### Problem: "Model not found"
```powershell
# Pull required models
docker exec ollama_new ollama pull llama3.2
docker exec ollama_new ollama pull nomic-embed-text

# Restart backend
docker restart research_backend
```

### Problem: "PDF not found"
```powershell
# Check if PDF exists
Get-ChildItem backend\data\uploads\

# Copy PDF if missing
Copy-Item "your-pdf.pdf" -Destination "backend\data\uploads\"

# Restart and rebuild
docker restart research_backend
docker exec -it research_backend python setup_knowledge_base.py
```

### Problem: "Cannot write to directory"
```powershell
# Fix permissions
icacls "backend\data" /grant Everyone:F /t

# Or recreate
Remove-Item -Recurse -Force backend\data
New-Item -ItemType Directory -Force -Path "backend/data/uploads"
docker restart research_backend
```

### Problem: "Knowledge base empty"
```powershell
# Rebuild it
docker exec -it research_backend python setup_knowledge_base.py
```

## 📊 Check Status

```powershell
# All containers
docker ps

# Backend status
docker exec research_backend python -c "from app.services.knowledge_base_service import KnowledgeBaseService; print(KnowledgeBaseService().get_stats())"

# Ollama status
docker exec ollama_new ollama list

# API health
Invoke-RestMethod http://localhost:8001/api/knowledge/health
```

## 🔄 Common Workflows

### Add New Document
```powershell
# 1. Copy PDF
Copy-Item "new-doc.pdf" -Destination "backend/data/uploads/"

# 2. Rebuild knowledge base
docker exec -it research_backend python setup_knowledge_base.py

# 3. Test
Invoke-RestMethod -Uri "http://localhost:8001/api/knowledge/query" `
    -Method Post -ContentType "application/json" `
    -Body '{"question":"test","n_results":3}'
```

### Update Configuration
```powershell
# 1. Edit docker-compose.yml
# Change KNOWLEDGE_BASE_MODEL or other env vars

# 2. Restart backend
docker compose restart backend

# 3. Rebuild knowledge base (if needed)
docker exec -it research_backend python setup_knowledge_base.py
```

### Full Reset
```powershell
# 1. Stop everything
docker compose down

# 2. Clear data
Remove-Item -Recurse -Force backend\data\knowledge_base\*

# 3. Start fresh
docker compose up -d

# 4. Wait for Ollama
docker logs ollama_new -f

# 5. Rebuild
docker exec -it research_backend python setup_knowledge_base.py
```

## 📦 What's Included

### Services Running
- **backend** (port 8001) - FastAPI with knowledge base
- **frontend** (port 3001) - React frontend
- **ollama** (port 11434) - LLM service
- **weaviate** (port 8080) - Vector database for RAG
- **mongo** (port 27017) - Database
- **kafka** (port 9092) - Message broker
- **consumer** - News processing service

### Volume Mounts
- `backend/data/knowledge_base` → `/app/data/knowledge_base` (ChromaDB)
- `backend/data/uploads` → `/app/data/uploads` (PDFs)

### Models Auto-Pulled
- `llama3` - Main generation model
- `llama3.2` - Knowledge base generation
- `nomic-embed-text` - Embeddings

## ✅ Success Checklist

- [ ] Docker installed and running
- [ ] PDF file in `backend/data/uploads/`
- [ ] `docker compose up -d` completed
- [ ] Ollama models pulled (check logs)
- [ ] Knowledge base built successfully
- [ ] API accessible at http://localhost:8001/docs
- [ ] Query endpoint returns valid responses

## 📚 Full Documentation

- **Complete Guide**: [KNOWLEDGE_BASE_DOCKER_GUIDE.md](KNOWLEDGE_BASE_DOCKER_GUIDE.md)
- **Local Setup**: [KNOWLEDGE_BASE_FIX_GUIDE.md](KNOWLEDGE_BASE_FIX_GUIDE.md)
- **API Details**: [KNOWLEDGE_BASE_SETUP.md](KNOWLEDGE_BASE_SETUP.md)

---

**Quick Help**: `docker exec -it research_backend python validate_knowledge_base.py`
