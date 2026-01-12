#!/bin/bash
set -e

echo "Starting Ollama server..."
ollama serve &

echo "Waiting for Ollama to start..."
sleep 5

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

wait
