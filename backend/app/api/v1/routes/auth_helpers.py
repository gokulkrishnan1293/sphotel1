import uuid
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import Response

from app.core.config import settings
from app.core.security.jwt import create_access_token
from app.core.security.permissions import UserRole
from app.models.tenant import Tenant

_COOKIE_MAX_AGE = settings.JWT_EXPIRY_HOURS * 3600
_PIN_ROLES = frozenset({UserRole.BILLER, UserRole.WAITER, UserRole.KITCHEN_STAFF, UserRole.MANAGER})
_ADMIN_ROLES = frozenset({UserRole.ADMIN, UserRole.SUPER_ADMIN})


def issue_pin_cookie(
    response: Response, user_id: uuid.UUID, tenant_id: str, role: UserRole
) -> None:
    token = create_access_token(user_id, tenant_id, role)
    response.set_cookie(
        key="access_token", value=token, httponly=True, samesite="lax",
        secure=settings.ENVIRONMENT != "development",
        max_age=_COOKIE_MAX_AGE, path="/api",
    )


def issue_admin_cookie(
    response: Response, user_id: uuid.UUID, tenant_id: str, role: UserRole
) -> None:
    token = create_access_token(user_id, tenant_id, role)
    response.set_cookie(
        key="access_token", value=token, httponly=True, samesite="strict",
        secure=settings.ENVIRONMENT != "development", path="/api",
    )


async def check_lockout(user_id: uuid.UUID, valkey: Any) -> None:
    if await valkey.exists(f"auth_locked:{user_id}"):
        raise HTTPException(
            status_code=403,
            detail={"code": "ACCOUNT_LOCKED", "message": "Account locked. Contact admin."},
        )


async def record_failed_attempt(user_id: uuid.UUID, valkey: Any) -> None:
    key = f"auth_attempts:{user_id}"
    count = await valkey.incr(key)
    if count == 1:
        await valkey.expire(key, 60)
    if count >= 5:
        await valkey.set(f"auth_locked:{user_id}", "1")


async def resolve_tenant(slug: str, db: AsyncSession) -> Tenant:
    result = await db.execute(
        select(Tenant).where(Tenant.slug == slug, Tenant.is_active.is_(True))
    )
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "TENANT_NOT_FOUND", "message": "Invalid tenant code"},
        )
    return tenant
