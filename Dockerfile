# Multi-stage build to minimize final image size
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install to a local directory
COPY api_requirements.txt .
RUN pip install --no-cache-dir --prefix=/build/deps -r api_requirements.txt

# Final stage - minimal runtime image
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed dependencies from builder
COPY --from=builder /build/deps /usr/local

# Copy only API code
COPY api/ ./api/

# Create token cache directory
RUN mkdir -p /app/token_cache && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Lightweight health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import os, urllib.request; api_prefix = os.environ.get('API_PREFIX', ''); urllib.request.urlopen(f'http://localhost:8000{api_prefix}/health', timeout=3)" || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
