"""
Simple RAG Usage Example
Quick guide to using the PDF RAG system with Ollama
"""

from pdf_rag_ollama import PDFRagSystem

# Initialize the RAG system
print("Initializing RAG system...")
rag = PDFRagSystem()

# Example 1: Simple question
print("\n" + "="*70)
print("EXAMPLE 1: Simple Question")
print("="*70)

result = rag.ask("What was the revenue in 2024?", n_results=3, stream=True)
# Response will be streamed to console

# Example 2: Strategic information
print("\n" + "="*70)
print("EXAMPLE 2: Strategic Information")
print("="*70)

result = rag.ask("What are the company's strategic objectives?", n_results=5, stream=True)

# Example 3: Show context chunks
print("\n" + "="*70)
print("EXAMPLE 3: With Context Display")
print("="*70)

result = rag.ask(
    "What challenges does the company face?", 
    n_results=3, 
    show_context=True,  # Shows retrieved chunks
    stream=True
)

# Example 4: Custom model
print("\n" + "="*70)
print("EXAMPLE 4: Using Different Model")
print("="*70)

result = rag.ask(
    "How many employees are there?",
    n_results=3,
    model="llama3.2:latest",  # Specify model
    stream=True
)

print("\n✅ Examples complete!")
