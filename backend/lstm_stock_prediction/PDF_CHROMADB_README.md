# PDF Document Storage in ChromaDB

Store and query PDF documents with automatic semantic embeddings using ChromaDB.

## 🎯 What This Does

- **Extracts text** from PDF files
- **Splits into chunks** with smart overlapping for context preservation
- **Generates embeddings** automatically for semantic search
- **Stores in ChromaDB** for fast retrieval
- **Enables semantic search** - ask questions in natural language!

## 📁 Files Created

1. **`pdf_to_chromadb.py`** - Core library with `PDFDocumentStore` class
2. **`store_annual_report.py`** - Interactive script to store and query your Annual Report

## 🚀 Quick Start

### Option 1: Run the Interactive Script

```bash
cd backend\lstm_stock_prediction
python store_annual_report.py
```

This will:
1. ✅ Store your Annual-Report-2024.pdf in ChromaDB
2. ✅ Generate embeddings for all content
3. ✅ Run sample queries to test
4. ✅ Enter interactive mode for custom questions

### Option 2: Use in Python Script

```python
from pdf_to_chromadb import PDFDocumentStore

# Initialize
store = PDFDocumentStore(use_local=True)

# Store PDF
pdf_path = r"C:\Users\USER\OneDrive\Documents\GitHub\Research-Project\backend\lstm_stock_prediction\data\uploads\Annual-Report-2024.pdf"
summary = store.store_pdf(pdf_path)

# Search
results = store.query_documents("What is the revenue growth?", n_results=5)
store.display_results(results)
```

### Option 3: Use in Jupyter Notebook

```python
# Cell 1: Import
from pdf_to_chromadb import PDFDocumentStore
store = PDFDocumentStore(use_local=True)

# Cell 2: Store PDF
pdf_path = r"YOUR_PDF_PATH_HERE"
summary = store.store_pdf(pdf_path, chunk_size=1000, overlap=200)

# Cell 3: Query
results = store.query_documents("financial performance", n_results=5)
store.display_results(results, show_full_text=True)
```

## 🔍 How It Works

### 1. Text Extraction
- Reads PDF using PyPDF2
- Extracts text from all pages
- Maintains page information

### 2. Chunking Strategy
- **Chunk Size**: 1000 characters (configurable)
- **Overlap**: 200 characters (for context continuity)
- **Smart Breaking**: Breaks at sentence boundaries when possible
- **Why Chunking?**: Better embeddings, more precise search results

### 3. Embedding Generation
- ChromaDB **automatically generates embeddings** for each chunk
- Uses default embedding model (can be customized)
- Embeddings enable semantic search (meaning-based, not just keywords)

### 4. Storage
- Each chunk stored with metadata:
  - Source document name
  - Chunk ID and position
  - Timestamp
  - Custom metadata (document type, year, etc.)

### 5. Querying
- Uses semantic similarity search
- Finds most relevant chunks based on meaning
- Returns results with relevance scores

## 📊 Example Queries

Once stored, you can ask natural language questions:

```python
# Financial information
results = store.query_documents("What was the revenue in 2024?")

# Strategic information
results = store.query_documents("What are the company's future plans?")

# Risk analysis
results = store.query_documents("What challenges does the company face?")

# Operational details
results = store.query_documents("How many employees does the company have?")

# Market analysis
results = store.query_documents("Who are the main competitors?")
```

## ⚙️ Configuration Options

### Chunk Size
```python
store.store_pdf(pdf_path, chunk_size=1000)  # Default: 1000 characters
```
- **Smaller chunks** (500-800): More precise, more chunks
- **Larger chunks** (1500-2000): More context, fewer chunks

### Overlap
```python
store.store_pdf(pdf_path, overlap=200)  # Default: 200 characters
```
- Ensures context continuity between chunks
- Prevents losing information at boundaries

### Custom Metadata
```python
metadata = {
    "document_type": "annual_report",
    "year": "2024",
    "category": "financial",
    "department": "finance"
}
store.store_pdf(pdf_path, metadata=metadata)
```

## 🔧 Advanced Usage

### Filter by Metadata
```python
results = store.query_documents(
    "revenue",
    n_results=5,
    filter_metadata={"year": "2024"}
)
```

### List All Documents
```python
docs = store.list_stored_documents()
```

### Delete Document
```python
store.delete_document("Annual-Report-2024.pdf")
```

### Use ChromaDB Server (Instead of Local)
```python
# Start ChromaDB server first: docker run -p 8000:8000 chromadb/chroma
store = PDFDocumentStore(use_local=False, host="localhost", port=8000)
```

## 📝 Your Annual Report Setup

The script is pre-configured with your file:
```python
pdf_path = r"C:\Users\USER\OneDrive\Documents\GitHub\Research-Project\backend\lstm_stock_prediction\data\uploads\Annual-Report-2024.pdf"
```

## 💡 Benefits

1. **Semantic Search**: Find information by meaning, not just keywords
2. **Fast Retrieval**: ChromaDB optimized for vector similarity
3. **Automatic Embeddings**: No manual embedding generation needed
4. **Context Preservation**: Overlapping chunks maintain context
5. **Scalable**: Can store multiple documents
6. **Flexible Queries**: Ask natural language questions

## 🎯 Use Cases

- **Financial Analysis**: Query annual reports for specific metrics
- **Research**: Extract information from research papers
- **Documentation**: Search technical documentation
- **Legal**: Find relevant sections in contracts
- **Due Diligence**: Analyze company documents

## 🔗 Integration with LSTM Models

You can combine this with your LSTM stock predictions:

```python
# Query annual report for company info
report_results = store.query_documents("financial performance of XYZ company")

# Use insights with LSTM predictions
from chromadb_integration import LSTMPredictionStore
lstm_store = LSTMPredictionStore()
predictions = lstm_store.query_by_company("XYZ")

# Combine insights for comprehensive analysis
```

## 📦 Requirements

Already in your `requirements.txt`:
- ✅ `chromadb>=0.4.22`
- ✅ `PyPDF2>=3.0.1`

## 🚦 Next Steps

1. **Run the script**: `python store_annual_report.py`
2. **Test queries**: Try different questions about your report
3. **Store more PDFs**: Add other documents (reports, papers, etc.)
4. **Integrate with your app**: Use in your FastAPI backend for document Q&A

## 📚 Additional Features to Add

Want to enhance this? You can add:
- Support for more file types (Word, Excel, HTML)
- Better text cleaning and preprocessing
- Custom embedding models
- Summarization of query results
- Export results to various formats
- API endpoints for web access

## 🤝 Support

If you need help or have questions:
1. Check the example queries in `store_annual_report.py`
2. Review the `PDFDocumentStore` class methods
3. Test with smaller PDFs first
4. Adjust chunk_size and overlap for your needs

---

**Ready to try?** Run `python store_annual_report.py` and start querying your Annual Report! 🚀
