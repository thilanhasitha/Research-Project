# Dockerfile
FROM mongo:8.0

# Install openssl
RUN apt-get update && apt-get install -y openssl && rm -rf /var/lib/apt/lists/*

# Create a directory for scripts
RUN mkdir -p /scripts
WORKDIR /scripts

# Copy dataset files
COPY social_media_data.json /scripts/social_media_data.json
COPY policies.json /scripts/policies.json

# Copy entrypoint script
COPY mongo-entrypoint.sh /scripts/mongo-entrypoint.sh
RUN chmod +x /scripts/mongo-entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/scripts/mongo-entrypoint.sh"]
