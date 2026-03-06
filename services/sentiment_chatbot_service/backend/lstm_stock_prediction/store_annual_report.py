"""
INTERACTIVE PDF TO CHROMADB STORAGE
Easy-to-use script for storing PDFs with embeddings
"""

from pdf_to_chromadb import PDFDocumentStore
import os


def main():
    """
    Interactive script to store and query PDF documents
    """
    
    print("PDF TO CHROMADB - INTERACTIVE TOOL")
    
    
    # Initialize ChromaDB store
    print("\nInitializing ChromaDB connection...")
    store = PDFDocumentStore(use_local=True)  # Change to False for server mode
    
    # PDF path (your Annual Report)
    pdf_path = r"C:\Users\USER\OneDrive\Documents\GitHub\Research-Project\backend\lstm_stock_prediction\data\uploads\Annual-Report-2024.pdf"
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"\n PDF file not found at: {pdf_path}")
        print("Please update the path and try again.")
        return
    
    print(f"\n✓ Found PDF: {os.path.basename(pdf_path)}")
    print(f"  Size: {os.path.getsize(pdf_path) / 1024 / 1024:.2f} MB")
    
    # Optional: Add custom metadata
    custom_metadata = {
        "document_type": "annual_report",
        "year": "2024",
        "category": "financial",
        "organization": "Your Company Name"  # Customize this
    }
    
    
    print("STEP 1: STORE PDF WITH EMBEDDINGS")
    
    
    try:
        # Store PDF with automatic embedding generation
        summary = store.store_pdf(
            pdf_path=pdf_path,
            chunk_size=1000,      # 1000 characters per chunk (good balance)
            overlap=200,          # 200 character overlap for context
            metadata=custom_metadata
        )
        
        print("\n SUCCESS! PDF stored with embeddings in ChromaDB")
        
    except Exception as e:
        print(f"\n Error storing PDF: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # List all stored documents
    
    print("STEP 2: VERIFY STORED DOCUMENTS")
   
    
    store.list_stored_documents()
    
    # Test queries
    
    print("STEP 3: TEST SEMANTIC SEARCH")
   
    
    # Example queries - customize these based on your report content
    test_queries = [
        "financial performance and revenue",
        "key business achievements",
        "future plans and strategy",
        "risk factors and challenges",
        "market analysis and competition"
    ]
    
    print("\nRunning sample queries to test semantic search...")
    
    for i, query in enumerate(test_queries, 1):
        
        print(f"Query {i}: {query}")
        
        
        results = store.query_documents(query, n_results=3)
        store.display_results(results, show_full_text=False)
    
    # Interactive query mode
    
    print("STEP 4: INTERACTIVE QUERY MODE")
    
    print("\nYou can now query your document!")
    print("Type your questions, or type 'exit' to quit.\n")
    
    while True:
        try:
            user_query = input("Your query: ").strip()
            
            if not user_query:
                continue
            
            if user_query.lower() in ['exit', 'quit', 'q']:
                print("\n Goodbye!")
                break
            
            # Search
            results = store.query_documents(user_query, n_results=5)
            store.display_results(results, show_full_text=False)
            
            print()  # Empty line for readability
            
        except KeyboardInterrupt:
            print("\n Goodbye!")
            break
        except Exception as e:
            print(f" Error: {e}")


# Alternative: Simple function calls for quick usage
def quick_store_pdf(pdf_path: str):
    """
    Quick function to store a PDF
    
    Args:
        pdf_path: Path to PDF file
    """
    store = PDFDocumentStore(use_local=True)
    return store.store_pdf(pdf_path)


def quick_search(query: str, n_results: int = 5):
    """
    Quick function to search stored documents
    
    Args:
        query: Search query
        n_results: Number of results
    """
    store = PDFDocumentStore(use_local=True)
    results = store.query_documents(query, n_results)
    store.display_results(results)
    return results


# ==========================================
# JUPYTER NOTEBOOK USAGE
# ==========================================
# If you want to use this in a Jupyter notebook, use these cells:
#
# CELL 1: Import and Initialize
# from pdf_to_chromadb import PDFDocumentStore
# store = PDFDocumentStore(use_local=True)
#
# CELL 2: Store Your PDF
# pdf_path = r"C:\Users\USER\OneDrive\Documents\GitHub\Research-Project\backend\lstm_stock_prediction\data\uploads\Annual-Report-2024.pdf"
# summary = store.store_pdf(
#     pdf_path=pdf_path,
#     chunk_size=1000,
#     overlap=200,
#     metadata={"document_type": "annual_report", "year": "2024"}
# )
#
# CELL 3: List Stored Documents
# store.list_stored_documents()
#
# CELL 4: Search Documents
# query = "financial performance"
# results = store.query_documents(query, n_results=5)
# store.display_results(results)
#
# CELL 5: Get Specific Information
# revenue_results = store.query_documents("revenue growth and sales", n_results=3)
# store.display_results(revenue_results, show_full_text=True)
#
# CELL 6: Compare Different Topics
# topics = ["financial performance", "operational efficiency", "future strategy", "market position"]
# for topic in topics:
#     print(f"\nTopic: {topic}")
#     results = store.query_documents(topic, n_results=2)
#     store.display_results(results)


if __name__ == "__main__":
    main()
