FROM python:3.11-slim

WORKDIR /main

# Copy requirements
COPY requirements.txt .

# 1. Install uvicorn/fastapi EXPLICITLY first 
# 2. Then install the rest of the requirements
RUN pip install --no-cache-dir uvicorn fastapi && \
    pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

COPY . .

EXPOSE 8003

# Use the python -m flag to be safe
CMD ["python", "-m", "uvicorn", "main.api:app", "--host", "0.0.0.0", "--port", "8003"]