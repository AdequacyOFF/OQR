FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including PaddleOCR requirements)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    zbar-tools \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.3

# Copy poetry files
COPY backend/pyproject.toml backend/poetry.lock* /app/

# Configure poetry to not create virtual env
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-root --no-interaction --no-ansi

# Copy application code
COPY backend/src /app/src

# Set PYTHONPATH
ENV PYTHONPATH=/app/src

# Run Celery worker
CMD celery -A olimpqr.infrastructure.tasks.celery_app worker --loglevel=info --concurrency=2
