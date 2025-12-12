from old.scripts.embedding_service import EmbeddingService

service = EmbeddingService()
text = "Apple stock price surged today."

embedding = service.get_embedding(text)

if embedding:
    print("Embedding generated successfully!")
    print("Length:", len(embedding))
    print("First 10 values:", embedding[:10])
else:
    print("Failed to generate embedding.")
