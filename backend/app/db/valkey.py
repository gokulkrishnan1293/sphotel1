from collections.abc import AsyncGenerator
from typing import Any

import redis.asyncio as aioredis

from app.core.config import settings

# Cache TTL for feature flags — flags refresh within 60 seconds of DB change.
VALKEY_FLAG_TTL: int = 60


async def get_valkey() -> AsyncGenerator[Any, None]:
    """FastAPI dependency that yields an async Redis/Valkey client.

    Valkey is Redis 7.2-compatible; the redis[asyncio] package works transparently.
    decode_responses=True means all values are returned as str (not bytes).
    Typed as Any because redis-py's Redis class lacks full generic annotations.
    """
    client = aioredis.Redis.from_url(settings.VALKEY_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()
