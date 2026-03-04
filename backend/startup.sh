#!/bin/bash
# Startup script for Research Backend System
# This script ensures Ollama model is available and directories exist before starting

set -e

echo "================================================"
echo "Starting Research Backend System..."
echo "================================================"

# Create required directories
echo ""
echo "Creating knowledge base directories..."
mkdir -p /app/data/knowledge_base
mkdir -p /app/data/uploads
mkdir -p /app/logs

echo "✓ Directories created"

# Wait for Ollama to be ready
echo ""
echo "Waiting for Ollama service..."
OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; then
        echo "✓ Ollama is ready!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Waiting... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "⚠ Warning: Could not connect to Ollama"
    echo "   Some features may not work correctly"
fi

# Check for required models
echo ""
echo "Checking Ollama models..."
OLLAMA_MODEL="${OLLAMA_MODEL:-llama3}"
KB_MODEL="${KNOWLEDGE_BASE_MODEL:-llama3.2}"
EMBED_MODEL="${KNOWLEDGE_BASE_EMBEDDING_MODEL:-nomic-embed-text}"

echo "   Required models:"
echo "   - Main: $OLLAMA_MODEL"
echo "   - Knowledge Base: $KB_MODEL"
echo "   - Embeddings: $EMBED_MODEL"

# Check if knowledge base exists
echo ""
if [ -d "/app/data/knowledge_base" ] && [ "$(ls -A /app/data/knowledge_base)" ]; then
    echo "✓ Knowledge base found"
else
    echo "ℹ Knowledge base not built yet"
    echo "   To build: docker exec -it research_backend python setup_knowledge_base.py"
fi

echo ""
echo "================================================"
echo "System Configuration:"
echo "  - Ollama: $OLLAMA_HOST"
echo "  - Main Model: $OLLAMA_MODEL"
echo "  - KB Model: $KB_MODEL"
echo "  - Embedding: $EMBED_MODEL"
echo "  - MongoDB: ${MONGO_URI:0:30}..."
echo "================================================"

echo ""
echo "Starting FastAPI server..."
echo "================================================"
echo ""

# Execute the command passed to the script (uvicorn)
exec "$@"
