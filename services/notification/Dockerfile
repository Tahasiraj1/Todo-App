# [Task]: T004 [From]: plan.md §Project Structure
# Multi-stage Python build for notification service
# Matches backend Dockerfile pattern

# Stage 1: Build dependencies
FROM python:3.13-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target /app/deps

# Stage 2: Runtime
FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /app/deps /app/deps
COPY src/ /app/src/

ENV PYTHONPATH="/app/deps:/app"
ENV PORT=8001

EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
