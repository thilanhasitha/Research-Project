"""
Minimal test for ChromaDB PDF storage
"""

import chromadb
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
import os

print("="*70)
print("MINIMAL CHROMADB TEST")
print("="*70)

# 1. Test ChromaDB initialization
print("\n1. Testing ChromaDB initialization...")
try:
    client = chromadb.Client()
    collection = client.get_or_create_collection("test_pdf")
    print(f"   ✓ ChromaDB initialized ({collection.count()} items)")
except Exception as e:
    print(f"   Failed: {e}")
    exit(1)

# 2. Test PDF reading
print("\n2. Testing PDF extraction...")
pdf_path = r"C:\Users\USER\OneDrive\Documents\GitHub\Research-Project\backend\lstm_stock_prediction\data\uploads\Annual-Report-2024.pdf"

try:
    reader = PdfReader(pdf_path)
    page1_text = reader.pages[0].extract_text()[:500]  # First 500 chars
    print(f"   ✓ Extracted sample text ({len(page1_text)} chars)")
    print(f"   Preview: {page1_text[:100]}...")
except Exception as e:
    print(f"    Failed: {e}")
    exit(1)

# 3. Test TF-IDF embedding generation
print("\n3. Testing TF-IDF embeddings...")
try:
    vectorizer = TfidfVectorizer(max_features=384)
    sample_texts = [
        "This is a financial report",
        "Company revenue increased",
        "Future business strategy"
    ]
    embeddings = vectorizer.fit_transform(sample_texts).toarray()
    print(f"   ✓ Generated embeddings: {embeddings.shape}")
except Exception as e:
    print(f"    Failed: {e}")
    exit(1)

# 4. Test ChromaDB storage with embeddings
print("\n4. Testing ChromaDB storage...")
try:
    print(f"   - Sample embeddings shape: {embeddings.shape}")
    print(f"   - Sample embedding type: {type(embeddings[0][0])}")
    print(f"   - Adding {len(sample_texts)} documents...")
    
    collection.add(
        documents=sample_texts,
        embeddings=embeddings.tolist(),
        metadatas=[{"id": i} for i in range(len(sample_texts))],
        ids=[f"doc_{i}" for i in range(len(sample_texts))]
    )
    print(f"   ✓ Stored {collection.count()} documents")
except Exception as e:
    print(f"    Failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    print("\n   Full traceback:")
    traceback.print_exc()
    
    # Try without embeddings
    print("\n   Trying without custom embeddings...")
    try:
        collection2 = client.get_or_create_collection("test_pdf_no_emb")
        collection2.add(
            documents=sample_texts,
            metadatas=[{"id": i} for i in range(len(sample_texts))],
            ids=[f"doc2_{i}" for i in range(len(sample_texts))]
        )
        print(f"   ✓ Success without custom embeddings! Stored {collection2.count()} documents")
    except Exception as e2:
        print(f"    Also failed: {e2}")
    exit(1)

# 5. Test querying
print("\n5. Testing query...")
try:
    query_text = "financial performance"
    query_emb = vectorizer.transform([query_text]).toarray()[0].tolist()
    results = collection.query(query_embeddings=[query_emb], n_results=2)
    print(f"   ✓ Query returned {len(results['ids'][0])} results")
    for i, doc in enumerate(results['documents'][0]):
        print(f"      {i+1}. {doc}")
except Exception as e:
    print(f"    Failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)


print(" ALL TESTS PASSED!")

print("\nChromaDB is working correctly. You can now store your full PDF.")
print("The issue with the main script may be related to:")
print("  - Memory constraints with 760 large chunks")
print("  - Embedding dimension mismatch")
print("  - Collection persistence")
