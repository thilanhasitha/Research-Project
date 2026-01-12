# Use lightweight Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy only requirements first (for efficient caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# RUN pip install --no-deps ollama-python==0.1.2

# Copy the rest of the application code
COPY . .

# Expose backend port
EXPOSE 8001

# Run the FastAPI server with increased timeout for LLM operations
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload", "--timeout-keep-alive", "300"]
