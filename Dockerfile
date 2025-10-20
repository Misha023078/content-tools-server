FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Avoid interactive prompts during apt operations
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (minimal) and clean up apt lists
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user (no login shell) and set ownership
RUN useradd -m -s /usr/sbin/nologin app && chown -R app:app /app
USER app

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
