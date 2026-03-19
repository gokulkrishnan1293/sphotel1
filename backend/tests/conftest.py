import os

# Set required env vars before any app import.
# pydantic-settings reads these at Settings() instantiation time.
# Tests that don't need a real DB (e.g. health endpoint) use these dummy values.
# Story 2.1 will replace this with proper test DB fixtures using a real test database.
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test"
)
os.environ.setdefault("VALKEY_URL", "redis://localhost:6379")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-only-not-for-production")
