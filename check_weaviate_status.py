"""
Script to check Weaviate database status and verify embeddings storage.
"""
import weaviate
import json
from typing import Dict, Any

def check_weaviate_status():
    """Check Weaviate connection and data storage status."""
    
    print("=" * 60)
    print("WEAVIATE DATABASE STATUS CHECK")
    print("=" * 60)
    
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
        
        print("\n Successfully connected to Weaviate")
        print(f"  Host: localhost:8080")
        
        # Check if Weaviate is ready
        if client.is_ready():
            print(" Weaviate is ready and operational")
        else:
            print(" Weaviate is not ready")
            return
        
        # Get cluster metadata
        try:
            meta = client.get_meta()
            print(f"\n Weaviate Version: {meta.get('version', 'Unknown')}")
        except Exception as e:
            print(f"\n⚠ Could not get metadata: {e}")
        
        # List all collections
        print("\n" + "-" * 60)
        print("COLLECTIONS IN WEAVIATE")
        print("-" * 60)
        
        collections_list = []
        for collection in client.collections.list_all():
            collections_list.append(collection)
            print(f"\n Collection: {collection}")
        
        if not collections_list:
            print("\n⚠ No collections found in Weaviate")
            print("  This means no data has been stored yet.")
            client.close()
            return
        
        # Check each collection for data and embeddings
        print("\n" + "-" * 60)
        print("COLLECTION DETAILS & EMBEDDINGS CHECK")
        print("-" * 60)
        
        for collection_name in collections_list:
            print(f"\n📁 Collection: {collection_name}")
            print("-" * 40)
            
            try:
                collection = client.collections.get(collection_name)
                
                # Get collection configuration
                config = collection.config.get()
                print(f"  Vector Config: {config.vector_config}")
                
                # Count objects
                response = collection.aggregate.over_all(total_count=True)
                total_count = response.total_count
                print(f"  Total Objects: {total_count}")
                
                if total_count == 0:
                    print("  ⚠ Collection is empty - no objects stored")
                    continue
                
                # Get a sample object with vector
                sample = collection.query.fetch_objects(
                    include_vector=True,
                    limit=1
                )
                
                if sample.objects:
                    obj = sample.objects[0]
                    print(f"\n  ✓ Sample Object Found:")
                    print(f"    UUID: {obj.uuid}")
                    
                    # Check if vector exists
                    if hasattr(obj, 'vector') and obj.vector:
                        vector = obj.vector
                        if isinstance(vector, dict):
                            # Multiple named vectors
                            for vec_name, vec_data in vector.items():
                                print(f"    Vector '{vec_name}': {len(vec_data)} dimensions")
                                print(f"    Sample values: {vec_data[:5]}...")
                        else:
                            # Single default vector
                            print(f" Vector Dimensions: {len(vector)}")
                            print(f" Sample values: {vector[:5]}...")
                        print(f" EMBEDDINGS ARE STORED!")
                    else:
                        print(f" NO VECTOR/EMBEDDING FOUND")
                    
                    # Show properties
                    print(f"\n    Properties:")
                    if hasattr(obj, 'properties'):
                        for key, value in obj.properties.items():
                            if isinstance(value, str) and len(value) > 100:
                                value = value[:100] + "..."
                            print(f"      - {key}: {value}")
                
                # Try to get more statistics
                print(f"\n  Checking for more objects...")
                all_objects = collection.query.fetch_objects(limit=10)
                
                vectors_count = 0
                no_vectors_count = 0
                
                for obj in all_objects.objects:
                    if hasattr(obj, 'vector') and obj.vector:
                        vectors_count += 1
                    else:
                        no_vectors_count += 1
                
                print(f"    Objects with embeddings: {vectors_count}/{len(all_objects.objects)}")
                if no_vectors_count > 0:
                    print(f"    Objects without embeddings: {no_vectors_count}")
                
            except Exception as e:
                print(f" Error checking collection {collection_name}: {e}")
        
        # Final summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        if collections_list:
            print(f" Found {len(collections_list)} collection(s)")
            print(f"  Collections: {', '.join(collections_list)}")
        else:
            print(" No collections exist yet")
        
        client.close()
        print("\n Connection closed")
        
    except Exception as e:
        print(f"\n Error connecting to Weaviate: {e}")
        print("\nTroubleshooting tips:")
        print("  1. Ensure Weaviate is running: docker compose ps")
        print("  2. Check if port 8080 is accessible")
        print("  3. Verify Weaviate logs: docker compose logs weaviate")

if __name__ == "__main__":
    check_weaviate_status()
