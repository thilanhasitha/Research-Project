"""
PDF Storage for Annual Report
Uses a simple approach with local file chunking and basic search
"""

from PyPDF2 import PdfReader
import re
import json
import os
from datetime import datetime
from typing import List, Dict


class SimplePDFIndex:
    """
    Simple PDF indexing without ChromaDB complications
    Stores chunks in JSON for searching
    """
    
    def __init__(self, data_dir: str = "data"):
        """Initialize with a data directory"""
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.index_file = os.path.join(data_dir, "pdf_index.json")
        self.chunks = []
        self.load_index()
    
    def load_index(self):
        """Load existing index if available"""
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
            print(f"✓ Loaded {len(self.chunks)} existing chunks")
    
    def save_index(self):
        """Save index to file"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        print(f"✓ Saved {len(self.chunks)} chunks to {self.index_file}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        print(f"\n Reading PDF: {os.path.basename(pdf_path)}")
        reader = PdfReader(pdf_path)
        text = ""
        
        print(f"   Pages: {len(reader.pages)}")
        for i, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            text += f"\n[Page {i}]\n{page_text}\n"
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
                'id': chunk_id,
                'text': chunk_text.strip(),
                'start': start,
                'end': end,
                'length': len(chunk_text)
            })
            
            chunk_id += 1
            start = end - overlap
        
        print(f"✓ Created {len(chunks)} chunks")
        return chunks
    
    def store_pdf(self, pdf_path: str, chunk_size: int = 1000) -> Dict:
        """Store PDF in index"""
        print("\n" + "="*70)
        print("PDF INDEXING")
        print("="*70)
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        # Extract and chunk
        text = self.extract_text_from_pdf(pdf_path)
        chunks = self.chunk_text(text, chunk_size)
        
        # Add metadata
        doc_name = os.path.basename(pdf_path)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for chunk in chunks:
            chunk['source'] = doc_name
            chunk['timestamp'] = timestamp
            chunk['file_path'] = pdf_path
        
        # Store
        self.chunks.extend(chunks)
        self.save_index()
        
        summary = {
            "status": "success",
            "file": doc_name,
            "chunks": len(chunks),
            "total_chars": len(text),
            "total_indexed": len(self.chunks)
        }
        
        print("\n" + "="*70)
        print(" INDEXING COMPLETE")
        print("="*70)
        print(f"File: {doc_name}")
        print(f"Chunks: {summary['chunks']}")
        print(f"Total Characters: {summary['total_chars']:,}")
        print(f"Total Indexed Chunks: {summary['total_indexed']}")
        print("="*70)
        
        return summary
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Simple keyword search"""
        query_lower = query.lower()
        query_terms = set(re.findall(r'\w+', query_lower))
        
        # Score chunks by keyword matches
        scored_chunks = []
        for chunk in self.chunks:
            text_lower = chunk['text'].lower()
            # Count term matches
            matches = sum(1 for term in query_terms if term in text_lower)
            if matches > 0:
                # Calculate score
                score = matches / len(query_terms) if query_terms else 0
                scored_chunks.append({
                    'chunk': chunk,
                    'score': score,
                    'matches': matches
                })
        
        # Sort by score
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_chunks[:n_results]
    
    def display_results(self, results: List[Dict], show_full: bool = False):
        """Display search results"""
        print("\n" + "="*70)
        print(f"SEARCH RESULTS ({len(results)} found)")
        print("="*70)
        
        for i, result in enumerate(results, 1):
            chunk = result['chunk']
            score = result['score']
            matches = result['matches']
            
            print(f"\n{i}. {chunk['source']} - Chunk {chunk['id']}")
            print(f"   Score: {score:.2f} ({matches} term matches)")
            
            if show_full:
                print(f"   Text:\n   {chunk['text']}")
            else:
                preview = chunk['text'][:300]
                if len(chunk['text']) > 300:
                    preview += "..."
                print(f"   Preview: {preview}")
            print("-"*70)
    
    def list_documents(self):
        """List indexed documents"""
        docs = {}
        for chunk in self.chunks:
            source = chunk['source']
            if source not in docs:
                docs[source] = {
                    'source': source,
                    'chunks': 0,
                    'timestamp': chunk['timestamp']
                }
            docs[source]['chunks'] += 1
        
        print("\n" + "="*70)
        print("INDEXED DOCUMENTS")
        print("="*70)
        for i, doc in enumerate(docs.values(), 1):
            print(f"{i}. {doc['source']}")
            print(f"   Chunks: {doc['chunks']}")
            print(f"   Indexed: {doc['timestamp']}")
        print("="*70)


# =============================================================================
# MAIN SCRIPT
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("SIMPLE PDF INDEXER")
    print("No external dependencies - works everywhere!")
    print("="*70)
    
    # Initialize
    indexer = SimplePDFIndex(data_dir="pdf_index_data")
    
    # PDF path
    pdf_path = r"C:\Users\USER\OneDrive\Documents\GitHub\Research-Project\backend\lstm_stock_prediction\data\uploads\Annual-Report-2024.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"\n PDF not found: {pdf_path}")
        exit(1)
    
    try:
        # Store PDF
        summary = indexer.store_pdf(pdf_path, chunk_size=1000)
        
        # List documents
        indexer.list_documents()
        
        # Test queries
        print("\n" + "="*70)
        print("TESTING SEARCH")
        print("="*70)
        
        test_queries = [
            "revenue financial performance",
            "business strategy objectives",
            "risk factors challenges",
            "future plans development"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            results = indexer.search(query, n_results=3)
            indexer.display_results(results)
        
        # Interactive mode
        print("\n" + "="*70)
        print("INTERACTIVE SEARCH MODE")
        print("Type your queries or 'exit' to quit")
        print("="*70)
        
        while True:
            try:
                user_query = input("\nYour query: ").strip()
                
                if not user_query or user_query.lower() in ['exit', 'quit', 'q']:
                    print("\n Goodbye!")
                    break
                
                results = indexer.search(user_query, n_results=5)
                indexer.display_results(results)
                
            except KeyboardInterrupt:
                print("\n\n Goodbye!")
                break
            except Exception as e:
                print(f" Error: {e}")
        
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
