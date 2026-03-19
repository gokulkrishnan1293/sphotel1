import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.core.security.pin import hash_pin
from app.db.session import get_db
from app.db.valkey import get_valkey
from app.models.audit_log import AuditLog
from app.models.user import TenantUser
from app.schemas.auth import AdminResetRequest, MeResponse
from app.schemas.common import DataResponse

router = APIRouter()


@router.post("/admin-reset/{target_id}", response_model=DataResponse[MeResponse])
async def admin_reset_credentials(
    target_id: uuid.UUID,
    body: AdminResetRequest,
    current_user: CurrentUser = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
    valkey: Any = Depends(get_valkey),
) -> DataResponse[MeResponse]:
    """Super-Admin reset of any Admin's credentials + account unlock."""
    result = await db.execute(
        select(TenantUser).where(
            TenantUser.id == target_id,
            TenantUser.tenant_id == current_user["tenant_id"],
        )
    )
    target = result.scalar_one_or_none()
    if target is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "Admin not found"},
        )
    if target.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail={"code": "ROLE_NOT_ALLOWED", "message": "Can only reset credentials for Admin accounts"},
        )

    updates: dict[str, object] = {}
    if body.email is not None:
        dupe = await db.execute(
            select(TenantUser).where(
                func.lower(TenantUser.email) == body.email.lower(),
                TenantUser.id != target_id,
            )
        )
        if dupe.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=409,
                detail={"code": "EMAIL_TAKEN", "message": "Email already in use"},
            )
        updates["email"] = body.email.lower()

    if body.password is not None:
        updates["password_hash"] = hash_pin(body.password)

    await db.execute(update(TenantUser).where(TenantUser.id == target_id).values(**updates))
    await valkey.delete(f"auth_locked:{target_id}")
    await valkey.delete(f"session_revoked:{target_id}")

    db.add(AuditLog(
        tenant_id=current_user["tenant_id"],
        actor_id=current_user["user_id"],
        action="admin_credentials_reset",
        target_id=target_id,
        payload={"changed": list(updates.keys())},
    ))
    await db.commit()

    result2 = await db.execute(select(TenantUser).where(TenantUser.id == target_id))
    user = result2.scalar_one()
    return DataResponse(data=MeResponse.model_validate(user))
