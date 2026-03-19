import json
import uuid
from typing import Any, cast

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.valkey import VALKEY_FLAG_TTL
from app.repositories.feature_flags import get_feature_flags_from_db
from app.schemas.feature_flags import FeatureFlagsDict

_CACHE_KEY_PREFIX = "feature_flags"


def _cache_key(tenant_id: uuid.UUID) -> str:
    return f"{_CACHE_KEY_PREFIX}:{tenant_id}"


async def get_feature_flags(
    tenant_id: uuid.UUID,
    db: AsyncSession,
    valkey: Any,
) -> FeatureFlagsDict:
    """Return feature flags for a tenant, using Valkey cache with 60s TTL.

    Cache miss falls back to PostgreSQL. Valkey errors are swallowed — the
    service degrades gracefully to DB-only reads rather than failing requests.
    valkey is typed as Any because redis-py lacks full generic annotations.
    """
    key = _cache_key(tenant_id)

    try:
        cached: str | None = await valkey.get(key)
        if cached is not None:
            return cast(FeatureFlagsDict, json.loads(cached))
    except Exception:
        pass  # Valkey unavailable — fall through to DB

    flags = await get_feature_flags_from_db(tenant_id, db)

    try:
        await valkey.set(key, json.dumps(flags), ex=VALKEY_FLAG_TTL)
    except Exception:
        pass  # Best-effort cache write — never fail the request

    return flags
