import time
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete as sql_delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole, can_assign_role
from app.core.security.pin import hash_pin
from app.db.session import get_db
from app.db.valkey import get_valkey
from app.models.audit_log import AuditLog
from app.models.user import TenantUser
from app.schemas.common import DataResponse, MessageResponse
from app.schemas.staff import ResetPinRequest, StaffResponse, UpdateStaffRequest

router = APIRouter(prefix="/staff", tags=["staff"])
_ADMIN = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)


async def _get_staff(sid: uuid.UUID, tid: str, db: AsyncSession) -> TenantUser:
    r = await db.execute(
        select(TenantUser).where(TenantUser.id == sid, TenantUser.tenant_id == tid)
    )
    u = r.scalar_one_or_none()
    if u is None:
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "Staff not found"})
    return u

def _check(actor: UserRole, target: UserRole) -> None:
    if not can_assign_role(actor, target):
        raise HTTPException(403, {"code": "ROLE_HIERARCHY_VIOLATION",
                                   "message": "Cannot manage staff at or above your role"})


@router.patch("/{sid}/pin", response_model=DataResponse[StaffResponse])
async def reset_pin(sid: uuid.UUID, body: ResetPinRequest,
    cu: CurrentUser = Depends(_ADMIN), db: AsyncSession = Depends(get_db)) -> DataResponse[StaffResponse]:
    t = await _get_staff(sid, cu["tenant_id"], db)
    _check(cu["role"], t.role)
    await db.execute(update(TenantUser).where(TenantUser.id == sid).values(pin_hash=hash_pin(body.pin)))
    db.add(AuditLog(tenant_id=cu["tenant_id"], actor_id=cu["user_id"], action="pin_reset", target_id=sid))
    await db.commit()
    await db.refresh(t)
    return DataResponse(data=StaffResponse.model_validate(t))


@router.patch("/{sid}/deactivate", response_model=DataResponse[StaffResponse])
async def deactivate_staff(sid: uuid.UUID,
    cu: CurrentUser = Depends(_ADMIN), db: AsyncSession = Depends(get_db),
    valkey: Any = Depends(get_valkey)) -> DataResponse[StaffResponse]:
    t = await _get_staff(sid, cu["tenant_id"], db)
    _check(cu["role"], t.role)
    await db.execute(update(TenantUser).where(TenantUser.id == sid).values(is_active=False))
    await valkey.set(f"auth_locked:{sid}", "1")
    db.add(AuditLog(tenant_id=cu["tenant_id"], actor_id=cu["user_id"], action="staff_deactivate", target_id=sid))
    await db.commit()
    await db.refresh(t)
    return DataResponse(data=StaffResponse.model_validate(t))


@router.delete("/{sid}/sessions", response_model=DataResponse[MessageResponse])
async def revoke_sessions(sid: uuid.UUID,
    cu: CurrentUser = Depends(_ADMIN), db: AsyncSession = Depends(get_db),
    valkey: Any = Depends(get_valkey)) -> DataResponse[MessageResponse]:
    t = await _get_staff(sid, cu["tenant_id"], db)
    _check(cu["role"], t.role)
    await valkey.set(f"session_revoked:{sid}", str(time.time()), ex=settings.JWT_EXPIRY_HOURS * 3600)
    await valkey.set(f"auth_locked:{sid}", "1")
    db.add(AuditLog(tenant_id=cu["tenant_id"], actor_id=cu["user_id"], action="sessions_revoke", target_id=sid))
    await db.commit()
    return DataResponse(data=MessageResponse(message="Sessions revoked"))


@router.patch("/{sid}", response_model=DataResponse[StaffResponse])
async def update_staff(sid: uuid.UUID, body: UpdateStaffRequest,
    cu: CurrentUser = Depends(_ADMIN), db: AsyncSession = Depends(get_db)) -> DataResponse[StaffResponse]:
    t = await _get_staff(sid, cu["tenant_id"], db)
    _check(cu["role"], t.role)
    updates = body.model_dump(exclude_unset=True)
    if updates:
        await db.execute(update(TenantUser).where(TenantUser.id == sid).values(**updates))
        db.add(AuditLog(tenant_id=cu["tenant_id"], actor_id=cu["user_id"], action="staff_update", target_id=sid, payload=updates))
        await db.commit()
        await db.refresh(t)
    return DataResponse(data=StaffResponse.model_validate(t))


@router.delete("/{sid}", response_model=DataResponse[MessageResponse])
async def delete_staff(sid: uuid.UUID,
    cu: CurrentUser = Depends(_ADMIN), db: AsyncSession = Depends(get_db)) -> DataResponse[MessageResponse]:
    t = await _get_staff(sid, cu["tenant_id"], db)
    _check(cu["role"], t.role)
    await db.execute(sql_delete(TenantUser).where(TenantUser.id == sid))
    db.add(AuditLog(tenant_id=cu["tenant_id"], actor_id=cu["user_id"], action="staff_delete", target_id=sid))
    await db.commit()
    return DataResponse(data=MessageResponse(message="Staff deleted"))
