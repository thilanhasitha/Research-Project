"""
Knowledge Base Service using Ollama and ChromaDB
================================================
Provides CSE Annual Report information using local vector embeddings.
"""

import chromadb
from chromadb.config import Settings
import ollama
from pathlib import Path 
from typing import List, Dict, Optional 
import logging 
import json
from datetime import datetime
import PyPDF2 
import time
import os

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """Service for querying CSE Annual Report knowledge base"""
    
    def __init__(self, 
                 model_name: str = None,
                 embedding_model: str = None,
                 db_path: str = "./data/knowledge_base",
                 ollama_host: str = None):
        """
        Initialize Knowledge Base Service
        
        Args:
            model_name: Ollama model for generation (defaults to env var or llama3.2)
            embedding_model: Model for embeddings (defaults to env var or nomic-embed-text)
            db_path: Path to ChromaDB storage
            ollama_host: Ollama host URL (defaults to env var or http://localhost:11434)
        """
        # Get configuration from environment variables or defaults
        self.model_name = model_name or os.getenv('KNOWLEDGE_BASE_MODEL', 'llama3.2')
        self.embedding_model = embedding_model or os.getenv('KNOWLEDGE_BASE_EMBEDDING_MODEL', 'nomic-embed-text')
        self.ollama_host = ollama_host or os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.db_path = Path(db_path)
        
        # Configure Ollama client with host
        if self.ollama_host != 'http://localhost:11434':
            os.environ['OLLAMA_HOST'] = self.ollama_host
            logger.info(f"Using Ollama host: {self.ollama_host}")
        
        # Ensure directory exists
        try:
            self.db_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Knowledge base directory: {self.db_path.absolute()}")
        except Exception as e:
            logger.error(f"Failed to create knowledge base directory: {e}")
            raise
        
        # Validate Ollama connection
        if not self._validate_ollama():
            logger.warning("Ollama connection validation failed. Service may not work correctly.")
        
        # Initialize ChromaDB client
        try:
            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info("ChromaDB client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
        
        self.collection = None
        self._load_collection()
    
    def _validate_ollama(self) -> bool:
        """Validate Ollama connection and models"""
        try:
            # Test basic connection
            models = ollama.list()
            logger.info("Ollama connection successful")
            
            # Extract model names
            if isinstance(models, dict):
                model_names = [m.get('name', m.get('model', '')) for m in models.get('models', [])]
            else:
                model_names = [m.name if hasattr(m, 'name') else str(m) for m in getattr(models, 'models', [])]
            
            # Clean model names
            clean_names = [name.split(':')[0] for name in model_names]
            
            # Check for embedding model
            embed_base = self.embedding_model.split(':')[0]
            if embed_base not in clean_names:
                logger.warning(f"Embedding model '{self.embedding_model}' not found. Available: {', '.join(model_names)}")
                logger.warning("The system will attempt to use it anyway, but may fail.")
            else:
                logger.info(f"Embedding model '{self.embedding_model}' is available")
            
            # Check for generation model
            model_base = self.model_name.split(':')[0]
            if model_base not in clean_names:
                logger.warning(f"Generation model '{self.model_name}' not found. Available: {', '.join(model_names)}")
                logger.warning("The system will attempt to use it anyway, but may fail.")
            else:
                logger.info(f"Generation model '{self.model_name}' is available")
            
            return True
            
        except Exception as e:
            logger.error(f"Ollama validation failed: {e}")
            logger.error("Make sure Ollama is running: ollama serve")
            return False
        
    def _load_collection(self, collection_name: str = "cse_annual_report_2024"):
        """Load existing collection or prepare for new one"""
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except Exception as e:
            logger.info(f"Collection not found: {collection_name}. Use build_from_pdf to create.")
            self.collection = None
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        logger.info(f"Extracting text from {pdf_path}...")
        
        text_content = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                logger.info(f"Processing {total_pages} pages...")
                
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append(f"[Page {i + 1}]\n{page_text}")
                    
                    if (i + 1) % 10 == 0:
                        logger.info(f"Processed {i + 1}/{total_pages} pages")
                
                full_text = "\n\n".join(text_content)
                logger.info(f"Extracted {len(full_text)} characters from {total_pages} pages")
                return full_text
                
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 800, 
                   overlap: int = 150) -> List[Dict]:
        """
        Split text into overlapping chunks for better context
        
        Args:
            text: Full text to chunk
            chunk_size: Characters per chunk
            overlap: Overlap between chunks
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        sentences = text.split('\n')
        
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + "\n"
            else:
                if current_chunk:
                    chunks.append({
                        'id': f'chunk_{chunk_id}',
                        'text': current_chunk.strip(),
                        'metadata': {
                            'chunk_id': chunk_id,
                            'length': len(current_chunk),
                            'source': 'CSE Annual Report 2024',
                            'created_at': datetime.now().isoformat()
                        }
                    })
                    chunk_id += 1
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + sentence + "\n"
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                'id': f'chunk_{chunk_id}',
                'text': current_chunk.strip(),
                'metadata': {
                    'chunk_id': chunk_id,
                    'length': len(current_chunk),
                    'source': 'CSE Annual Report 2024',
                    'created_at': datetime.now().isoformat()
                }
            })
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def get_embeddings(self, text: str, retry_count: int = 3) -> List[float]:
        """Generate embeddings using Ollama with retry logic"""
        for attempt in range(retry_count):
            try:
                response = ollama.embeddings(
                    model=self.embedding_model,
                    prompt=text
                )
                
                # Handle both dict and object responses
                if isinstance(response, dict):
                    return response['embedding']
                else:
                    return response.embedding
                    
            except Exception as e:
                if attempt < retry_count - 1:
                    logger.warning(f"Embedding generation failed (attempt {attempt + 1}/{retry_count}): {e}")
                    time.sleep(1)  # Wait before retry
                else:
                    logger.error(f"Error generating embeddings after {retry_count} attempts: {e}")
                    raise
    
    def build_from_pdf(self, pdf_path: str, 
                      collection_name: str = "cse_annual_report_2024",
                      force_rebuild: bool = False) -> bool:
        """
        Build knowledge base from PDF file
        
        Args:
            pdf_path: Path to CSE annual report PDF
            collection_name: Name for the collection
            force_rebuild: If True, delete existing collection and rebuild
            
        Returns:
            True if successful
        """
        try:
            # Check if collection exists
            if force_rebuild:
                try:
                    self.client.delete_collection(name=collection_name)
                    logger.info(f"Deleted existing collection: {collection_name}")
                except:
                    pass
            
            # Create new collection
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={
                    "created_at": datetime.now().isoformat(),
                    "source": pdf_path
                }
            )
            
            # Extract and chunk text
            text = self.extract_text_from_pdf(pdf_path)
            chunks = self.chunk_text(text)
            
            # Add chunks to collection with embeddings
            logger.info("Generating embeddings and building vector database...")
            batch_size = 10
            
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                
                for chunk in batch:
                    try:
                        embedding = self.get_embeddings(chunk['text'])
                        
                        self.collection.add(
                            ids=[chunk['id']],
                            embeddings=[embedding],
                            documents=[chunk['text']],
                            metadatas=[chunk['metadata']]
                        )
                    except Exception as e:
                        logger.error(f"Error adding chunk {chunk['id']}: {e}")
                        continue
                
                logger.info(f"Processed {min(i + batch_size, len(chunks))}/{len(chunks)} chunks")
            
            logger.info(f" Knowledge base built successfully with {len(chunks)} chunks!")
            return True
            
        except Exception as e:
            logger.error(f"Error building knowledge base: {e}")
            return False
    
    def query(self, question: str, n_results: int = 5, 
             include_sources: bool = True) -> Dict:
        """
        Query the knowledge base
        
        Args:
            question: User question
            n_results: Number of relevant chunks to retrieve
            include_sources: Whether to include source documents
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        if self.collection is None:
            return {
                'error': 'Knowledge base not initialized',
                'answer': 'Please build the knowledge base first using the setup endpoint.',
                'sources': [],
                'confidence': 0.0
            }
        
        try:
            logger.info(f"Query: {question}")
            
            # Generate embedding for question
            question_embedding = self.get_embeddings(question)
            
            # Search similar chunks
            results = self.collection.query(
                query_embeddings=[question_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            if not results['documents'] or not results['documents'][0]:
                return {
                    'answer': 'No relevant information found in the CSE Annual Report.',
                    'sources': [],
                    'confidence': 0.0
                }
            
            # Build context from retrieved chunks
            context = "\n\n".join(results['documents'][0])
            
            # Detect if user wants bullet points or structured format
            wants_bullet_points = any(keyword in question.lower() for keyword in [
                'bullet points', 'list in bullet', 'key points', 'summarize', 
                'highlights', 'main', 'key', 'statistics', 'metrics', 'provide in bullet'
            ])
            
            # Generate answer using Ollama with appropriate formatting
            if wants_bullet_points:
                prompt = f"""You are a financial analyst assistant. Based on the following excerpts from the CSE (Colombo Stock Exchange) Annual Report 2024, answer the question in BULLET POINT format ONLY.

Context from CSE Annual Report 2024:
{context}

Question: {question}

CRITICAL FORMATTING REQUIREMENTS:
- You MUST respond using bullet points (• or -)
- Start each point with a bullet symbol
- Keep each point concise (1-2 lines max)
- Include specific numbers and facts
- NO paragraphs or prose - ONLY bullet points
- If data is not available, state it as a bullet point

Example format:
• Point 1 with specific data
• Point 2 with statistics
• Point 3 with key information

Your answer in bullet points:"""
            else:
                prompt = f"""You are a financial analyst assistant. Based on the following excerpts from the CSE (Colombo Stock Exchange) Annual Report 2024, provide a clear and accurate answer to the question.

Context from CSE Annual Report 2024:
{context}

Question: {question}

Instructions:
- Answer based only on the provided context
- Be specific and cite numbers/facts when available
- If the context doesn't contain the answer, say so clearly
- Keep the answer concise and professional

Answer:"""
            
            try:
                # Adjust temperature based on response format
                temperature = 0.2 if wants_bullet_points else 0.3
                
                response = ollama.generate(
                    model=self.model_name,
                    prompt=prompt,
                    options={
                        'temperature': temperature,
                        'top_p': 0.9
                    }
                )
                
                # Handle both dict and object responses
                if isinstance(response, dict):
                    answer_text = response['response'].strip()
                else:
                    answer_text = response.response.strip()
                    
            except Exception as gen_error:
                logger.error(f"Error generating answer: {gen_error}")
                answer_text = f"Error generating answer: {str(gen_error)}"
            
            # Calculate confidence
            confidence = self._calculate_confidence(results)
            
            result = {
                'answer': answer_text,
                'confidence': confidence,
                'metadata': {
                    'model': self.model_name,
                    'embedding_model': self.embedding_model,
                    'chunks_retrieved': len(results['documents'][0]),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            if include_sources:
                result['sources'] = [
                    {
                        'content': doc[:200] + '...' if len(doc) > 200 else doc,
                        'metadata': meta
                    }
                    for doc, meta in zip(results['documents'][0], results['metadatas'][0])
                ]
            
            logger.info(f"Query completed with confidence: {confidence}")
            return result
            
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            return {
                'error': str(e),
                'answer': f'Error processing query: {str(e)}',
                'sources': [],
                'confidence': 0.0
            }
    
    def _calculate_confidence(self, results: Dict) -> float:
        """Calculate confidence score based on retrieval distances"""
        try:
            if 'distances' in results and results['distances'] and results['distances'][0]:
                distances = results['distances'][0]
                # Convert distances to confidence (lower distance = higher confidence)
                avg_distance = sum(distances) / len(distances)
                # Normalize to 0-1 range (assuming max distance of 2.0)
                confidence = max(0.0, min(1.0, 1 - (avg_distance / 2.0)))
                return round(confidence, 2)
        except:
            pass
        return 0.75
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        if self.collection is None:
            return {'status': 'not_initialized'}
        
        try:
            count = self.collection.count()
            return {
                'status': 'active',
                'total_chunks': count,
                'model': self.model_name,
                'embedding_model': self.embedding_model,
                'collection_name': self.collection.name
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
