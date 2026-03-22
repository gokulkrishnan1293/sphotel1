import os
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.db.valkey import get_valkey
from app.models.menu import MenuItem
from app.models.tenant import Tenant
from app.models.user import TenantUser
from app.schemas.common import DataResponse
from app.schemas.feature_flags import FeatureFlagsResponse
from app.schemas.print_template import PrintTemplateConfig, PrintTemplateUpdate
from app.schemas.tenant import (
    BrandingUpdateRequest,
    ChecklistItem,
    OnboardingStatusResponse,
    TenantResponse,
)
from app.services.feature_flags import get_feature_flags

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("", response_model=DataResponse[list[TenantResponse]])
async def list_tenants(
    current_user: CurrentUser = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[list[TenantResponse]]:
    """List all tenants — super_admin only."""
    result = await db.execute(select(Tenant).order_by(Tenant.name))
    tenants = result.scalars().all()
    return DataResponse(data=[TenantResponse.model_validate(t) for t in tenants])

# Checklist items in the onboarding order (FR60).
# completed=False for items whose tables don't exist yet in this story.
# Staff PINs is the only dynamically-computed item in Story 3.2.
_STATIC_ITEMS: list[tuple[str, str, str]] = [
    ("menu_items", "Add menu items", "/admin/menu"),
    ("tables", "Configure tables", "/admin/tables"),
    ("gst_rates", "Set GST rates", "/admin/gst"),
    ("print_template", "Configure print template", "/admin/print-settings"),
    ("print_agent", "Register print agent", "/admin/print-agent"),
    ("staff_pins", "Add staff PINs", "/admin/staff"),
    ("telegram", "Configure Telegram notifications", "/admin/telegram"),
]

_OPERATIONAL_ROLES = [
    UserRole.BILLER,
    UserRole.WAITER,
    UserRole.KITCHEN_STAFF,
    UserRole.MANAGER,
]


async def _compute_checklist(
    tenant_id_str: str, db: AsyncSession
) -> list[ChecklistItem]:
    """Build the onboarding checklist with dynamic completion checks."""
    staff_result = await db.execute(
        select(func.count())
        .select_from(TenantUser)
        .where(
            TenantUser.tenant_id == tenant_id_str,
            TenantUser.role.in_(_OPERATIONAL_ROLES),
            TenantUser.pin_hash.is_not(None),
            TenantUser.is_active.is_(True),
        )
    )
    staff_count: int = staff_result.scalar_one()

    menu_result = await db.execute(
        select(func.count())
        .select_from(MenuItem)
        .where(
            MenuItem.tenant_id == tenant_id_str,
            MenuItem.is_available.is_(True),
        )
    )
    menu_count: int = menu_result.scalar_one()

    _dynamic: dict[str, bool] = {
        "staff_pins": staff_count > 0,
        "menu_items": menu_count > 0,
    }

    items: list[ChecklistItem] = []
    for key, label, route in _STATIC_ITEMS:
        items.append(
            ChecklistItem(
                key=key,
                label=label,
                completed=_dynamic.get(key, False),
                route=route,
            )
        )
    return items


@router.get("/me/onboarding", response_model=DataResponse[OnboardingStatusResponse])
async def get_onboarding_status(
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[OnboardingStatusResponse]:
    """Return onboarding checklist for the authenticated Admin's tenant."""
    tenant_slug = current_user["tenant_id"]
    result = await db.execute(select(Tenant).where(Tenant.slug == tenant_slug))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "Tenant not found"},
        )
    items = await _compute_checklist(tenant_slug, db)
    return DataResponse(
        data=OnboardingStatusResponse(
            completed=tenant.onboarding_completed, items=items
        )
    )


@router.post(
    "/me/onboarding/complete", response_model=DataResponse[TenantResponse]
)
async def complete_onboarding(
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[TenantResponse]:
    """Mark onboarding as complete for the authenticated Admin's tenant."""
    result = await db.execute(
        select(Tenant).where(Tenant.slug == current_user["tenant_id"])
    )
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "Tenant not found"},
        )
    tenant.onboarding_completed = True
    await db.commit()
    await db.refresh(tenant)
    return DataResponse(data=TenantResponse.model_validate(tenant))


@router.get("/me/print-template", response_model=DataResponse[PrintTemplateConfig])
async def get_print_template(
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[PrintTemplateConfig]:
    """Return the current print template for the authenticated Admin's tenant."""
    result = await db.execute(select(Tenant).where(Tenant.slug == current_user["tenant_id"]))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Tenant not found"})
    template = PrintTemplateConfig(**(tenant.print_template or {}))
    return DataResponse(data=template)


@router.patch("/me/print-template", response_model=DataResponse[PrintTemplateConfig])
async def update_print_template(
    body: PrintTemplateUpdate,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[PrintTemplateConfig]:
    """Update the print template for the authenticated Admin's tenant."""
    result = await db.execute(select(Tenant).where(Tenant.slug == current_user["tenant_id"]))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Tenant not found"})
    current = PrintTemplateConfig(**(tenant.print_template or {}))
    updated = current.model_copy(update=body.model_dump(exclude_none=True))
    tenant.print_template = updated.model_dump()
    await db.commit()
    await db.refresh(tenant)
    return DataResponse(data=updated)


@router.get("/{tenant_slug}/features", response_model=DataResponse[FeatureFlagsResponse])
async def get_tenant_features(
    tenant_slug: str,
    db: AsyncSession = Depends(get_db),
    valkey: Any = Depends(get_valkey),
) -> DataResponse[FeatureFlagsResponse]:
    """Return feature flags for a tenant identified by slug.

    Resolves slug → UUID, then serves flags from Valkey (60s TTL) with DB fallback.
    Unknown slugs return all-false defaults.
    """
    result = await db.execute(select(Tenant).where(Tenant.slug == tenant_slug))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        return DataResponse(data=FeatureFlagsResponse())
    flags = await get_feature_flags(tenant.id, db, valkey)
    return DataResponse(data=FeatureFlagsResponse(**flags))
@router.get("/me/branding", response_model=DataResponse[TenantResponse])
async def get_branding(
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[TenantResponse]:
    """Return branding/PWA settings for the authenticated Admin's tenant."""
    result = await db.execute(select(Tenant).where(Tenant.slug == current_user["tenant_id"]))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Tenant not found"})
    return DataResponse(data=TenantResponse.model_validate(tenant))


@router.patch("/me/branding", response_model=DataResponse[TenantResponse])
async def update_branding(
    body: BrandingUpdateRequest,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[TenantResponse]:
    """Update branding/PWA settings for the authenticated Admin's tenant."""
    result = await db.execute(select(Tenant).where(Tenant.slug == current_user["tenant_id"]))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Tenant not found"})
    
    if body.pwa_settings:
        current_pwa = tenant.pwa_settings or {}
        updated_pwa = {**current_pwa, **body.pwa_settings.model_dump(exclude_none=True)}
        tenant.pwa_settings = updated_pwa
        
    await db.commit()
    await db.refresh(tenant)
    return DataResponse(data=TenantResponse.model_validate(tenant))


from app.core.storage import storage

@router.post("/me/logo", response_model=DataResponse[TenantResponse])
async def upload_logo(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[TenantResponse]:
    """Upload a custom logo for the tenant to Cloudflare R2."""
    try:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        tenant_slug = current_user["tenant_id"]
        result = await db.execute(select(Tenant).where(Tenant.slug == tenant_slug))
        tenant = result.scalar_one_or_none()
        if tenant is None:
            raise HTTPException(status_code=404, detail="Tenant not found")

        # Upload to R2
        file_ext = os.path.splitext(file.filename or "")[1] or ".png"
        key = f"logos/{str(tenant.id)}{file_ext}"
        
        logo_url = await storage.upload_file(file, key)

        tenant.logo_path = logo_url
        await db.commit()
        await db.refresh(tenant)
        return DataResponse(data=TenantResponse.model_validate(tenant))
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"ERROR: Logo upload failed to R2: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload logo to cloud storage")
