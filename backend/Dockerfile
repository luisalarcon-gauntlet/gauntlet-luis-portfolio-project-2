# Backend Dockerfile - FastAPI application
# Multi-stage build for production-ready image

# Stage 1: Dependencies
FROM python:3.11.10-slim-bookworm AS deps

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Builder (if needed for any build steps)
FROM python:3.11.10-slim-bookworm AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Stage 3: Runtime
FROM python:3.11.10-slim-bookworm AS runner

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/ /app/

# Copy db directory for migrations and seeds
COPY db/ /db/

# Create non-root user
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app

# Make entrypoint executable
RUN chmod +x entrypoint.sh

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=15s --timeout=5s --retries=3 --start-period=20s \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application via entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
