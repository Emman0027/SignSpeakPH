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

# Create the app folder first, then the non-root user
# (the old order ran `chown /app` before /app existed, which failed the build)
WORKDIR /app
RUN adduser --disabled-password --gecos '' --shell /bin/bash appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# MediaPipe's lite pose model (model_complexity=0, used in
# src/utils/mediapipe_utils.py) is NOT bundled in the pip package: it is
# downloaded into site-packages on first use. Do it now, as root, so the
# non-root appuser never needs network access or write permission at runtime.
RUN python -c "import mediapipe as mp; mp.solutions.pose.Pose(model_complexity=0).close()"

# Copy the code owned by the non-root user so the app can write data/feedback
COPY --chown=appuser:appuser . .

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

# Healthcheck (uses Python because curl is not installed in python:3.11-slim).
# start-period is long because MediaPipe and the model load at startup.
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request as u; u.urlopen('http://localhost:%s/health' % os.environ.get('PORT', '10000'), timeout=3)"]
