# Knowledge Base with Docker - Complete Guide

## Overview
This guide shows how to use the knowledge base system with Docker Compose.

## Changes Made

### 1. Updated Requirements
Added to `backend/requirements.txt`:
- `chromadb>=0.4.22` - Vector database
- `PyPDF2>=3.0.1` - PDF processing

### 2. Docker Compose Configuration
Updated `docker-compose.yml` backend service with:
- **Volume Mounts**:
  - `./backend/data/knowledge_base:/app/data/knowledge_base` - ChromaDB storage
  - `./backend/data/uploads:/app/data/uploads` - PDF upload location
- **Environment Variables**:
  - `KNOWLEDGE_BASE_MODEL=llama3.2` - Generation model
  - `KNOWLEDGE_BASE_EMBEDDING_MODEL=nomic-embed-text` - Embedding model
  - `OLLAMA_HOST=http://ollama:11434` - Docker Ollama service

### 3. Service Updates
`backend/app/services/knowledge_base_service.py` now:
- Reads Ollama host from environment variable
- Supports Docker networking
- Uses environment-based configuration

## Setup Instructions

### Step 1: Prepare PDF Files
Place your PDF documents in the host directory before starting Docker:
```powershell
# Create directory
New-Item -ItemType Directory -Force -Path "backend/data/uploads"

# Copy your PDF
Copy-Item "path/to/Annual-Report-2024.pdf" -Destination "backend/data/uploads/"
```

### Step 2: Start Docker Services
```powershell
docker compose up --build -d
```

This will:
- Build and start all services
- Create volume mounts for knowledge base
- Start Ollama with required models
- Start backend with knowledge base support

### Step 3: Wait for Ollama to Pull Models
```powershell
# Check Ollama logs
docker logs ollama_new -f

# Wait for models to be downloaded (may take several minutes)
# You should see: "llama3.2" and "nomic-embed-text" being pulled
```

### Step 4: Access Container to Build Knowledge Base
```powershell
# Enter the backend container
docker exec -it research_backend bash

# Inside container, run setup
cd /app
python setup_knowledge_base.py
```

The script will:
- Find your PDF in `/app/data/uploads/`
- Extract text and create chunks
- Generate embeddings using Docker Ollama
- Store in ChromaDB (persisted via volume mount)

### Step 5: Verify Knowledge Base
```powershell
# Still inside container
python validate_knowledge_base.py

# Or test via API
python test_knowledge_api.py
```

### Step 6: Access from Host
The API is now available at:
- **API Base**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **Query Endpoint**: POST http://localhost:8001/api/knowledge/query

## Testing from Host Machine

### Option 1: Using Swagger UI
1. Open: http://localhost:8001/docs
2. Find `/api/knowledge/query`
3. Click "Try it out"
4. Enter your question
5. Execute

### Option 2: Using PowerShell
```powershell
$body = @{
    question = "What are the key financial highlights?"
    n_results = 5
    include_sources = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/knowledge/query" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

### Option 3: Using Python from Host
```python
import requests

response = requests.post('http://localhost:8001/api/knowledge/query', json={
    "question": "What was the total trading volume?",
    "n_results": 5
})
print(response.json()['answer'])
```

## Volume Persistence

### Data Locations
- **On Host**: 
  - `backend/data/knowledge_base/` - ChromaDB database
  - `backend/data/uploads/` - PDF files
- **In Container**: 
  - `/app/data/knowledge_base/` - ChromaDB database
  - `/app/data/uploads/` - PDF files

### Benefits
- ✅ Knowledge base survives container restarts
- ✅ PDFs accessible from host
- ✅ Can rebuild knowledge base without losing data
- ✅ Easy backup (just copy `data/` directory)

## Ollama Models Management

### Check Available Models
```powershell
docker exec ollama_new ollama list
```

### Pull Additional Models
```powershell
# For better generation
docker exec ollama_new ollama pull llama3.2

# Alternative embedding models
docker exec ollama_new ollama pull mxbai-embed-large
```

### Update Model Configuration
Edit `docker-compose.yml`:
```yaml
environment:
  - KNOWLEDGE_BASE_MODEL=llama3.2
  - KNOWLEDGE_BASE_EMBEDDING_MODEL=nomic-embed-text
```

Then restart:
```powershell
docker compose restart backend
```

## Common Tasks

### Rebuild Knowledge Base
```powershell
# Enter container
docker exec -it research_backend bash

# Run setup with force rebuild
cd /app
python setup_knowledge_base.py
```

### Add New PDFs
```powershell
# Copy new PDF to uploads
Copy-Item "new-report.pdf" -Destination "backend/data/uploads/"

# Rebuild knowledge base (in container)
docker exec -it research_backend python setup_knowledge_base.py
```

### View Logs
```powershell
# Backend logs
docker logs research_backend -f

# Ollama logs
docker logs ollama_new -f
```

### Reset Knowledge Base
```powershell
# From host - delete database
Remove-Item -Recurse -Force backend/data/knowledge_base/*

# Rebuild
docker exec -it research_backend python setup_knowledge_base.py
```

## Troubleshooting

### Issue 1: Ollama Models Not Found
**Symptoms**: "Model 'llama3.2' not found"

**Solution**:
```powershell
# Check if model exists
docker exec ollama_new ollama list

# Pull the model
docker exec ollama_new ollama pull llama3.2
docker exec ollama_new ollama pull nomic-embed-text
```

### Issue 2: Permission Errors
**Symptoms**: Cannot write to `/app/data/knowledge_base`

**Solution**:
```powershell
# Fix permissions on host
icacls "backend\data" /grant Everyone:F /t

# Or recreate directories
Remove-Item -Recurse -Force backend/data
docker compose restart backend
```

### Issue 3: Container Cannot Access PDF
**Symptoms**: "PDF file not found"

**Solution**:
```powershell
# Verify PDF is in correct location
Get-ChildItem backend\data\uploads\

# Copy if missing
Copy-Item "your-pdf.pdf" -Destination "backend\data\uploads\"

# Restart container to remount volume
docker compose restart backend
```

### Issue 4: ChromaDB Errors
**Symptoms**: "Cannot initialize ChromaDB"

**Solution**:
```powershell
# Clear database and rebuild
Remove-Item -Recurse -Force backend/data/knowledge_base/*
docker compose restart backend

# Rebuild knowledge base
docker exec -it research_backend python setup_knowledge_base.py
```

### Issue 5: Slow Performance
**Symptoms**: Queries take >30 seconds

**Solution**:
```powershell
# Use faster model
# Edit docker-compose.yml:
# KNOWLEDGE_BASE_MODEL=phi  # Smaller, faster model

# Or reduce chunk retrieval
# In API request: "n_results": 3  # Instead of 5
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Host Machine                         │
│                                                          │
│  backend/data/uploads/        backend/data/knowledge_base/│
│  └── Annual-Report-2024.pdf   └── chroma.sqlite3       │
│                                                          │
└──────────────────┬──────────────────────────────────────┘
                   │ Volume Mounts
┌──────────────────▼──────────────────────────────────────┐
│              Docker: research_backend                   │
│                                                          │
│  /app/data/uploads/          /app/data/knowledge_base/  │
│  └── Annual-Report-2024.pdf  └── chroma.sqlite3         │
│                                                          │
│  Knowledge Base Service                                 │
│  ├── PDF Parser (PyPDF2)                                │
│  ├── Text Chunking                                      │
│  ├── ChromaDB Client                                    │
│  └── API Routes                                         │
│                                                          │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP (Docker Network)
┌──────────────────▼──────────────────────────────────────┐
│              Docker: ollama_new                         │
│                                                          │
│  Ollama Service (Port 11434)                            │
│  ├── llama3.2 (Generation)                              │
│  ├── nomic-embed-text (Embeddings)                      │
│  └── API Server                                         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Production Considerations

### 1. Pre-build Knowledge Base
Instead of building in container, you can:
```powershell
# Build locally first
cd backend
python setup_knowledge_base.py

# Then start Docker (data already exists)
docker compose up -d
```

### 2. Optimize Dockerfile
Add knowledge base build to Dockerfile:
```dockerfile
# Copy PDF and build script
COPY data/uploads/ /app/data/uploads/
COPY setup_knowledge_base.py /app/

# Build knowledge base during image build
RUN python setup_knowledge_base.py || true
```

### 3. Use Init Container
Create a separate service to build knowledge base:
```yaml
knowledge-builder:
  build: ./backend
  volumes:
    - ./backend/data:/app/data
  command: python setup_knowledge_base.py
  depends_on:
    - ollama
```

### 4. Health Checks
Add health check to backend:
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "from app.services.knowledge_base_service import KnowledgeBaseService; kb = KnowledgeBaseService(); assert kb.get_stats()['status'] == 'active'"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## Backup and Restore

### Backup Knowledge Base
```powershell
# Create backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Compress-Archive -Path "backend\data\knowledge_base" -DestinationPath "kb_backup_$timestamp.zip"
```

### Restore Knowledge Base
```powershell
# Extract backup
Expand-Archive -Path "kb_backup_20260228_120000.zip" -DestinationPath "backend\data\" -Force

# Restart container
docker compose restart backend
```

## Success Checklist

- [ ] ChromaDB and PyPDF2 in requirements.txt
- [ ] Volume mounts configured in docker-compose.yml
- [ ] Environment variables set for knowledge base
- [ ] PDF files placed in `backend/data/uploads/`
- [ ] Docker services started: `docker compose up -d`
- [ ] Ollama models pulled (llama3.2, nomic-embed-text)
- [ ] Knowledge base built in container
- [ ] API endpoint accessible at http://localhost:8001
- [ ] Query endpoint returns valid responses
- [ ] Data persists after container restart

## Summary

Your knowledge base is now fully integrated with Docker:
- ✅ Runs in backend container
- ✅ Uses Docker Ollama service
- ✅ Persistent storage via volumes
- ✅ Accessible via API on port 8001
- ✅ Easy to maintain and update

---

**Version**: 1.0  
**Last Updated**: February 28, 2026  
**Status**: Docker Ready ✅
