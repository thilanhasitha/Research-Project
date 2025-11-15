# Use a base image with bash and curl
FROM ubuntu:22.04

# Install dependencies (adjust if needed)
RUN apt-get update && \
    apt-get install -y curl bash && \
    rm -rf /var/lib/apt/lists/*

# Copy the start script into the container
COPY start-ollama.sh /start-ollama.sh

# Make it executable
RUN chmod +x /start-ollama.sh

# Set entrypoint
ENTRYPOINT ["/start-ollama.sh"]
