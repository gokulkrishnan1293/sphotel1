import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import settings
from app.core.security.permissions import UserRole


def create_access_token(
    user_id: uuid.UUID,
    tenant_id: str,
    role: UserRole,
    expiry_hours: int | None = None,
) -> str:
    """Create a signed JWT for the given user identity."""
    now = datetime.now(UTC)
    hours = expiry_hours if expiry_hours is not None else settings.JWT_EXPIRY_HOURS
    payload: dict[str, object] = {
        "user_id": str(user_id),
        "tenant_id": tenant_id,
        "role": str(role),
        "iat": now,
        "exp": now + timedelta(hours=hours),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, object]:
    """Decode and validate a JWT. Raises jwt.InvalidTokenError on failure."""
    decoded: dict[str, object] = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    return decoded
