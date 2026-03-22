import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.menu import MenuItem, MenuItemVariant, MenuItemVendorPrice
from app.schemas.menu import MenuItemCreate, MenuItemResponse, MenuItemUpdate


async def _get(db: AsyncSession, tenant_id: str, item_id: uuid.UUID) -> MenuItem:
    r = await db.execute(select(MenuItem).where(MenuItem.id == item_id, MenuItem.tenant_id == tenant_id))
    item = r.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"MenuItem {item_id} not found")
    return item


def _apply_relations(item: MenuItem, data: MenuItemCreate | MenuItemUpdate) -> None:
    vd = data.model_dump(exclude_unset=True)
    if "variants" in vd and vd["variants"] is not None:
        item.variants = [
            MenuItemVariant(
                tenant_id=item.tenant_id, menu_item_id=item.id,
                name=v["name"], price_paise=v["price_paise"],
                parcel_price_paise=v.get("parcel_price_paise"),
                display_order=i,
                vendor_prices=[
                    MenuItemVendorPrice(tenant_id=item.tenant_id, vendor_slug=vp["vendor_slug"], price_paise=vp["price_paise"])
                    for vp in (v.get("vendor_prices") or [])
                ],
            )
            for i, v in enumerate(vd["variants"])
        ]
    if "vendor_prices" in vd and vd["vendor_prices"] is not None:
        item.vendor_prices = [
            MenuItemVendorPrice(tenant_id=item.tenant_id, menu_item_id=item.id, vendor_slug=vp["vendor_slug"], price_paise=vp["price_paise"])
            for vp in vd["vendor_prices"]
        ]


async def list_menu_items(db: AsyncSession, tenant_id: str) -> Sequence[MenuItem]:
    r = await db.execute(select(MenuItem).where(MenuItem.tenant_id == tenant_id).order_by(MenuItem.display_order, MenuItem.name))
    return r.scalars().all()


async def get_menu_item(db: AsyncSession, tenant_id: str, item_id: uuid.UUID) -> MenuItem:
    return await _get(db, tenant_id, item_id)


async def create_menu_item(db: AsyncSession, tenant_id: str, data: MenuItemCreate) -> MenuItem:
    dump = data.model_dump(exclude={"variants", "vendor_prices"})
    item = MenuItem(tenant_id=tenant_id, **dump)
    item.variants = []
    item.vendor_prices = []
    db.add(item)
    await db.flush()
    _apply_relations(item, data)
    try:
        await db.commit()
        await db.refresh(item)
    except IntegrityError as exc:
        await db.rollback()
        if "uq_menu_items_tenant_short_code" in str(exc.orig):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Short code already used by another item")
        raise
    return item


async def update_menu_item(db: AsyncSession, tenant_id: str, item_id: uuid.UUID, data: MenuItemUpdate) -> MenuItem:
    item = await _get(db, tenant_id, item_id)
    for field, value in data.model_dump(exclude_unset=True, exclude={"variants", "vendor_prices"}).items():
        setattr(item, field, value)
    _apply_relations(item, data)
    try:
        await db.commit()
        await db.refresh(item)
    except IntegrityError as exc:
        await db.rollback()
        if "uq_menu_items_tenant_short_code" in str(exc.orig):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Short code already used by another item")
        raise
    return item


async def delete_menu_item(db: AsyncSession, tenant_id: str, item_id: uuid.UUID) -> None:
    item = await _get(db, tenant_id, item_id)
    await db.delete(item)
    await db.commit()


def apply_vendor_pricing(item: MenuItem, vendor: str | None) -> MenuItemResponse:
    """Build a MenuItemResponse with effective_price_paise resolved for the given vendor context.

    vendor=None      → no override, effective_price_paise stays None (use price_paise)
    vendor="parcel"  → parcel_price_paise if set, otherwise price_paise
    vendor=<slug>    → MenuItemVendorPrice for that slug if set, otherwise price_paise
    """
    resp = MenuItemResponse.model_validate(item)
    if vendor is None:
        return resp

    if vendor == "parcel":
        resp.effective_price_paise = (
            item.parcel_price_paise if item.parcel_price_paise is not None else item.price_paise
        )
        for variant_model, variant_resp in zip(item.variants, resp.variants):
            variant_resp.effective_price_paise = (
                variant_model.parcel_price_paise
                if variant_model.parcel_price_paise is not None
                else variant_model.price_paise
            )
    else:
        item_vp = {vp.vendor_slug: vp.price_paise for vp in item.vendor_prices}
        resp.effective_price_paise = item_vp.get(vendor, item.price_paise)
        for variant_model, variant_resp in zip(item.variants, resp.variants):
            var_vp = {vp.vendor_slug: vp.price_paise for vp in variant_model.vendor_prices}
            variant_resp.effective_price_paise = var_vp.get(vendor, variant_model.price_paise)

    return resp
