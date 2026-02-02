# [Task]: T015, T045 [From]: spec.md FR-002, FR-003, FR-004, FR-005
# Multi-stage build for FastAPI backend - Kubernetes compatible
# Uses UV package manager with pyproject.toml
# Multi-arch: docker buildx build --platform linux/amd64,linux/arm64 -t <tag> .

# Stage 1: Builder stage
FROM python:3.13-slim AS builder

WORKDIR /app

# Install system dependencies and UV
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add UV to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies using UV (creates .venv)
RUN uv sync --frozen --no-dev

# Stage 2: Runtime stage
FROM python:3.13-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .

# Set up environment - use virtual environment Python explicitly
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

# Expose port (default 8000 for Kubernetes, configurable via PORT env)
EXPOSE 8000

# Health check for Kubernetes liveness/readiness probes
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD /app/.venv/bin/python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8000}/health')" || exit 1

# Use PORT environment variable if provided, otherwise default to 8000
CMD ["sh", "-c", "/app/.venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
