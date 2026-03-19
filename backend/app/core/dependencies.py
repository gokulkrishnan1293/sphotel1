import uuid
from collections.abc import Awaitable, Callable
from typing import Any, TypedDict

import jwt
from fastapi import Depends, Header, HTTPException, Request

from app.core.security.jwt import decode_access_token
from app.core.security.permissions import UserRole
from app.db.valkey import get_valkey


class CurrentUser(TypedDict):
    """Authenticated user context injected by require_role() into endpoints."""

    user_id: uuid.UUID
    tenant_id: str  # VARCHAR in DB — TenantMixin uses str, not UUID
    role: UserRole


async def get_current_user(
    request: Request,
    valkey: Any = Depends(get_valkey),
    x_tenant_override: str | None = Header(default=None),
) -> CurrentUser:
    """Extract and validate JWT from httpOnly access_token cookie."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Authentication required"},
        )
    try:
        payload = decode_access_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Authentication required"},
        )

    user_id_str = str(payload["user_id"])

    # Check if admin explicitly revoked all sessions for this user (Story 2.4)
    revoked_at = await valkey.get(f"session_revoked:{user_id_str}")
    if revoked_at is not None:
        token_iat = float(str(payload.get("iat", 0)))
        if float(revoked_at) >= token_iat:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "SESSION_REVOKED",
                    "message": "Session has been revoked. Please log in again.",
                },
            )

    role = UserRole(str(payload["role"]))
    tenant_id = str(payload["tenant_id"])

    # Super-admin can act on any tenant via X-Tenant-Override header
    if role == UserRole.SUPER_ADMIN and x_tenant_override:
        tenant_id = x_tenant_override

    return CurrentUser(
        user_id=uuid.UUID(user_id_str),
        tenant_id=tenant_id,
        role=role,
    )


def require_role(
    *allowed_roles: UserRole,
) -> Callable[..., Awaitable[CurrentUser]]:
    """FastAPI dependency factory for role-based access control.

    Usage:
        @router.get("/protected")
        async def endpoint(
            user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
        ) -> ...

    Raises HTTP 401 when no valid session cookie exists.
    Raises HTTP 403 when the authenticated role is not in allowed_roles.
    """

    async def _check_role(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail={"code": "FORBIDDEN", "message": "Insufficient permissions"},
            )
        return current_user

    return _check_role
