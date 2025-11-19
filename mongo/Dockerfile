FROM mongo:8.0
RUN apt-get update && apt-get install -y openssl && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /scripts
WORKDIR /scripts
COPY dataset.json /scripts/dataset.json
COPY policies.json /scripts/policies.json
COPY mongo-entrypoint.sh /scripts/mongo-entrypoint.sh
RUN chmod +x /scripts/mongo-entrypoint.sh
ENTRYPOINT ["/scripts/mongo-entrypoint.sh"]
