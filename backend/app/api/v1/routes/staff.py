import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole, can_assign_role
from app.core.security.pin import hash_pin
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import TenantUser
from app.schemas.common import DataResponse
from app.schemas.staff import CreateStaffRequest, StaffResponse, WaiterView

router = APIRouter(prefix="/staff", tags=["staff"])


def _check_can_manage(actor_role: UserRole, target_role: UserRole) -> None:
    """Raise 403 if actor cannot manage a user with target_role (FR87)."""
    if not can_assign_role(actor_role, target_role):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ROLE_HIERARCHY_VIOLATION",
                "message": "Cannot manage staff at or above your own role level",
            },
        )


@router.get("", response_model=DataResponse[list[StaffResponse]])
async def list_staff(
    current_user: CurrentUser = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[list[StaffResponse]]:
    """Return all staff (active and inactive) in the caller's tenant."""
    result = await db.execute(
        select(TenantUser).where(TenantUser.tenant_id == current_user["tenant_id"])
    )
    users = result.scalars().all()
    return DataResponse(data=[StaffResponse.model_validate(u) for u in users])


@router.post("", response_model=DataResponse[StaffResponse], status_code=201)
async def create_staff(
    body: CreateStaffRequest,
    current_user: CurrentUser = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[StaffResponse]:
    """Create a new staff member with a bcrypt-hashed PIN."""
    _check_can_manage(current_user["role"], body.role)
    new_user = TenantUser(
        tenant_id=current_user["tenant_id"],
        name=body.name,
        role=body.role,
        pin_hash=hash_pin(body.pin),
        short_code=body.short_code,
    )
    db.add(new_user)
    await db.flush()
    db.add(AuditLog(
        tenant_id=current_user["tenant_id"],
        actor_id=current_user["user_id"],
        action="staff_create",
        target_id=new_user.id,
        payload={"role": str(body.role), "name": body.name},
    ))
    await db.commit()
    await db.refresh(new_user)
    return DataResponse(data=StaffResponse.model_validate(new_user))


@router.get("/waiters", response_model=DataResponse[list[WaiterView]])
async def list_waiters(
    current_user: CurrentUser = Depends(
        require_role(UserRole.BILLER, UserRole.WAITER, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[list[WaiterView]]:
    """Return active waiters — accessible to billing staff for waiter assignment."""
    result = await db.execute(
        select(TenantUser).where(
            TenantUser.tenant_id == current_user["tenant_id"],
            TenantUser.role == UserRole.WAITER,
            TenantUser.is_active.is_(True),
        )
    )
    return DataResponse(data=[WaiterView.model_validate(u) for u in result.scalars().all()])
