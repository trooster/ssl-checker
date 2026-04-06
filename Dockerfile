# SSL Certificate Monitor Dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /root/.local /root/.local

# Set environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# Copy application code
COPY app/ ./app/
COPY run.py .

# Create non-root user
RUN useradd -m -u 1000 ssluser && \
    chown -R ssluser:ssluser /app && \
    mkdir -p /app/data && \
    chown -R ssluser:ssluser /app/data /app/logs

# Switch to non-root user
USER ssluser

# Expose port
EXPOSE 4444

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:4444/')" || exit 1

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:4444", "--workers", "2", "run:app"]
