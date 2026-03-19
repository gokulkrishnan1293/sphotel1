from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routes.auth_helpers import (
    _ADMIN_ROLES,
    check_lockout,
    issue_admin_cookie,
    record_failed_attempt,
    resolve_tenant,
)
from app.core.security.permissions import UserRole
from app.core.security.pin import verify_pin
from app.core.security.rate_limiter import limiter
from app.core.security.totp import verify_totp
from app.db.session import get_db
from app.db.valkey import get_valkey
from app.models.audit_log import AuditLog
from app.models.user import TenantUser
from app.schemas.auth import AdminLoginRequest, LoginResponse

router = APIRouter()


@router.post("/admin", response_model=LoginResponse)
@limiter.limit("5/minute")
async def admin_login(
    request: Request,
    body: AdminLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    valkey: Any = Depends(get_valkey),
) -> LoginResponse:
    """Authenticate Admin/Super-Admin with email + password + TOTP."""
    result = await db.execute(
        select(TenantUser).where(func.lower(TenantUser.email) == body.email.lower())
    )
    user = result.scalar_one_or_none()

    if (
        user is None or not user.is_active
        or user.password_hash is None or user.totp_secret is None
    ):
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Invalid credentials"},
        )

    if user.role not in _ADMIN_ROLES:
        raise HTTPException(
            status_code=403,
            detail={"code": "ROLE_NOT_ALLOWED", "message": "Use PIN login for operational accounts"},
        )

    if body.tenant_slug is not None:
        tenant = await resolve_tenant(body.tenant_slug, db)
        if str(user.tenant_id) != str(tenant.slug) or user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=401,
                detail={"code": "UNAUTHORIZED", "message": "Invalid credentials"},
            )
    elif user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403,
            detail={"code": "ROLE_NOT_ALLOWED", "message": "Provide tenant code for admin login"},
        )

    await check_lockout(user.id, valkey)

    password_ok = verify_pin(body.password, user.password_hash)
    totp_ok = verify_totp(user.totp_secret, body.totp_code)
    if not password_ok or not totp_ok:
        await record_failed_attempt(user.id, valkey)
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Invalid credentials"},
        )

    await valkey.delete(f"auth_attempts:{user.id}")

    if user.role == UserRole.SUPER_ADMIN:
        ip = request.client.host if request.client else "unknown"
        db.add(AuditLog(
            tenant_id=user.tenant_id,
            actor_id=user.id,
            action="super_admin_login",
            payload={"ip": ip},
        ))
        await db.commit()

    issue_admin_cookie(response, user.id, user.tenant_id, user.role)
    return LoginResponse(message="Login successful")
