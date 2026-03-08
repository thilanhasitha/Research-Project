# How to Test Knowledge Base System - Step by Step Guide

## Prerequisites Check

### 1. Check Ollama Status
```powershell
# Check if Ollama is running
Get-Process ollama -ErrorAction SilentlyContinue

# If not running, start it (in a separate terminal)
ollama serve

# Check if models are installed
ollama list
```

### 2. Install Required Dependencies
```powershell
cd backend
pip install chromadb ollama PyPDF2
```

### 3. Pull Required Models
```powershell
ollama pull llama2
ollama pull nomic-embed-text
```

## Setup Steps

### 1. Create Required Directories
```powershell
# From backend folder
New-Item -ItemType Directory -Force -Path "data/uploads"
New-Item -ItemType Directory -Force -Path "data/knowledge_base"
```

### 2. Place Your PDF
Copy your `CSE_Annual_Report_2024.pdf` to `backend/data/uploads/`

### 3. Build Knowledge Base
```powershell
python setup_knowledge_base.py
```

## Testing Methods

### Method 1: Comprehensive System Test (Recommended)
```powershell
python test_full_system.py
```

This tests:
- ✅ Dependencies installed
- ✅ Ollama service running
- ✅ Required models available
- ✅ ChromaDB connection
- ✅ PDF file exists
- ✅ Knowledge base built
- ✅ Query functionality
- ✅ API endpoints (if server running)

### Method 2: Interactive Test
```powershell
python test_knowledge_base.py
```

This allows you to:
- Ask questions interactively
- Test query responses
- Check confidence scores

### Method 3: API Endpoint Test

Start the server:
```powershell
uvicorn app.main:app --reload
```

Then test endpoints:

**Health Check:**
```powershell
curl http://localhost:8000/api/knowledge/health
```

**Get Stats:**
```powershell
curl http://localhost:8000/api/knowledge/stats
```

**Query:**
```powershell
curl -X POST http://localhost:8000/api/knowledge/query `
  -H "Content-Type: application/json" `
  -d '{"question": "What is in the report?", "n_results": 5}'
```

### Method 4: Python Script Test
```python
# test_quick.py
import requests

# Test health
health = requests.get('http://localhost:8000/api/knowledge/health')
print("Health:", health.json())

# Test query
query = requests.post(
    'http://localhost:8000/api/knowledge/query',
    json={"question": "What was the revenue?", "n_results": 5}
)
result = query.json()
print("Answer:", result['answer'])
print("Confidence:", result['confidence'])
```

### Method 5: Browser Test
Visit: http://localhost:8000/docs

- Click on `/api/knowledge/query`
- Click "Try it out"
- Enter your question
- Click "Execute"

## Expected Results

### ✅ Successful Test Shows:
```
✅ All dependencies installed
✅ Ollama service running on port 11434
✅ Models: llama2, nomic-embed-text available
✅ ChromaDB connection established
✅ Knowledge base collection with N chunks
✅ PDF file found
✅ Query returns answers with confidence > 0.7
✅ API endpoints responding (if server running)
```

### ❌ Common Issues:

**1. "Ollama connection failed"**
```powershell
# Solution: Start Ollama
ollama serve
```

**2. "Collection not found"**
```powershell
# Solution: Build knowledge base
python setup_knowledge_base.py
```

**3. "PDF extraction failed"**
```powershell
# Solution: Check PDF exists
Test-Path "data/uploads/CSE_Annual_Report_2024.pdf"
```

**4. "Module not found: chromadb"**
```powershell
# Solution: Install dependencies
pip install chromadb ollama PyPDF2
```

**5. "API endpoints not responding"**
```powershell
# Solution: Start server
uvicorn app.main:app --reload
```

## Complete Test Workflow

```powershell
# 1. Check Prerequisites
Get-Process ollama  # Should be running
pip list | Select-String "chromadb|ollama|PyPDF2"  # Should show all three

# 2. Run comprehensive test
python test_full_system.py

# 3. If all tests pass, test interactively
python test_knowledge_base.py

# 4. Start server and test API
Start-Process powershell -ArgumentList "-Command", "uvicorn app.main:app --reload"
Start-Sleep 5
Invoke-WebRequest http://localhost:8000/api/knowledge/health

# 5. Test from browser
Start-Process "http://localhost:8000/docs"
```

## Verification Checklist

- [ ] Ollama service is running
- [ ] Models (llama2, nomic-embed-text) are installed
- [ ] All Python dependencies installed
- [ ] PDF file in correct location
- [ ] Knowledge base built successfully
- [ ] test_full_system.py passes all tests
- [ ] Interactive test returns relevant answers
- [ ] API health endpoint responds
- [ ] API query endpoint returns answers
- [ ] Confidence scores > 0.5

## Performance Benchmarks

**Expected Response Times:**
- Health check: < 100ms
- Stats query: < 200ms
- Simple query: 2-5 seconds
- Complex query: 5-10 seconds

**Memory Usage:**
- Ollama: ~2-4 GB
- Python backend: ~500 MB - 1 GB
- ChromaDB: ~100-500 MB

## Next Steps After Testing

If all tests pass:
1. ✅ Integrate with frontend
2. ✅ Add more documents
3. ✅ Create custom query templates
4. ✅ Implement caching for common queries
5. ✅ Add analytics and tracking

## Troubleshooting Commands

```powershell
# Check Ollama status
Get-Process ollama
netstat -ano | Select-String "11434"

# Check FastAPI server
netstat -ano | Select-String "8000"

# View ChromaDB collections
python -c "import chromadb; print([c.name for c in chromadb.Client().list_collections()])"

# Check PDF
Get-ChildItem backend/data/uploads/*.pdf

# Test Ollama directly
ollama run llama2 "Hello"
```
