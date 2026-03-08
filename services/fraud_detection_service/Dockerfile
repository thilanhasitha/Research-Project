FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --timeout=1000 --retries=5 -r requirements.txt

COPY main ./main
COPY src ./src
COPY static ./static

EXPOSE 8003

CMD ["uvicorn", "main.api:app", "--host", "0.0.0.0", "--port", "8003"]