# ------------------------------------------------------------------------------------
# STAGE 1: Builder (Compiles wheels, installs dependencies)
# ------------------------------------------------------------------------------------
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# system deps for some Python packages (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# create virtualenv and install dependencies
COPY requirements.txt ./
RUN python -m venv /app/.venv \
    && /app/.venv/bin/python -m pip install --upgrade pip setuptools wheel \
    && /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

# Runner
FROM python:3.11-slim-bookworm

WORKDIR /app

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy the pre-built virtual environment from the Builder stage
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Run the app (main.py at repo root)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
