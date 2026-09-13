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

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=10000
EXPOSE 10000

CMD gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1
