# Knowledge Base System - Complete Setup & Fix Guide

## Overview
This document provides a complete guide to set up and fix the knowledge base system for querying CSE Annual Reports.

## System Components

### 1. Core Service
- **File**: `backend/app/services/knowledge_base_service.py`
- **Features**:
  - PDF text extraction
  - Text chunking with overlap
  - Ollama embeddings generation
  - ChromaDB vector storage
  - Natural language querying
  - Confidence scoring
  - Enhanced error handling and retry logic

### 2. API Routes
- **File**: `backend/app/routes/knowledge_routes.py`
- **Endpoints**:
  - `POST /api/knowledge/query` - Ask questions
  - `POST /api/knowledge/build` - Build from local PDF
  - `POST /api/knowledge/upload-pdf` - Upload and build
  - `GET /api/knowledge/stats` - Get statistics
  - `GET /api/knowledge/health` - Health check
  - `DELETE /api/knowledge/reset` - Reset database

### 3. Setup & Testing Scripts
- `backend/init_knowledge_base_directories.py` - Initialize directories
- `backend/setup_knowledge_base.py` - Build knowledge base from PDF
- `backend/validate_knowledge_base.py` - Comprehensive system validation
- `backend/test_knowledge_base.py` - Interactive testing

## Quick Start (Step-by-Step)

### Step 1: Initialize Directories
```powershell
cd backend
python init_knowledge_base_directories.py
```

This creates:
- `data/knowledge_base/` - ChromaDB storage
- `data/uploads/` - PDF upload location
- `logs/` - Application logs

### Step 2: Install Dependencies
```powershell
# Activate virtual environment (if you have one)
& c:\Users\USER\OneDrive\Documents\GitHub\Research-Project\.venv\Scripts\Activate.ps1

# Install knowledge base dependencies
pip install chromadb ollama PyPDF2

# Verify installation
python -c "import chromadb, ollama, PyPDF2; print('All dependencies installed!')"
```

### Step 3: Setup Ollama

#### Install Ollama
1. Download from: https://ollama.ai
2. Install and start Ollama

#### Verify Ollama is Running
```powershell
# Check if Ollama process is running
Get-Process ollama -ErrorAction SilentlyContinue

# If not running, start it in a new terminal
ollama serve
```

#### Pull Required Models
```powershell
ollama pull llama3.2
ollama pull nomic-embed-text

# Verify models
ollama list
```

### Step 4: Place Your PDF
Put your CSE Annual Report PDF in one of these locations:
- `backend/data/uploads/Annual-Report-2024.pdf` ✅ (Recommended)
- `backend/data/uploads/CSE_Annual_Report_2024.pdf`
- `backend/lstm_stock_prediction/data/raw/Annual-Report-2024.pdf`

### Step 5: Validate System
```powershell
cd backend
python validate_knowledge_base.py
```

This checks:
- ✅ Ollama connection
- ✅ ChromaDB installation
- ✅ Service initialization
- ✅ Embedding generation
- ✅ Query functionality

### Step 6: Build Knowledge Base
```powershell
cd backend
python setup_knowledge_base.py
```

This will:
1. Locate your PDF file
2. Extract text from all pages
3. Create text chunks (~800 chars each)
4. Generate embeddings for each chunk
5. Store in ChromaDB vector database

**Time**: 5-15 minutes depending on PDF size

### Step 7: Start API Server
```powershell
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 8: Test the System

#### Option A: Interactive CLI Test
```powershell
cd backend
python test_knowledge_base.py
```

#### Option B: API Test (Browser)
Open: http://localhost:8000/docs

Try the `/api/knowledge/query` endpoint with:
```json
{
  "question": "What was the total trading volume in 2024?",
  "n_results": 5,
  "include_sources": true
}
```

#### Option C: API Test (PowerShell)
```powershell
$body = @{
    question = "What are the key financial highlights?"
    n_results = 5
    include_sources = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/knowledge/query" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

## Common Issues & Fixes

### Issue 1: Ollama Not Running
**Symptoms**: "Cannot connect to Ollama" error

**Fix**:
```powershell
# Start Ollama in a separate terminal
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

### Issue 2: Models Not Found
**Symptoms**: "Model 'llama3.2' not found"

**Fix**:
```powershell
ollama pull llama3.2
ollama pull nomic-embed-text
ollama list
```

### Issue 3: PDF Not Found
**Symptoms**: "PDF file not found"

**Fix**:
1. Check PDF location: `backend/data/uploads/`
2. Ensure filename matches expected patterns
3. Or provide full path when prompted

### Issue 4: ChromaDB Errors
**Symptoms**: "Cannot initialize ChromaDB"

**Fix**:
```powershell
# Reinstall ChromaDB
pip uninstall chromadb -y
pip install chromadb>=0.4.22

# Clear existing data (if corrupted)
Remove-Item -Recurse -Force backend/data/knowledge_base/*
```

### Issue 5: Out of Memory
**Symptoms**: System slows down or crashes during build

**Fix**:
1. Close other applications
2. Reduce chunk size in `setup_knowledge_base.py`:
   - Edit the script
   - Change `chunk_size=800` to `chunk_size=500`
3. Process in smaller batches

### Issue 6: Import Errors
**Symptoms**: "Module not found" errors

**Fix**:
```powershell
# Ensure you're in the backend directory
cd backend

# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements-knowledge.txt
```

## Maintenance Commands

### View Knowledge Base Stats
```python
from app.services.knowledge_base_service import KnowledgeBaseService
kb = KnowledgeBaseService()
print(kb.get_stats())
```

### Rebuild Knowledge Base
```powershell
# This will delete existing data and rebuild
python setup_knowledge_base.py
```

### Reset Knowledge Base (via API)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/knowledge/reset" -Method Delete
```

## Performance Tips

### 1. Optimize Chunk Size
- Smaller chunks (500-700 chars): Better precision, more chunks
- Larger chunks (800-1200 chars): Better context, fewer chunks

### 2. Adjust Number of Results
- More results (n_results=8-10): Better context, slower
- Fewer results (n_results=3-5): Faster, less context

### 3. Use Faster Models
```python
# In setup_knowledge_base.py or when initializing service
MODEL_NAME = "phi"  # Lightweight and fast
EMBEDDING_MODEL = "nomic-embed-text"  # Already optimized
```

## API Integration Examples

### Python
```python
import requests

response = requests.post('http://localhost:8000/api/knowledge/query', json={
    "question": "What was CSE's revenue?",
    "n_results": 5
})
result = response.json()
print(result['answer'])
```

### JavaScript/TypeScript
```javascript
const response = await fetch('http://localhost:8000/api/knowledge/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: "What was CSE's revenue?",
    n_results: 5
  })
});
const result = await response.json();
console.log(result.answer);
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/knowledge/query" \
  -H "Content-Type: application/json" \
  -d '{"question":"What was CSE'\''s revenue?","n_results":5}'
```

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend/Client                     │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────▼──────────────────────────────────┐
│                   FastAPI Server                        │
│                  (app/main.py)                          │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Knowledge Routes Layer                     │
│          (app/routes/knowledge_routes.py)               │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│           Knowledge Base Service                        │
│      (app/services/knowledge_base_service.py)           │
│                                                          │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │  PDF Parser    │  │   Chunking   │  │  Embeddings│  │
│  │   (PyPDF2)     │──│   Logic      │──│  (Ollama)  │  │
│  └────────────────┘  └──────────────┘  └──────┬─────┘  │
│                                                │         │
└────────────────────────────────────────────────┼─────────┘
                                                 │
                       ┌─────────────────────────┼─────────┐
                       │                         │         │
           ┌───────────▼──────────┐  ┌──────────▼───────┐ │
           │   ChromaDB           │  │   Ollama LLM     │ │
           │ (Vector Storage)     │  │ (Generation)     │ │
           └──────────────────────┘  └──────────────────┘ │
                                                           │
                    External Dependencies                  │
           └────────────────────────────────────────────────┘
```

## Files Changed/Created

### Modified Files
1. `backend/app/services/knowledge_base_service.py`
   - Added Ollama connection validation
   - Enhanced error handling with retry logic
   - Better directory management
   - Improved embedding generation

2. `backend/setup_knowledge_base.py`
   - Smart PDF file detection
   - Better Ollama validation
   - User-friendly prompts

### New Files Created
1. `backend/init_knowledge_base_directories.py` - Directory initialization
2. `backend/validate_knowledge_base.py` - Comprehensive validation script
3. `KNOWLEDGE_BASE_FIX_GUIDE.md` - This guide

## Success Checklist

Before considering the system "fully working", verify:

- [ ] All directories created (`data/knowledge_base/`, `data/uploads/`)
- [ ] Dependencies installed (chromadb, ollama, PyPDF2)
- [ ] Ollama running (`ollama serve`)
- [ ] Models downloaded (llama3.2, nomic-embed-text)
- [ ] PDF file in correct location
- [ ] Validation script passes all checks
- [ ] Knowledge base built successfully
- [ ] API server starts without errors
- [ ] Query endpoint returns valid responses
- [ ] Interactive test works correctly
- [ ] Stats endpoint shows active status

## Getting Help

If you encounter issues:

1. **Run validation**: `python validate_knowledge_base.py`
2. **Check logs**: Look for error messages in console output
3. **Verify Ollama**: `ollama list` should show both models
4. **Test connection**: `curl http://localhost:11434/api/tags`
5. **Check directories**: Ensure all paths exist
6. **Review this guide**: Follow troubleshooting section

## Next Steps

Once the knowledge base is working:

1. **Integrate with frontend**: Update frontend to call `/api/knowledge/query`
2. **Add more documents**: Process additional PDFs
3. **Customize prompts**: Modify system prompts for better answers
4. **Optimize performance**: Adjust chunk sizes and model parameters
5. **Add authentication**: Secure endpoints if needed
6. **Monitor usage**: Track queries and performance metrics

---

**Version**: 1.0  
**Last Updated**: February 28, 2026  
**Status**: Production Ready ✅
