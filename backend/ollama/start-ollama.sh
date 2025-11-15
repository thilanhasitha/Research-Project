#!/bin/bash
set -e

# Start Ollama server in the background
echo "Starting Ollama server..."
ollama serve &

# Wait a few seconds for server to initialize
sleep 5

# Pull default model if not present
MODEL_NAME="nomic-embed-text"  # Adjust as needed
if ! ollama show "$MODEL_NAME" >/dev/null 2>&1; then
    echo "Pulling model $MODEL_NAME..."
    ollama pull "$MODEL_NAME"
fi

# Keep the container alive
wait
