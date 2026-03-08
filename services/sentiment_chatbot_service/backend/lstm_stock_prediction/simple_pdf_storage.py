"""
Simple PDF to ChromaDB Storage - No External Embedding Dependencies
Uses basic TF-IDF style embeddings for quick setup
"""

import chromadb
from datetime import datetime
import os
from typing import List, Dict
from PyPDF2 import PdfReader
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class SimplePDFStore:
    """
    Store PDF documents in ChromaDB with scikit-learn TF-IDF embeddings
    """
    
    def __init__(self):
        """Initialize local ChromaDB client"""
        print("\n Initializing ChromaDB (local mode)...")
        self.client = chromadb.Client()
        
        # Create collection
        self.collection = self.client.get_or_create_collection(
            name="pdf_documents_simple",
            metadata={"description": "PDF storage with TF-IDF embeddings"}
        )
        
        # TF-IDF vectorizer for embeddings
        self.vectorizer = TfidfVectorizer(
            max_features=384,  # Match common embedding dimensions
            ngram_range=(1, 2),
            min_df=1
        )
        
        print(f"✓ ChromaDB ready ({self.collection.count()} chunks)")
    
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        reader = PdfReader(pdf_path)
        text = ""
        
        print(f"\n Reading: {os.path.basename(pdf_path)}")
        print(f"   Pages: {len(reader.pages)}")
        
        for i, page in enumerate(reader.pages, 1):
            text += f"\n--- Page {i} ---\n{page.extract_text()}\n"
            if i % 20 == 0:
                print(f"   Processed {i} pages...")
        
        print(f"✓ Extracted {len(text):,} characters")
        return text
    
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """Split text into chunks"""
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            if end < len(text):
                last_period = chunk_text.rfind('.')
                if last_period > chunk_size * 0.7:
                    end = start + last_period + 1
                    chunk_text = text[start:end]
            
            chunks.append({
                'text': chunk_text.strip(),
                'chunk_id': chunk_id,
                'length': len(chunk_text)
            })
            
            chunk_id += 1
            start = end - overlap
        
        print(f"✓ Created {len(chunks)} chunks")
        return chunks
    
    
    def store_pdf(self, pdf_path: str, chunk_size: int = 1000) -> Dict:
        """Store PDF with TF-IDF embeddings"""
        print("\n" + "="*70)
        print("PDF TO CHROMADB STORAGE (SIMPLE MODE)")
        print("="*70)
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        # Extract and chunk
        text = self.extract_text_from_pdf(pdf_path)
        chunks = self.chunk_text(text, chunk_size)
        
        # Generate TF-IDF embeddings
        print(f"\n Generating TF-IDF embeddings...")
        chunk_texts = [c['text'] for c in chunks]
        
        try:
            embeddings = self.vectorizer.fit_transform(chunk_texts).toarray()
            print(f"✓ Generated embeddings: shape {embeddings.shape}")
        except Exception as e:
            print(f" Error generating embeddings: {e}")
            raise
        
        # Prepare for storage
        doc_name = os.path.basename(pdf_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        documents = []
        metadatas = []
        ids = []
        embeddings_list = []
        
        for i, chunk in enumerate(chunks):
            doc_id = f"{doc_name}_{timestamp}_chunk_{i}"
            
            metadata = {
                "source": doc_name,
                "timestamp": timestamp,
                "chunk_id": i,
                "total_chunks": len(chunks),
                "file_path": pdf_path,
                "type": "pdf_document"
            }
            
            documents.append(chunk['text'])
            metadatas.append(metadata)
            ids.append(doc_id)
            embeddings_list.append(embeddings[i].tolist())
        
        # Store in batches
        print(f"\n Storing {len(documents)} chunks in ChromaDB...")
        
        batch_size = 50  # Smaller batches for stability
        stored_count = 0
        
        try:
            for i in range(0, len(documents), batch_size):
                batch_end = min(i + batch_size, len(documents))
                
                try:
                    self.collection.add(
                        documents=documents[i:batch_end],
                        metadatas=metadatas[i:batch_end],
                        ids=ids[i:batch_end],
                        embeddings=embeddings_list[i:batch_end]
                    )
                    
                    stored_count = batch_end
                    print(f"   Stored {stored_count}/{len(documents)} chunks...")
                    
                except Exception as batch_error:
                    print(f"⚠ Error in batch {i}-{batch_end}: {batch_error}")
                    continue
                
        except Exception as e:
            print(f"\n Storage error: {e}")
            if stored_count >0:
                print(f"   Partial success: {stored_count}/{len(documents)} chunks stored")
            raise
        
        summary = {
            "status": "success",
            "file": doc_name,
            "total_chunks": len(chunks),
            "total_characters": len(text),
            "collection_total": self.collection.count()
        }
        
        print("\n" + "="*70)
        print(" STORAGE COMPLETE!")
        print("="*70)
        print(f"File: {doc_name}")
        print(f"Chunks: {summary['total_chunks']}")
        print(f"Characters: {summary['total_characters']:,}")
        print(f"Collection Total: {summary['collection_total']}")
        print("="*70)
        
        return summary
    
    
    def query_documents(self, query: str, n_results: int = 5) -> Dict:
        """Query using TF-IDF similarity"""
        print(f"\n Searching: '{query}'")
        
        # Transform query to TF-IDF space
        query_embedding = self.vectorizer.transform([query]).toarray()[0].tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        print(f"✓ Found {len(results['ids'][0])} results")
        return results
    
    
    def display_results(self, results: Dict, show_full: bool = False):
        """Display search results"""
        print("\n" + "="*70)
        print("SEARCH RESULTS")
        print("="*70)
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            print(f"\n{i}. {metadata['source']} (Chunk {metadata['chunk_id']+1}/{metadata['total_chunks']})")
            print(f"   Score: {1 - distance:.4f}")
            
            if show_full:
                print(f"   Text: {doc}")
            else:
                preview = doc[:300] + "..." if len(doc) > 300 else doc
                print(f"   Preview: {preview}")
            print("-"*70)
    
    
    def list_documents(self):
        """List stored documents"""
        results = self.collection.get()
        
        docs = {}
        for meta in results['metadatas']:
            source = meta['source']
            if source not in docs:
                docs[source] = {'source': source, 'chunks': 0, 'timestamp': meta['timestamp']}
            docs[source]['chunks'] += 1
        
        print("\n" + "="*70)
        print("STORED DOCUMENTS")
        print("="*70)
        for i, doc in enumerate(docs.values(), 1):
            print(f"{i}. {doc['source']} - {doc['chunks']} chunks - {doc['timestamp']}")
        print("="*70)


# =============================================================================
# MAIN SCRIPT
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("SIMPLE PDF TO CHROMADB STORAGE")
    print("Using scikit-learn TF-IDF (No external dependencies)")
    print("="*70)
    
    # Initialize
    store = SimplePDFStore()
    
    # PDF path
    pdf_path = r"C:\Users\USER\OneDrive\Documents\GitHub\Research-Project\backend\lstm_stock_prediction\data\uploads\Annual-Report-2024.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"\n PDF not found: {pdf_path}")
        exit(1)
    
    try:
        # Store PDF
        summary = store.store_pdf(pdf_path, chunk_size=1000)
        
        # List documents
        store.list_documents()
        
        # Test queries
        print("\n" + "="*70)
        print("TESTING SEMANTIC SEARCH")
        print("="*70)
        
        test_queries = [
            "revenue and financial performance",
            "business strategy",
            "risk factors",
            "future plans"
        ]
        
        for query in test_queries:
            results = store.query_documents(query, n_results=3)
            store.display_results(results)
        
        # Interactive mode
        print("\n" + "="*70)
        print("INTERACTIVE QUERY MODE")
        print("Type your questions or 'exit' to quit")
        print("="*70)
        
        while True:
            try:
                user_query = input("\nYour query: ").strip()
                
                if not user_query or user_query.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                results = store.query_documents(user_query, n_results=5)
                store.display_results(results)
                
            except KeyboardInterrupt:
                print("\n\n Goodbye!")
                break
            except Exception as e:
                print(f" Error: {e}")
        
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
