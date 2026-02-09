FROM ollama/ollama:latest

RUN apt-get update && apt-get install -y dos2unix curl && rm -rf /var/lib/apt/lists/*

COPY start-ollama.sh /start-ollama.sh
RUN dos2unix /start-ollama.sh && chmod +x /start-ollama.sh

ENTRYPOINT ["/start-ollama.sh"]
