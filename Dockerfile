# IteraMindAI — container image for Hugging Face Spaces (Docker SDK),
# Railway, Render, Fly.io, or any Docker host.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=7860

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Hugging Face Spaces routes to port 7860 by default.
EXPOSE 7860

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
