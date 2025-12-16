#!/bin/bash
# Startup script for RSS News Collection System
# This script ensures Ollama model is available before starting

echo " Starting RSS News Collection System..."

# Wait for Ollama to be ready
echo " Waiting for Ollama service..."
until curl -s http://ollama:11434/api/tags > /dev/null 2>&1; do
    echo "   Ollama not ready yet, waiting..."
    sleep 2
done
echo " Ollama is ready!"

# Check if model exists
MODEL_NAME="${OLLAMA_MODEL:-llama3.2}"
echo " Checking for model: $MODEL_NAME"

# Try to pull model (will skip if already exists)
if ! curl -s http://ollama:11434/api/tags | grep -q "\"name\":\"$MODEL_NAME\""; then
    echo " Pulling model $MODEL_NAME (this may take a few minutes)..."
    docker exec ollama_new ollama pull $MODEL_NAME || echo "⚠️ Could not pull model, it may already exist"
else
    echo " Model $MODEL_NAME is already available"
fi

echo " System ready! Starting FastAPI server..."
