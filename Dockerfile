FROM python:3.11-slim

# MediaPipe and OpenCV need these system graphics libraries, missing from
# minimal server images (this is the "libGL.so.1: cannot open shared
# object file" crash, and from Render's native Python buildpack).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN adduser --disabled-password --gecos '' --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Change ownership of application files to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

ENV PORT=10000
EXPOSE 10000

# Use multiple workers based on CPU cores (default to 2 if not set)
ENV WORKERS_PER_CORE=2
ENV MAX_WORKERS=
ENV WEB_CONCURRENCY=

# Calculate workers at runtime
CMD sh -c "if [ -z \"$WEB_CONCURRENCY\" ]; then \
    workers=$(( $(nproc) * $WORKERS_PER_CORE )); \
    if [ -n \"$MAX_WORKERS\" ] && [ \"$workers\" -gt \"$MAX_WORKERS\" ]; then \
        workers=$MAX_WORKERS; \
    fi; \
else \
    workers=$WEB_CONCURRENCY; \
fi; \
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers $workers --worker-class sync"

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1