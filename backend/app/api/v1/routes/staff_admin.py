from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.core.security.pin import hash_pin
from app.core.security.totp import generate_totp_secret, get_provisioning_uri
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.tenant import Tenant
from app.models.user import TenantUser
from app.schemas.common import DataResponse
from app.schemas.staff import AdminCreatedResponse, CreateAdminRequest, StaffResponse

router = APIRouter(prefix="/staff", tags=["staff"])


@router.post("/admin", response_model=DataResponse[AdminCreatedResponse], status_code=201)
async def create_admin(
    body: CreateAdminRequest,
    current_user: CurrentUser = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[AdminCreatedResponse]:
    """Super-admin creates a new tenant admin with email + password + TOTP enrollment."""
    tenant_row = await db.execute(select(Tenant).where(Tenant.slug == body.tenant_slug))
    tenant = tenant_row.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "TENANT_NOT_FOUND", "message": "Tenant not found"},
        )

    dupe = await db.execute(
        select(TenantUser).where(func.lower(TenantUser.email) == body.email.lower())
    )
    if dupe.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=409,
            detail={"code": "EMAIL_TAKEN", "message": "Email already in use"},
        )

    totp_secret = generate_totp_secret()
    admin = TenantUser(
        tenant_id=body.tenant_slug,
        name=body.name,
        role=UserRole.ADMIN,
        email=body.email.lower(),
        password_hash=hash_pin(body.password),
        totp_secret=totp_secret,
        is_active=True,
    )
    db.add(admin)
    await db.flush()
    db.add(AuditLog(
        tenant_id=body.tenant_slug,
        actor_id=current_user["user_id"],
        action="admin_create",
        target_id=admin.id,
        payload={"email": body.email.lower(), "name": body.name},
    ))
    await db.commit()
    await db.refresh(admin)

    totp_uri = get_provisioning_uri(totp_secret, body.email.lower())
    return DataResponse(data=AdminCreatedResponse(
        **StaffResponse.model_validate(admin).model_dump(),
        totp_uri=totp_uri,
    ))
