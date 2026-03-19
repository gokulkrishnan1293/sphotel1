from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routes.auth_helpers import (
    _PIN_ROLES,
    check_lockout,
    issue_pin_cookie,
    record_failed_attempt,
    resolve_tenant,
)
from app.core.security.pin import verify_pin
from app.core.security.rate_limiter import limiter
from app.db.session import get_db
from app.db.valkey import get_valkey
from app.models.user import TenantUser
from app.schemas.auth import LoginResponse, PinLoginRequest

router = APIRouter()


@router.post("/pin", response_model=LoginResponse)
@limiter.limit("5/minute")
async def pin_login(
    request: Request,
    body: PinLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    valkey: Any = Depends(get_valkey),
) -> LoginResponse:
    """Authenticate operational staff with PIN. Sets httpOnly JWT cookie."""
    tenant = await resolve_tenant(body.tenant_slug, db)
    result = await db.execute(
        select(TenantUser).where(
            TenantUser.id == body.user_id,
            TenantUser.tenant_id == tenant.slug,
        )
    )
    user = result.scalar_one_or_none()

    if user is None or not user.is_active or user.pin_hash is None:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Invalid credentials"},
        )

    if user.role not in _PIN_ROLES:
        raise HTTPException(
            status_code=403,
            detail={"code": "ROLE_NOT_ALLOWED", "message": "Use email login for admin accounts"},
        )

    await check_lockout(user.id, valkey)

    if not verify_pin(body.pin, user.pin_hash):
        await record_failed_attempt(user.id, valkey)
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Invalid credentials"},
        )

    await valkey.delete(f"auth_attempts:{user.id}")
    issue_pin_cookie(response, user.id, user.tenant_id, user.role)
    return LoginResponse(message="Login successful")
