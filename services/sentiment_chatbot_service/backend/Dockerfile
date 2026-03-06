# Use lightweight Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (for efficient caching)
COPY requirements-minimal.txt requirements.txt
COPY requirements.txt requirements-full.txt

# Install minimal dependencies for faster build
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Copy and prepare startup script
COPY startup.sh /startup.sh
RUN dos2unix /startup.sh && chmod +x /startup.sh

# Expose backend port
EXPOSE 8001

# Use startup script as entrypoint
ENTRYPOINT ["/startup.sh"]

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload", "--timeout-keep-alive", "300"]
