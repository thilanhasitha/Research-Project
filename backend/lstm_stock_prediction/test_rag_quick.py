"""
Simple single question test
"""
from pdf_rag_ollama import PDFRagSystem

print("Initializing RAG system...")
rag = PDFRagSystem()

print("\nAsking: 'How many employees does the company have?'")
print("="*70)

result = rag.ask(
    "How many employees does the company have?",
    n_results=3,
    stream=True,
    show_context=False
)

print("\n" + "="*70)
print("Done!")
