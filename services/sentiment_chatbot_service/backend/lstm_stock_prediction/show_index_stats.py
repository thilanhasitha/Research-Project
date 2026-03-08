"""
Show statistics about the indexed PDF
"""
import json
import os

index_file = "pdf_index_data/pdf_index.json"

if os.path.exists(index_file):
    with open(index_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\n" + "="*70)
    print("PDF INDEX STATISTICS")
    print("="*70)
    
    print(f"\nTotal Chunks: {len(data)}")
    
    total_chars = sum(len(chunk['text']) for chunk in data)
    print(f"Total Characters: {total_chars:,}")
    print(f"Average Chunk Size: {total_chars//len(data)} characters")
    
    unique_sources = set(chunk['source'] for chunk in data)
    print(f"\nDocuments Indexed: {len(unique_sources)}")
    
    for src in unique_sources:
        chunks = [c for c in data if c['source'] == src]
        chars = sum(len(c['text']) for c in chunks)
        print(f"\n   {src}")
        print(f"     Chunks: {len(chunks)}")
        print(f"     Characters: {chars:,}")
        print(f"     Avg Chunk Size: {chars//len(chunks)} chars")
        if chunks:
            print(f"     Timestamp: {chunks[0].get('timestamp', 'N/A')}")
    
    print("\n" + "="*70)
    print("STORAGE INFO")
    print("="*70)
    file_size = os.path.getsize(index_file)
    print(f"Index File: {index_file}")
    print(f"File Size: {file_size / 1024 / 1024:.2f} MB")
    print("="*70)
    
    print("\n  NOTE: This uses JSON file storage, NOT ChromaDB")
    print("   ChromaDB had Windows compatibility issues with embeddings.")
    print("   The current solution uses keyword-based search on JSON data.")
    
else:
    print(f" Index file not found: {index_file}")
