# Use Python 3.11 Slim for a smaller base, but we need build tools for ML libs
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# gcc/g++/make: required for llama-cpp-python
# ffmpeg: required for audio processing (faster-whisper)
# libgomp1: OpenMP support for ML execution
# curl/ca-certificates: to download models/binaries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    ffmpeg \
    libgomp1 \
    curl \
    ca-certificates \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies (including AI libs)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download Linux Piper binary (replaces Windows version)
RUN mkdir -p /app/piper && \
    curl -L https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz | tar -xz -C /app/piper --strip-components=1

# Copy source code
COPY . .

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
