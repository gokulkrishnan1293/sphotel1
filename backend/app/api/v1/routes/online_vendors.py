"""Online vendor management — per-tenant list of delivery platforms."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.models.tenant import Tenant
from app.schemas.common import DataResponse

router = APIRouter(prefix="/tenants/me/online-vendors", tags=["tenants"])
_ADMIN = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)


class VendorItem(BaseModel):
    slug: str   # e.g. "swiggy"
    name: str   # e.g. "Swiggy"


async def _tenant(cu: CurrentUser, db: AsyncSession) -> Tenant:
    r = await db.execute(select(Tenant).where(Tenant.slug == cu["tenant_id"]))
    t = r.scalar_one_or_none()
    if not t:
        raise HTTPException(404, "Tenant not found")
    return t


@router.get("", response_model=DataResponse[list[VendorItem]])
async def list_vendors(
    cu: CurrentUser = Depends(_ADMIN), db: AsyncSession = Depends(get_db)
) -> DataResponse[list[VendorItem]]:
    t = await _tenant(cu, db)
    return DataResponse(data=[VendorItem(**v) for v in (t.online_vendors or [])])


@router.post("", response_model=DataResponse[list[VendorItem]], status_code=201)
async def add_vendor(
    body: VendorItem,
    cu: CurrentUser = Depends(_ADMIN),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[list[VendorItem]]:
    t = await _tenant(cu, db)
    vendors = list(t.online_vendors or [])
    if any(v["slug"] == body.slug for v in vendors):
        raise HTTPException(409, "Vendor slug already exists")
    vendors.append(body.model_dump())
    t.online_vendors = vendors
    await db.commit()
    return DataResponse(data=[VendorItem(**v) for v in vendors])


@router.delete("/{slug}", status_code=204)
async def remove_vendor(
    slug: str,
    cu: CurrentUser = Depends(_ADMIN),
    db: AsyncSession = Depends(get_db),
) -> None:
    t = await _tenant(cu, db)
    t.online_vendors = [v for v in (t.online_vendors or []) if v["slug"] != slug]
    await db.commit()
