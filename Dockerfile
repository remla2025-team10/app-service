FROM python:3.10-slim AS builder

WORKDIR /app

# Install git and build tools incase of uncommon cpu architectures
RUN apt-get update && \
    apt-get install -y --no-install-recommends git build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Runtime stage ---
FROM python:3.10-slim AS runtime

WORKDIR /app

# Copy installed Python packages from the builder
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY . .

EXPOSE 5000

CMD ["python", "run.py"]

LABEL org.opencontainers.image.source="https://github.com/remla2025-team10/app-service"
