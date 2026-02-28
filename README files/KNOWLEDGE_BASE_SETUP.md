# CSE Annual Report Knowledge Base - Setup Guide

## Overview
This knowledge base system allows you to query the CSE (Colombo Stock Exchange) Annual Report 2024 using natural language. It uses:
- **Ollama** for local LLM (no API keys needed!)
- **ChromaDB** for vector storage
- **nomic-embed-text** for embeddings

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd backend
pip install chromadb ollama PyPDF2
```

### Step 2: Install and Start Ollama

1. Download Ollama from: https://ollama.ai
2. Install and start the Ollama service
3. Pull required models:

```bash
ollama pull llama2
ollama pull nomic-embed-text
```

**Alternative Models** (if you want):
```bash
ollama pull mistral      # Faster, good quality
ollama pull mixtral      # Best quality, slower
ollama pull phi          # Lightweight
```

### Step 3: Place Your PDF

Put your CSE Annual Report 2024 PDF at:
```
backend/data/uploads/CSE_Annual_Report_2024.pdf
```

Or upload it via the API endpoint later.

### Step 4: Build Knowledge Base

Run the setup script:
```bash
cd backend
python setup_knowledge_base.py
```

This will:
- Extract text from the PDF
- Create text chunks
- Generate embeddings
- Store in ChromaDB vector database

**Time:** Takes 5-15 minutes depending on PDF size and your computer.

### Step 5: Start the API Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 6: Test It!

Open your browser: http://localhost:8000/docs

Try the `/api/knowledge/query` endpoint with questions like:
- "What was the total trading volume in 2024?"
- "What are the key financial highlights?"
- "What risks are mentioned in the annual report?"

## 📡 API Endpoints

### Query Knowledge Base
```http
POST /api/knowledge/query
Content-Type: application/json

{
  "question": "What was CSE's revenue in 2024?",
  "n_results": 5,
  "include_sources": true
}
```

**Response:**
```json
{
  "answer": "According to the CSE Annual Report 2024...",
  "confidence": 0.87,
  "sources": [...],
  "metadata": {...}
}
```

### Upload PDF and Build
```http
POST /api/knowledge/upload-pdf
Content-Type: multipart/form-data

file: <your-pdf-file>
```

### Get Statistics
```http
GET /api/knowledge/stats
```

### Health Check
```http
GET /api/knowledge/health
```

## 🔧 Configuration

Edit `backend/app/services/knowledge_base_service.py`:

```python
# Change models
model_name = "mistral"           # LLM model
embedding_model = "nomic-embed-text"  # Embedding model

# Change chunk size
chunk_size = 800      # Characters per chunk
overlap = 150         # Overlap between chunks
```

## 🎨 Frontend Integration

### React Example

```javascript
// src/services/knowledgeService.js
const API_URL = 'http://localhost:8000';

export const queryKnowledgeBase = async (question) => {
  const response = await fetch(`${API_URL}/api/knowledge/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question: question,
      n_results: 5,
      include_sources: true
    })
  });
  
  return await response.json();
};

// Usage in component
import { queryKnowledgeBase } from './services/knowledgeService';

function KnowledgeChat() {
  const [answer, setAnswer] = useState('');
  
  const askQuestion = async (question) => {
    const result = await queryKnowledgeBase(question);
    setAnswer(result.answer);
  };
  
  return (
    <div>
      <input 
        onSubmit={(e) => askQuestion(e.target.value)} 
        placeholder="Ask about CSE Annual Report..."
      />
      <div>{answer}</div>
    </div>
  );
}
```

### Simple Fetch Example

```javascript
fetch('http://localhost:8000/api/knowledge/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: "What are the main risks in CSE 2024?"
  })
})
.then(res => res.json())
.then(data => console.log(data.answer));
```

## 📊 How It Works

1. **Document Processing**
   - PDF → Text extraction
   - Text → Chunks (800 chars with 150 char overlap)
   - Each chunk gets metadata (page, position, etc.)

2. **Embedding Generation**
   - Each chunk → Ollama embedding (nomic-embed-text)
   - Embeddings stored in ChromaDB vector database

3. **Query Process**
   - User question → Ollama embedding
   - Find similar chunks (vector similarity search)
   - Top 5 chunks → Context for LLM
   - LLM generates answer based on context

4. **Response**
   - Answer from LLM
   - Confidence score
   - Source chunks (for transparency)

## 🔍 Example Questions

**Financial:**
- "What was the total revenue in 2024?"
- "How did CSE perform compared to previous year?"
- "What are the profit margins?"

**Strategic:**
- "What are CSE's strategic priorities for 2024?"
- "What new initiatives were launched?"
- "What are the future plans?"

**Risk & Governance:**
- "What risks are identified in the report?"
- "What corporate governance measures are in place?"
- "What regulatory changes affected CSE?"

**Market Data:**
- "What was the trading volume?"
- "How many companies are listed?"
- "What sectors performed best?"

## 🛠️ Troubleshooting

### Ollama Connection Error
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start Ollama
ollama serve
```

### Model Not Found
```bash
# Pull the model
ollama pull llama2
ollama pull nomic-embed-text
```

### PDF Not Found
- Check path: `backend/data/uploads/CSE_Annual_Report_2024.pdf`
- Or use the upload endpoint

### Slow Performance
- Use smaller model: `phi` instead of `llama2`
- Reduce chunk retrieval: `n_results: 3`
- Increase chunk size to reduce total chunks

### Low Quality Answers
- Use better model: `mixtral` instead of `llama2`
- Increase chunks retrieved: `n_results: 7`
- Reduce chunk size for more precise context

## 📈 Performance Tips

1. **First Time Setup**: Takes 5-15 minutes
2. **Subsequent Queries**: 2-5 seconds per query
3. **Memory Usage**: ~2-4GB for models + embeddings
4. **Disk Space**: ~500MB for models, ~50MB for vector DB

## 🔐 Security Notes

- All data stored locally
- No external API calls
- No data sent to cloud services
- PDF content never leaves your server

## 🆚 Comparison with News Scraping

| Feature | Knowledge Base | News Scraping |
|---------|---------------|---------------|
| Data Source | Static PDF (Annual Report) | Dynamic RSS feeds |
| Update Frequency | Manual/Scheduled | Real-time |
| Accuracy | Very High (official docs) | Variable |
| Context | Deep, structured | Brief, fragmented |
| Use Case | Company info, financials | Market news, sentiment |

**Best Practice:** Use both!
- Knowledge Base → Company fundamentals, financials
- News Scraping → Market trends, real-time news

## 📚 Additional Resources

- Ollama: https://ollama.ai
- ChromaDB: https://www.trychroma.com/
- FastAPI: https://fastapi.tiangolo.com/

## 🎯 Next Steps

1. ✅ Set up knowledge base
2. Add more documents (quarterly reports, prospectuses)
3. Create combined endpoint (news + knowledge base)
4. Build frontend chat interface
5. Add query history and analytics
6. Implement caching for common questions

## 💡 Advanced Features (Optional)

### Multi-Document Support
- Add multiple PDFs (different years, different companies)
- Query across all documents
- Filter by document type or date

### Query History
- Store queries in MongoDB
- Track popular questions
- Improve answers based on feedback

### Hybrid Search
- Combine with news data
- Cross-reference with stock predictions
- Provide comprehensive insights

Need help? Check the API docs at: http://localhost:8000/docs
