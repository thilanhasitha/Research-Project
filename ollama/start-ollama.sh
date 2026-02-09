#!/bin/bash
set -e

echo "Starting Ollama server..."
ollama serve &

echo "Waiting for Ollama to start..."
# Wait for Ollama to be ready with better retry logic
for i in {1..30}; do
  if ollama list >/dev/null 2>&1; then
    echo "Ollama is ready!"
    break
  fi
  echo "Waiting for Ollama to be ready... ($i/30)"
  sleep 2
done

# Pull your required models
MODELS=("llama3" "nomic-embed-text")

for MODEL in "${MODELS[@]}"; do
  echo "Checking model: $MODEL"
  if ! ollama show $MODEL >/dev/null 2>&1; then
    echo "Pulling model: $MODEL"
    ollama pull $MODEL
  else
    echo "$MODEL already exists. Skipping pull."
  fi
done

echo "All models ready. Ollama is running."

# Keep container running
wait
