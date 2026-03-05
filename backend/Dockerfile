FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
# Filter out heavy ML libs for the main API to keep it lean
RUN grep -v "faster-whisper\|llama-cpp-python\|piper-tts" requirements.txt > api_reqs.txt
RUN pip install --no-cache-dir -r api_reqs.txt

# Copy source code
COPY . .

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
