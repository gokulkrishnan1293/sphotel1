from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routes.auth_helpers import _ADMIN_ROLES
from app.core.security.pin import verify_pin
from app.core.security.totp import generate_totp_secret, get_provisioning_uri
from app.db.session import get_db
from app.models.user import TenantUser
from app.schemas.auth import TotpSetupRequest, TotpSetupResponse

router = APIRouter()


@router.post("/totp/setup", response_model=TotpSetupResponse)
async def totp_setup(
    body: TotpSetupRequest,
    db: AsyncSession = Depends(get_db),
) -> TotpSetupResponse:
    """Bootstrap TOTP enrollment for Admin/Super-Admin before first login."""
    result = await db.execute(
        select(TenantUser).where(func.lower(TenantUser.email) == body.email.lower())
    )
    user = result.scalar_one_or_none()

    if user is None or not user.is_active or user.password_hash is None:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Invalid credentials"},
        )

    if user.role not in _ADMIN_ROLES:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ROLE_NOT_ALLOWED",
                "message": "TOTP setup only available for admin accounts",
            },
        )

    if not verify_pin(body.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Invalid credentials"},
        )

    if user.totp_secret is not None:
        secret = user.totp_secret
    else:
        secret = generate_totp_secret()
        await db.execute(
            update(TenantUser).where(TenantUser.id == user.id).values(totp_secret=secret)
        )
        await db.commit()

    assert user.email is not None
    return TotpSetupResponse(
        provisioning_uri=get_provisioning_uri(secret, user.email),
        secret=secret,
    )
