"""
RAG System: PDF Search + Ollama Response Generation
Retrieval-Augmented Generation for Annual Report Q&A
"""

import json
import os
import re
from typing import List, Dict, Tuple
import requests


class PDFRagSystem:
    """
    RAG System combining PDF search with Ollama for intelligent responses
    """
    
    def __init__(self, index_file: str = "pdf_index_data/pdf_index.json", 
                 ollama_url: str = "http://localhost:11434"):
        """
        Initialize RAG system
        
        Args:
            index_file: Path to JSON index file
            ollama_url: Ollama API URL
        """
        self.index_file = index_file
        self.ollama_url = ollama_url
        self.chunks = []
        self.load_index()
        self.check_ollama()
    
    def load_index(self):
        """Load PDF index"""
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
            print(f"✓ Loaded {len(self.chunks)} chunks from index")
        else:
            print(f"❌ Index file not found: {self.index_file}")
            print("   Run simple_pdf_indexer.py first to create the index")
    
    def check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"✓ Ollama is running")
                print(f"  Available models: {len(models)}")
                for model in models[:5]:  # Show first 5 models
                    print(f"    - {model['name']}")
                return True
        except Exception as e:
            print(f"⚠ Ollama not reachable: {e}")
            print(f"  Make sure Ollama is running on {self.ollama_url}")
            return False
    
    def search_chunks(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search for relevant chunks using keyword matching
        
        Args:
            query: Search query
            n_results: Number of results
            
        Returns:
            List of relevant chunks with scores
        """
        query_lower = query.lower()
        query_terms = set(re.findall(r'\w+', query_lower))
        
        # Score chunks by keyword matches
        scored_chunks = []
        for chunk in self.chunks:
            text_lower = chunk['text'].lower()
            
            # Count term matches
            matches = sum(1 for term in query_terms if term in text_lower)
            
            if matches > 0:
                # Calculate score (percentage of query terms found)
                score = matches / len(query_terms) if query_terms else 0
                
                # Boost score if terms appear close together
                if len(query_terms) > 1 and query_lower in text_lower:
                    score *= 1.5  # Boost for exact phrase match
                
                scored_chunks.append({
                    'chunk': chunk,
                    'score': score,
                    'matches': matches
                })
        
        # Sort by score
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_chunks[:n_results]
    
    def create_context(self, search_results: List[Dict], max_chars: int = 4000) -> str:
        """
        Create context from search results for Ollama
        
        Args:
            search_results: Search results
            max_chars: Maximum context characters
            
        Returns:
            Formatted context string
        """
        context_parts = []
        total_chars = 0
        
        for i, result in enumerate(search_results, 1):
            chunk = result['chunk']
            chunk_text = chunk['text']
            
            # Check if adding this chunk would exceed limit
            if total_chars + len(chunk_text) > max_chars:
                break
            
            context_parts.append(f"[Context {i}]\n{chunk_text}\n")
            total_chars += len(chunk_text)
        
        return "\n".join(context_parts)
    
    def generate_response(self, query: str, context: str, model: str = "llama3.2:latest", 
                         stream: bool = True) -> Dict:
        """
        Generate response using Ollama with context
        
        Args:
            query: User query
            context: Retrieved context
            model: Ollama model to use
            stream: Whether to stream the response
            
        Returns:
            Response dictionary
        """
        # Create prompt with context
        prompt = f"""You are an AI assistant helping users understand the Annual Report. Use the provided context to answer the question accurately and concisely.

Context from Annual Report:
{context}

Question: {query}

Instructions:
- Answer based on the context provided
- Be specific and cite relevant information
- If the context doesn't contain enough information, say so
- Keep the answer clear and concise

Answer:"""
        
        try:
            if stream:
                # Streaming response
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": 0.3,
                            "top_p": 0.9,
                            "num_predict": 500
                        }
                    },
                    stream=True,
                    timeout=120
                )
                
                if response.status_code == 200:
                    full_response = ""
                    print()  # New line before streaming
                    
                    for line in response.iter_lines():
                        if line:
                            chunk = json.loads(line)
                            token = chunk.get("response", "")
                            full_response += token
                            print(token, end="", flush=True)
                            
                            if chunk.get("done", False):
                                print()  # New line after completion
                                return {
                                    "status": "success",
                                    "response": full_response,
                                    "model": model,
                                    "total_duration": chunk.get("total_duration", 0) / 1e9
                                }
                    
                    return {
                        "status": "success",
                        "response": full_response,
                        "model": model,
                        "total_duration": 0
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"Ollama API error: {response.status_code}",
                        "response": ""
                    }
            else:
                # Non-streaming response
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "top_p": 0.9,
                            "num_predict": 500
                        }
                    },
                    timeout=120
                )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "response": result.get("response", ""),
                    "model": model,
                    "total_duration": result.get("total_duration", 0) / 1e9
                }
            else:
                return {
                    "status": "error",
                    "error": f"Ollama API error: {response.status_code}",
                    "response": ""
                }
                
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "error": "Request timed out. Ollama might be processing a large request.",
                "response": ""
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response": ""
            }
    
    def ask(self, query: str, n_results: int = 5, model: str = "llama3.2:latest", 
            show_context: bool = False, stream: bool = True) -> Dict:
        """
        Complete RAG pipeline: Search + Generate
        
        Args:
            query: User question
            n_results: Number of chunks to retrieve
            model: Ollama model
            show_context: Whether to show retrieved context
            
        Returns:
            Response dictionary with answer and metadata
        """
        print("\n" + "="*70)
        print("RAG PIPELINE")
        print("="*70)
        
        # Step 1: Retrieve relevant chunks
        print(f"\n🔍 Searching for: '{query}'")
        search_results = self.search_chunks(query, n_results)
        
        if not search_results:
            return {
                "status": "no_context",
                "query": query,
                "response": "I couldn't find relevant information in the Annual Report to answer this question.",
                "chunks_found": 0
            }
        
        print(f"✓ Found {len(search_results)} relevant chunks")
        
        if show_context:
            print("\nRetrieved chunks:")
            for i, result in enumerate(search_results, 1):
                chunk = result['chunk']
                print(f"\n{i}. Score: {result['score']:.2f} | Chunk {chunk['id']}")
                preview = chunk['text'][:150] + "..." if len(chunk['text']) > 150 else chunk['text']
                print(f"   {preview}")
        
        # Step 2: Create context
        context = self.create_context(search_results)
        print(f"\n📄 Context created: {len(context)} characters")
        
        # Step 3: Generate response with Ollama
        print(f"\n🤖 Generating response with {model}...")
        result = self.generate_response(query, context, model, stream=stream)
        
        if result['status'] == 'success':
            print(f"✓ Response generated in {result['total_duration']:.2f}s")
            
            return {
                "status": "success",
                "query": query,
                "response": result['response'],
                "chunks_found": len(search_results),
                "chunks_used": len(search_results),
                "model": model,
                "duration": result['total_duration'],
                "context": context if show_context else None
            }
        else:
            print(f"❌ Error generating response: {result.get('error')}")
            return {
                "status": "error",
                "query": query,
                "error": result.get('error'),
                "chunks_found": len(search_results)
            }
    
    def display_response(self, result: Dict):
        """Display formatted response"""
        print("\n" + "="*70)
        print("RESPONSE")
        print("="*70)
        
        if result['status'] == 'success':
            print(f"\nQuestion: {result['query']}")
            print(f"\nAnswer:\n{result['response']}")
            print(f"\n{'-'*70}")
            print(f"Chunks retrieved: {result['chunks_found']}")
            print(f"Model: {result['model']}")
            print(f"Duration: {result['duration']:.2f}s")
        elif result['status'] == 'no_context':
            print(f"\nQuestion: {result['query']}")
            print(f"\n⚠ {result['response']}")
        else:
            print(f"\n❌ Error: {result.get('error')}")
        
        print("="*70)


# =============================================================================
# MAIN SCRIPT - Interactive Q&A
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("PDF RAG SYSTEM WITH OLLAMA")
    print("Annual Report Q&A System")
    print("="*70)
    
    # Initialize RAG system
    rag = PDFRagSystem()
    
    if not rag.chunks:
        print("\n❌ No index found. Please run simple_pdf_indexer.py first.")
        exit(1)
    
    # Test queries
    print("\n" + "="*70)
    print("EXAMPLE QUERIES")
    print("="*70)
    
    example_queries = [
        "What was the total revenue in 2024?",
        "What are the key strategic objectives?",
        "How many employees does the company have?"
    ]
    
    print("\nTrying example queries...\n")
    
    for query in example_queries:
        result = rag.ask(query, n_results=3, show_context=False)
        rag.display_response(result)
        print()
    
    # Interactive mode
    print("\n" + "="*70)
    print("INTERACTIVE Q&A MODE")
    print("="*70)
    print("\nAsk questions about the Annual Report!")
    print("Commands:")
    print("  - Type your question to get an answer")
    print("  - Type 'context' to see retrieved chunks")
    print("  - Type 'exit' or 'quit' to stop")
    print("="*70)
    
    show_context = False
    
    while True:
        try:
            user_input = input("\n💬 Your question: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'context':
                show_context = not show_context
                print(f"✓ Context display {'enabled' if show_context else 'disabled'}")
                continue
            
            # Ask question
            result = rag.ask(user_input, n_results=5, show_context=show_context)
            rag.display_response(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
