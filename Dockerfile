# ---- builder ----
FROM python:3.12-slim AS builder

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential \
    && pip install --user --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy source
COPY . .

# ---- final ----
FROM python:3.12-alpine

# Create a non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy installed packages from builder (user-site)
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy app code
COPY --from=builder /app /app

# Filesystem & permissions
RUN chown -R appuser:appgroup /app

EXPOSE 8000

USER appuser

# Use a small worker count; Uvicorn defaults are fine for proof-of-concept
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--loop", "auto"]
