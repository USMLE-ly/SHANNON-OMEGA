# =============================================================================
# Luxor Pro Stylist Tweaks — Dockerfile
# =============================================================================
# Multi-stage build: slim Python image with optional GPU support.
# =============================================================================

FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Runtime image ──────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Install runtime system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY main.py orchestrator.py ./

# Create cache directory
RUN mkdir -p /data/cache && chmod 777 /data/cache

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
    CMD curl -sf http://localhost:8767/tweaks/health || exit 1

EXPOSE 8767

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8767", "--workers", "4", "--proxy-headers", "--forwarded-allow-ips", "*"]
