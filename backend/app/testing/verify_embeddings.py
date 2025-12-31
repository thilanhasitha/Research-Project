"""
Comprehensive script to verify Weaviate embeddings storage and functionality.
"""
import weaviate
from weaviate.classes.query import MetadataQuery

def verify_embeddings():
    """Verify that Weaviate is storing embeddings properly."""
    
    print("=" * 70)
    print("WEAVIATE EMBEDDINGS VERIFICATION")
    print("=" * 70)
    
    try:
        # Connect to Weaviate
        client = weaviate.connect_to_custom(
            http_host="localhost",
            http_port=8080,
            http_secure=False,
            grpc_host="localhost",
            grpc_port=50051,
            grpc_secure=False
        )
        
        print("\n✓ Successfully connected to Weaviate")
        
        # Check if ready
        if not client.is_ready():
            print("\n✗ Weaviate is not ready!")
            return
        
        print("✓ Weaviate is ready and operational")
        
        # Get metadata
        meta = client.get_meta()
        print(f"\n Weaviate Version: {meta.get('version', 'Unknown')}")
        
        # Check for text2vec-ollama module
        modules = meta.get('modules', {})
        print(f"\n Loaded Modules:")
        for module_name, module_info in modules.items():
            print(f"  - {module_name}")
            if module_name == "text2vec-ollama":
                print(f"    ✓ Ollama integration active")
        
        # List collections
        print("\n" + "-" * 70)
        print("COLLECTIONS")
        print("-" * 70)
        
        collections_list = list(client.collections.list_all())
        print(f"\n Found {len(collections_list)} collection(s): {collections_list}")
        
        if not collections_list:
            print("\n No collections found!")
            client.close()
            return
        
        # Check RSSNews collection
        if "RSSNews" in collections_list:
            print("\n" + "-" * 70)
            print("RSSNEWS COLLECTION ANALYSIS")
            print("-" * 70)
            
            collection = client.collections.get("RSSNews")
            
            # Get collection config
            config = collection.config.get()
            print(f"\n Collection Configuration:")
            print(f"  Vectorizer: {config.vectorizer_config}")
            
            # Count objects
            response = collection.aggregate.over_all(total_count=True)
            total_count = response.total_count
            print(f"\n Total Objects: {total_count}")
            
            if total_count == 0:
                print("\n Collection is empty - no data stored!")
                client.close()
                return
            
            # Get sample objects WITH vectors
            print("\n" + "-" * 70)
            print("VECTOR ANALYSIS")
            print("-" * 70)
            
            print("\n Fetching sample objects with vectors...")
            
            sample = collection.query.fetch_objects(
                include_vector=True,
                limit=5
            )
            
            if not sample.objects:
                print(" No objects found!")
                client.close()
                return
            
            print(f"\n Retrieved {len(sample.objects)} sample object(s)")
            
            vectors_found = 0
            vectors_missing = 0
            vector_dimensions = None
            
            for i, obj in enumerate(sample.objects, 1):
                print(f"\n--- Object {i} ---")
                print(f"  UUID: {obj.uuid}")
                
                # Check properties
                if hasattr(obj, 'properties'):
                    props = obj.properties
                    print(f"  Title: {props.get('title', 'N/A')[:50]}...")
                    print(f"  Has content: {bool(props.get('content'))}")
                
                # Check vector
                if hasattr(obj, 'vector') and obj.vector:
                    vectors_found += 1
                    
                    if isinstance(obj.vector, dict):
                        # Named vectors
                        for vec_name, vec_data in obj.vector.items():
                            if vec_data:
                                print(f"   Vector '{vec_name}': {len(vec_data)} dimensions")
                                vector_dimensions = len(vec_data)
                                print(f"    Sample values: {vec_data[:5]}")
                    else:
                        # Single vector
                        print(f"   Vector: {len(obj.vector)} dimensions")
                        vector_dimensions = len(obj.vector)
                        print(f"    Sample values: {obj.vector[:5]}")
                else:
                    vectors_missing += 1
                    print(f"   NO VECTOR FOUND!")
            
            # Summary
            print("\n" + "=" * 70)
            print("SUMMARY")
            print("=" * 70)
            print(f"\n Collection Stats:")
            print(f"  Total objects: {total_count}")
            print(f"  Sample size checked: {len(sample.objects)}")
            print(f"  Objects with vectors: {vectors_found}")
            print(f"  Objects without vectors: {vectors_missing}")
            
            if vector_dimensions:
                print(f"  Vector dimensions: {vector_dimensions}")
            
            if vectors_found > 0:
                print(f"\n SUCCESS! Embeddings are being stored properly!")
                print(f"   {vectors_found}/{len(sample.objects)} sample objects have vectors")
            else:
                print(f"\n PROBLEM! No vectors found in sample objects!")
                print(f"   Check Ollama connection and text2vec-ollama configuration")
            
            # Test vector search
            print("\n" + "-" * 70)
            print("VECTOR SEARCH TEST")
            print("-" * 70)
            
            if vectors_found > 0:
                print("\n Testing semantic search with 'Sri Lanka news'...")
                try:
                    results = collection.query.near_text(
                        query="Sri Lanka news",
                        limit=3,
                        return_metadata=MetadataQuery(distance=True)
                    )
                    
                    if results.objects:
                        print(f"\n Found {len(results.objects)} results!")
                        for i, result in enumerate(results.objects, 1):
                            print(f"\n  Result {i}:")
                            print(f"    Title: {result.properties.get('title', 'N/A')[:60]}...")
                            if hasattr(result.metadata, 'distance'):
                                print(f"    Distance: {result.metadata.distance:.4f}")
                    else:
                        print(" No results returned from vector search")
                        
                except Exception as e:
                    print(f" Vector search failed: {e}")
            
        else:
            print(f"\n RSSNews collection not found!")
            print(f"   Available collections: {collections_list}")
        
        client.close()
        print("\n" + "=" * 70)
        print("Verification complete!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_embeddings()
