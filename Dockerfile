FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    postgresql-client \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements*.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-test.txt \
    && pip install --no-cache-dir \
        django \
        celery[redis] \
        django-celery-beat \
        shapely \
        geoalchemy2

# Copy application code
COPY . .

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]