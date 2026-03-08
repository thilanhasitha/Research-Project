"""
PDF Document Storage in ChromaDB
Extract text from PDFs and store with embeddings for semantic search
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from datetime import datetime
import os
from typing import List, Dict, Optional
from PyPDF2 import PdfReader
import re


class PDFDocumentStore:
    """
    Store and retrieve PDF documents using ChromaDB with automatic embeddings
    """
    
    def __init__(self, host: str = "localhost", port: int = 8000, use_local: bool = False):
        """
        Initialize ChromaDB connection
        
        Args:
            host: ChromaDB server host (use 'chromadb' if inside Docker)
            port: ChromaDB server port
            use_local: Use local client instead of server
        """
        self.use_local = use_local
        
        if use_local:
            self.client = chromadb.Client()
            print("✓ Using local ChromaDB client")
        else:
            try:
                # Use environment variables if available
                host = os.getenv('CHROMADB_HOST', host)
                port = int(os.getenv('CHROMADB_PORT', port))
                
                self.client = chromadb.HttpClient(host=host, port=port)
                self.client.heartbeat()
                print(f"✓ Connected to ChromaDB at {host}:{port}")
            except Exception as e:
                print(f"⚠ Could not connect to ChromaDB server: {e}")
                print("  Falling back to local client")
                self.client = chromadb.Client()
                self.use_local = True
        
        # Try to use sentence-transformers first, fall back to default if not available
        try:
            print("🔄 Initializing embedding function (sentence-transformers)...")
            embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            print("✓ Using sentence-transformers for embeddings")
        except Exception as e:
            print(f"⚠ Sentence-transformers not available: {e}")
            print("  Using default embedding function")
            embedding_func = None  # Use ChromaDB default
        
        # Create or get collection for documents
        if embedding_func:
            self.collection = self.client.get_or_create_collection(
                name="pdf_documents",
                metadata={"description": "PDF document storage with embeddings"},
                embedding_function=embedding_func
            )
        else:
            self.collection = self.client.get_or_create_collection(
                name="pdf_documents",
                metadata={"description": "PDF document storage with embeddings"}
            )
        
        print(f"✓ Collection ready with {self.collection.count()} document chunks")
    
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            print(f" Reading PDF: {os.path.basename(pdf_path)}")
            print(f"   Pages: {len(reader.pages)}")
            
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                text += f"\n--- Page {page_num} ---\n{page_text}\n"
                
                if page_num % 10 == 0:
                    print(f"   Processed {page_num} pages...")
            
            print(f" Extracted {len(text)} characters from {len(reader.pages)} pages")
            return text
            
        except Exception as e:
            print(f" Error reading PDF: {e}")
            raise
    
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """
        Split text into overlapping chunks for better context preservation
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Characters to overlap between chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Clean text
        text = re.sub(r'\n+', '\n', text)  # Remove excessive newlines
        text = re.sub(r' +', ' ', text)     # Remove excessive spaces
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            # Get chunk
            end = start + chunk_size
            chunk_text = text[start:end]
            
            # Try to break at sentence boundary if possible
            if end < len(text):
                last_period = chunk_text.rfind('.')
                last_newline = chunk_text.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.7:  # Only break if not too far back
                    end = start + break_point + 1
                    chunk_text = text[start:end]
            
            chunks.append({
                'text': chunk_text.strip(),
                'chunk_id': chunk_id,
                'start_pos': start,
                'end_pos': end,
                'length': len(chunk_text)
            })
            
            chunk_id += 1
            start = end - overlap  # Move forward with overlap
        
        print(f"✓ Created {len(chunks)} chunks (avg {sum(c['length'] for c in chunks)//len(chunks)} chars each)")
        return chunks
    
    
    def store_pdf(self, pdf_path: str, chunk_size: int = 1000, overlap: int = 200, 
                  metadata: Optional[Dict] = None) -> Dict:
        """
        Store PDF document in ChromaDB with embeddings
        
        Args:
            pdf_path: Path to PDF file
            chunk_size: Maximum characters per chunk
            overlap: Characters overlap between chunks
            metadata: Optional additional metadata
            
        Returns:
            Dictionary with storage summary
        """
       
        print("PDF TO CHROMADB STORAGE")
       
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        
        # Chunk text
        chunks = self.chunk_text(text, chunk_size, overlap)
        
        # Prepare for ChromaDB
        doc_name = os.path.basename(pdf_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        documents = []
        metadatas = []
        ids = []
        
        print(f"\n Preparing {len(chunks)} chunks for storage...")
        
        for chunk in chunks:
            # Create unique ID
            doc_id = f"{doc_name}_{timestamp}_chunk_{chunk['chunk_id']}"
            
            # Prepare metadata
            chunk_metadata = {
                "source": doc_name,
                "timestamp": timestamp,
                "chunk_id": chunk['chunk_id'],
                "total_chunks": len(chunks),
                "chunk_size": chunk['length'],
                "file_path": pdf_path,
                "type": "pdf_document"
            }
            
            # Add custom metadata if provided
            if metadata:
                chunk_metadata.update(metadata)
            
            documents.append(chunk['text'])
            metadatas.append(chunk_metadata)
            ids.append(doc_id)
        
        # Store in ChromaDB (embeddings are generated automatically)
        print(f" Storing in ChromaDB (generating embeddings)...")
        
        batch_size = 100
        stored_count = 0
        
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_meta = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            self.collection.add(
                documents=batch_docs,
                metadatas=batch_meta,
                ids=batch_ids
            )
            
            stored_count += len(batch_docs)
            print(f"   Stored {stored_count}/{len(documents)} chunks...")
        
        summary = {
            "status": "success",
            "file": doc_name,
            "total_chunks": len(chunks),
            "total_characters": len(text),
            "avg_chunk_size": sum(c['length'] for c in chunks) // len(chunks),
            "timestamp": timestamp,
            "collection_total": self.collection.count()
        }
        
        
        print(" STORAGE COMPLETE")
        
        print(f"File: {doc_name}")
        print(f"Total Chunks: {summary['total_chunks']}")
        print(f"Total Characters: {summary['total_characters']:,}")
        print(f"Average Chunk Size: {summary['avg_chunk_size']} characters")
        print(f"Collection Total: {summary['collection_total']} chunks")
        
        
        return summary
    
    
    def query_documents(self, query: str, n_results: int = 5, 
                       filter_metadata: Optional[Dict] = None) -> Dict:
        """
        Query documents using semantic search
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            Query results with documents and metadata
        """
        print(f"\n Searching for: '{query}'")
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter_metadata
        )
        
        print(f"✓ Found {len(results['ids'][0])} results")
        return results
    
    
    def display_results(self, results: Dict, show_full_text: bool = False):
        """
        Display query results in a readable format
        
        Args:
            results: Results from query_documents()
            show_full_text: Show full text or truncated
        """
        print("\n" + "="*70)
        print("SEARCH RESULTS")
        print("="*70)
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            print(f"\n{i}. Source: {metadata['source']} (Chunk {metadata['chunk_id']+1}/{metadata['total_chunks']})")
            print(f"   Relevance Score: {1 - distance:.4f}")
            print(f"   Timestamp: {metadata['timestamp']}")
            print(f"   Text Preview:")
            
            if show_full_text:
                print(f"   {doc}")
            else:
                preview = doc[:300] + "..." if len(doc) > 300 else doc
                print(f"   {preview}")
            
    
    
    def list_stored_documents(self) -> List[Dict]:
        """
        List all stored documents with summary
        
        Returns:
            List of document summaries
        """
        results = self.collection.get()
        
        # Group by source document
        docs = {}
        for metadata in results['metadatas']:
            source = metadata['source']
            if source not in docs:
                docs[source] = {
                    'source': source,
                    'chunks': 0,
                    'timestamp': metadata['timestamp']
                }
            docs[source]['chunks'] += 1
        
        
        print("STORED DOCUMENTS")
        
        
        for i, doc in enumerate(docs.values(), 1):
            print(f"{i}. {doc['source']}")
            print(f"   Chunks: {doc['chunks']}")
            print(f"   Stored: {doc['timestamp']}")
        
        
        print(f"Total: {len(docs)} documents, {len(results['ids'])} chunks")
        
        return list(docs.values())
    
    
    def delete_document(self, source_name: str):
        """
        Delete all chunks of a document
        
        Args:
            source_name: Name of source document to delete
        """
        results = self.collection.get(
            where={"source": source_name}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            print(f"✓ Deleted {len(results['ids'])} chunks from '{source_name}'")
        else:
            print(f"⚠ No chunks found for '{source_name}'")


# ==========================================
# USAGE EXAMPLE
# ==========================================

if __name__ == "__main__":
    # Initialize store
    store = PDFDocumentStore(use_local=True)  # Set to False to use ChromaDB server
    
    # Store the Annual Report
    pdf_path = r"C:\Users\USER\OneDrive\Documents\GitHub\Research-Project\backend\lstm_stock_prediction\data\uploads\Annual-Report-2024.pdf"
    
    # Add custom metadata
    custom_metadata = {
        "document_type": "annual_report",
        "year": "2024",
        "category": "financial"
    }
    
    try:
        # Store PDF with embeddings
        summary = store.store_pdf(
            pdf_path=pdf_path,
            chunk_size=1000,      # Characters per chunk
            overlap=200,          # Overlap between chunks
            metadata=custom_metadata
        )
        
        print("\n PDF successfully stored with embeddings!")
        
        # List stored documents
        store.list_stored_documents()
        
        # Example queries
        
        print("EXAMPLE SEMANTIC SEARCH")
        
        
        # Search for specific content
        queries = [
            "revenue and financial performance",
            "business strategy and objectives",
            "risk factors and challenges"
        ]
        
        for query in queries:
            results = store.query_documents(query, n_results=3)
            store.display_results(results, show_full_text=False)
            
    except FileNotFoundError as e:
        print(f"\n Error: {e}")
        print("Please check the file path and try again.")
    except Exception as e:
        print(f"\n Unexpected error: {e}")
        import traceback
        traceback.print_exc()
