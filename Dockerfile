FROM python:3.12-slim

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps: Tesseract OCR (+ English). Add other languages if needed.
RUN apt-get update && apt-get install -y --no-install-recommends \
      tesseract-ocr \
      tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /webapp

# Install Python deps (cached layer)
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Run as non-root
RUN adduser --disabled-password --gecos "" --uid 5678 appuser \
    && chown -R appuser:appuser /webapp
USER appuser

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "webapp.main:app"]
