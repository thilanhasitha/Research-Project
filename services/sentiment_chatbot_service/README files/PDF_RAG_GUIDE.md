# PDF RAG System with Ollama

Complete Retrieval-Augmented Generation system for querying your Annual Report using AI.

## 🎯 What This Does

The RAG system combines:
1. **Retrieval**: Searches your PDF index for relevant content
2. **Augmentation**: Provides context to the AI
3. **Generation**: Uses Ollama to generate accurate, context-aware answers

Instead of just keyword search, you get **intelligent answers** based on the actual content of your Annual Report.

## 🏗️ Architecture

```
User Question
     ↓
[PDF Index Search] → Find relevant chunks (keyword matching)
     ↓
[Context Creation] → Combine top chunks
     ↓
[Ollama LLM] → Generate answer based on context
     ↓
AI-Generated Answer
```

## 📋 Prerequisites

1. **PDF Index** - Run `simple_pdf_indexer.py` first to create the index
2. **Ollama** - Must be running locally
3. **LLM Model** - Have a model installed (e.g., llama3.2:latest)

### Check if Ollama is Running

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve

# Pull a model if needed
ollama pull llama3.2:latest
```

## 🚀 Quick Start

### 1. Interactive Mode (Recommended)

```bash
cd backend/lstm_stock_prediction
python pdf_rag_ollama.py
```

This will:
- Load your PDF index
- Check Ollama connection
- Run example queries
- Enter interactive Q&A mode

### 2. Programmatic Usage

```python
from pdf_rag_ollama import PDFRagSystem

# Initialize
rag = PDFRagSystem()

# Ask a question
result = rag.ask(
    "What was the total revenue in 2024?",
    n_results=5,      # Number of chunks to retrieve
    stream=True,      # Stream response in real-time
    show_context=False # Show retrieved chunks
)

# Display formatted response
rag.display_response(result)
```

### 3. Use the Example Script

```bash
python rag_usage_example.py
```

## 💡 Example Questions

### Financial Questions
```
- What was the total revenue in 2024?
- What were the main revenue sources?
- How did profitability change compared to last year?
- What are the key financial metrics?
```

### Strategic Questions
```
- What are the company's strategic objectives?
- What are the future growth plans?
- What markets is the company targeting?
- What are the key initiatives?
```

### Operational Questions
```
- How many employees does the company have?
- What is the organizational structure?
- What technology platforms are used?
- What are the main products and services?
```

### Risk & Challenges
```
- What are the main risk factors?
- What challenges does the company face?
- How does the company manage cybersecurity?
- What regulatory changes affect the business?
```

## ⚙️ Configuration Options

### Number of Chunks to Retrieve
```python
result = rag.ask(query, n_results=5)  # Retrieve top 5 chunks
```
- **More chunks (5-10)**: Better context, longer processing
- **Fewer chunks (2-3)**: Faster, more focused

### Show Retrieved Context
```python
result = rag.ask(query, show_context=True)
```
Shows which chunks were retrieved before generating the answer.

### Streaming vs Non-Streaming
```python
# Streaming (default) - shows tokens as generated
result = rag.ask(query, stream=True)

# Non-streaming - waits for complete response
result = rag.ask(query, stream=False)
```

### Different Models
```python
# Use different Ollama model
result = rag.ask(query, model="mistral:latest")
result = rag.ask(query, model="llama3.2:latest")
result = rag.ask(query, model="gemma:7b")
```

## 📊 Response Structure

```python
{
    "status": "success",
    "query": "What was the revenue?",
    "response": "According to the Annual Report...",
    "chunks_found": 5,
    "chunks_used": 5,
    "model": "llama3.2:latest",
    "duration": 2.34,
    "context": "..." # Only if show_context=True
}
```

## 🔧 Advanced Usage

### Custom Ollama URL
```python
rag = PDFRagSystem(
    index_file="pdf_index_data/pdf_index.json",
    ollama_url="http://192.168.1.100:11434"  # Remote Ollama
)
```

### Multiple Questions in Batch
```python
questions = [
    "What was the revenue?",
    "How many employees?",
    "What are the strategic goals?"
]

for question in questions:
    result = rag.ask(question, stream=False)
    print(f"Q: {question}")
    print(f"A: {result['response']}\n")
```

### Integrate into FastAPI
```python
from fastapi import FastAPI
from pdf_rag_ollama import PDFRagSystem

app = FastAPI()
rag = PDFRagSystem()

@app.post("/ask")
async def ask_question(query: str):
    result = rag.ask(query, stream=False)
    return result
```

## 🎛️ How It Works

### 1. Retrieval Phase
```python
def search_chunks(self, query: str, n_results: int = 5):
    # Tokenize query
    # Search for keyword matches in chunks
    # Score chunks by relevance
    # Return top N chunks
```

Uses keyword-based search with:
- Term frequency matching
- Exact phrase boost
- Relevance scoring

### 2. Context Creation
```python
def create_context(self, search_results, max_chars=4000):
    # Combine relevant chunks
    # Limit to 4000 characters (fits in LLM context)
    # Format for LLM consumption
```

### 3. Response Generation
```python
def generate_response(self, query, context, model):
    # Create prompt with context
    # Call Ollama API
    # Stream or return complete response
```

Prompt template:
```
You are an AI assistant helping users understand the Annual Report.
Use the provided context to answer the question accurately.

Context from Annual Report:
[Retrieved chunks]

Question: [User question]

Answer based on the context...
```

## 🐛 Troubleshooting

### "Ollama not reachable"
```bash
# Start Ollama
ollama serve

# Check it's running
curl http://localhost:11434/api/tags
```

### "No index found"
```bash
# Create the index first
python simple_pdf_indexer.py
```

### "Request timed out"
- Increase timeout in code (default: 120s)
- Use a smaller/faster model
- Reduce n_results to provide less context

### "No relevant chunks found"
- Try different keywords
- Check if PDF was indexed correctly
- Verify index file exists

## 📈 Performance Tips

1. **Faster Responses**: Use smaller models (1B-3B parameters)
2. **Better Accuracy**: Use larger models (7B+ parameters)
3. **Reduce Latency**: Decrease n_results to 2-3 chunks
4. **Better Context**: Increase n_results to 7-10 chunks

## 🔄 Comparison: Before vs After

### Before (Simple Search Only)
```
Query: "What was the revenue?"
Result: Shows raw text chunks containing "revenue"
→ User has to read and interpret
```

### After (RAG with Ollama)
```
Query: "What was the revenue?"
Result: "According to the Annual Report, the company generated 
total revenue of $XX million in 2024, representing a YY% 
increase from the previous year..."
→ Clear, direct answer with context
```

## 🎯 Use Cases

1. **Quick Information Retrieval**: "How many employees?"
2. **Analysis**: "What were the main challenges in 2024?"
3. **Comparison**: "How did revenue compare to last year?"
4. **Summarization**: "Summarize the strategic objectives"
5. **Insights**: "What are the growth opportunities?"

## 🔐 Privacy Note

- All processing happens **locally**
- No data sent to external APIs
- Ollama runs on your machine
- PDF content stays on your system

## 📦 Files

- `pdf_rag_ollama.py` - Main RAG system
- `rag_usage_example.py` - Usage examples
- `simple_pdf_indexer.py` - Creates the PDF index
- `pdf_index_data/pdf_index.json` - The searchable index

## 🚀 Next Steps

1. **Run it**: `python pdf_rag_ollama.py`
2. **Try different models**: Install and test various Ollama models
3. **Integrate**: Add to your application via API
4. **Extend**: Add more PDFs to the index
5. **Customize**: Adjust prompts for your specific needs

---

**Ready to ask questions about your Annual Report?** 🎉

Run: `python pdf_rag_ollama.py`
