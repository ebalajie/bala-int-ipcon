# ---- Stage 1: Builder ----
FROM python:3.12-slim AS builder

WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install dependencies into /app/deps
RUN pip install --prefix=/app/deps -r requirements.txt

# ---- Stage 2: Final Image ----
FROM python:3.12-slim

# Create non-root user
RUN useradd -m appuser

WORKDIR /app

# Copy installed dependencies
COPY --from=builder /app/deps /usr/local

# Copy application code
COPY main.py .

# Switch to non-root user
USER appuser

# Expose app port
EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
