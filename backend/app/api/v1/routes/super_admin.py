from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.db.valkey import get_valkey
from app.models.feature_flags import TenantFeatureFlags
from app.models.tenant import Tenant
from app.schemas.common import DataResponse
from app.schemas.feature_flags import FeatureFlagsResponse
from app.schemas.tenant import (
    PlatformStatsResponse,
    TenantCreateRequest,
    TenantResponse,
)
from app.services.tenant_provision_service import provision_tenant
from app.repositories.feature_flags import get_feature_flags_from_db


class TenantUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    is_active: bool | None = None


class FeatureFlagsUpdateRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    waiter_mode: bool | None = None
    suggestion_engine: bool | None = None
    telegram_alerts: bool | None = None
    gst_module: bool | None = None
    payroll_rewards: bool | None = None
    discount_complimentary: bool | None = None
    waiter_transfer: bool | None = None
    bill_close_ux: bool | None = None

router = APIRouter(prefix="/super-admin", tags=["super-admin"])


@router.post("/tenants", status_code=201, response_model=DataResponse[TenantResponse])
async def create_tenant(
    body: TenantCreateRequest,
    current_user: CurrentUser = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[TenantResponse]:
    """Provision a new tenant with isolated data environment."""
    tenant = await provision_tenant(body, db, current_user["user_id"])
    return DataResponse(data=TenantResponse.model_validate(tenant))


@router.get("/stats", response_model=DataResponse[PlatformStatsResponse])
async def get_platform_stats(
    current_user: CurrentUser = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[PlatformStatsResponse]:
    """Aggregate platform analytics. Never exposes per-tenant data (FR58)."""
    result = await db.execute(
        select(func.count()).select_from(Tenant).where(Tenant.is_active.is_(True))
    )
    total_tenants: int = result.scalar_one()
    return DataResponse(
        data=PlatformStatsResponse(
            total_tenants=total_tenants,
            total_bills_processed=0,  # Bills table added in Epic 4
        )
    )


async def _get_tenant_or_404(slug: str, db: AsyncSession) -> Tenant:
    result = await db.execute(select(Tenant).where(Tenant.slug == slug))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": f"Tenant '{slug}' not found"},
        )
    return tenant


@router.patch("/tenants/{slug}", response_model=DataResponse[TenantResponse])
async def update_tenant(
    slug: str,
    body: TenantUpdateRequest,
    current_user: CurrentUser = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[TenantResponse]:
    """Update tenant name or active status."""
    tenant = await _get_tenant_or_404(slug, db)
    if body.name is not None:
        tenant.name = body.name
    if body.is_active is not None:
        tenant.is_active = body.is_active
    await db.commit()
    await db.refresh(tenant)
    return DataResponse(data=TenantResponse.model_validate(tenant))


@router.delete("/tenants/{slug}", status_code=204)
async def delete_tenant(
    slug: str,
    current_user: CurrentUser = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Permanently delete a tenant and all associated data."""
    tenant = await _get_tenant_or_404(slug, db)
    await db.delete(tenant)
    await db.commit()


@router.get("/tenants/{slug}/features", response_model=DataResponse[FeatureFlagsResponse])
async def get_tenant_features(
    slug: str,
    current_user: CurrentUser = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[FeatureFlagsResponse]:
    """Get feature flags for a tenant by slug."""
    tenant = await _get_tenant_or_404(slug, db)
    flags = await get_feature_flags_from_db(tenant.id, db)
    return DataResponse(data=FeatureFlagsResponse(**flags))


@router.patch("/tenants/{slug}/features", response_model=DataResponse[FeatureFlagsResponse])
async def update_tenant_features(
    slug: str,
    body: FeatureFlagsUpdateRequest,
    current_user: CurrentUser = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
    valkey=Depends(get_valkey),
) -> DataResponse[FeatureFlagsResponse]:
    """Update feature flags for a tenant. Creates the row if it doesn't exist."""
    tenant = await _get_tenant_or_404(slug, db)

    result = await db.execute(
        select(TenantFeatureFlags).where(TenantFeatureFlags.tenant_id == tenant.id)
    )
    row = result.scalar_one_or_none()
    if row is None:
        row = TenantFeatureFlags(tenant_id=tenant.id)
        db.add(row)

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(row, field, value)

    await db.commit()
    await db.refresh(row)

    # Invalidate Valkey cache so new flags take effect immediately
    try:
        await valkey.delete(f"feature_flags:{tenant.id}")
    except Exception:
        pass

    updated_flags = await get_feature_flags_from_db(tenant.id, db)
    return DataResponse(data=FeatureFlagsResponse(**updated_flags))
