from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.models.tenant import Tenant
from app.models.user import TenantUser
from app.schemas.auth import StaffPublicItem, TenantPublicInfo
from app.schemas.common import DataResponse

router = APIRouter()

_PIN_ROLES = frozenset({UserRole.BILLER, UserRole.WAITER, UserRole.KITCHEN_STAFF, UserRole.MANAGER})


@router.get("/tenant/{slug}", response_model=DataResponse[TenantPublicInfo])
async def get_tenant_info(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> DataResponse[TenantPublicInfo]:
    """Public endpoint — verify tenant code and return basic tenant info."""
    result = await db.execute(
        select(Tenant).where(Tenant.slug == slug, Tenant.is_active.is_(True))
    )
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "TENANT_NOT_FOUND", "message": "Invalid tenant code"},
        )
    return DataResponse(
        data=TenantPublicInfo(
            id=str(tenant.id),
            name=tenant.name,
            slug=tenant.slug,
            pwa_settings=tenant.pwa_settings,
            logo_path=tenant.logo_path,
        )
    )


@router.get("/tenant/{slug}/staff", response_model=DataResponse[list[StaffPublicItem]])
async def get_tenant_staff(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> DataResponse[list[StaffPublicItem]]:
    """Public endpoint — return active PIN-role staff for tenant login picker."""
    tenant_result = await db.execute(
        select(Tenant).where(Tenant.slug == slug, Tenant.is_active.is_(True))
    )
    tenant = tenant_result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "TENANT_NOT_FOUND", "message": "Invalid tenant code"},
        )
    staff_result = await db.execute(
        select(TenantUser).where(
            TenantUser.tenant_id == tenant.slug,
            TenantUser.is_active.is_(True),
            TenantUser.role.in_([r.value for r in _PIN_ROLES]),
        )
    )
    staff = [
        StaffPublicItem(id=str(u.id), name=u.name, role=u.role.value)
        for u in staff_result.scalars()
    ]
    return DataResponse(data=staff)
