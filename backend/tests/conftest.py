"""Shared test fixtures."""

import os
import pytest

# Override settings before importing anything that uses them
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-at-least-32-chars")
os.environ.setdefault("HMAC_SECRET_KEY", "test-hmac-secret-key-for-testing-32-chars")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://olimpqr_user:olimpqr_pass@localhost:5432/olimpqr_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("MINIO_ENDPOINT", "localhost:9000")
os.environ.setdefault("MINIO_ACCESS_KEY", "minioadmin")
os.environ.setdefault("MINIO_SECRET_KEY", "minioadmin")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/0")
os.environ.setdefault("ENVIRONMENT", "test")
