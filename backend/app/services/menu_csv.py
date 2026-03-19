"""CSV export/import for menu items."""
import csv
import io
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.menu import MenuItem
from app.schemas.menu import MenuItemCreate, MenuItemUpdate

VENDOR_SLUGS = ["swiggy", "zomato", "flyer_eats"]
_BASE = ["short_code", "name", "category", "variation", "food_type", "available", "base_price", "parcel_price"]
CSV_COLS = _BASE + VENDOR_SLUGS


def export_csv(items: Sequence[MenuItem]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CSV_COLS)
    w.writeheader()
    for item in items:
        vp = {v.vendor_slug: v.price_paise // 100 for v in item.vendor_prices}
        base: dict = {
            "short_code": item.short_code or "", "name": item.name, "category": item.category,
            "variation": "", "food_type": item.food_type.value,
            "available": "yes" if item.is_available else "no",
            "base_price": item.price_paise // 100,
            "parcel_price": (item.parcel_price_paise or 0) // 100 or "",
            **{s: vp.get(s, "") for s in VENDOR_SLUGS},
        }
        w.writerow(base)
        for v in item.variants:
            vvp = {vp2.vendor_slug: vp2.price_paise // 100 for vp2 in v.vendor_prices}
            w.writerow({**base, "variation": v.name, "base_price": v.price_paise // 100,
                        "parcel_price": (v.parcel_price_paise or 0) // 100 or "",
                        **{s: vvp.get(s, "") for s in VENDOR_SLUGS}})
    return buf.getvalue()


def _paise(v: str) -> int | None:
    return int(float(v) * 100) if v.strip() else None


async def import_csv(db: AsyncSession, tenant_id: str, content: str) -> dict:
    from sqlalchemy import delete
    from app.services.menu_service import create_menu_item
    reader = csv.DictReader(io.StringIO(content))
    groups: dict[str, dict] = {}
    for row in reader:
        sc = row.get("short_code", "").strip()
        key = sc or row["name"].strip()
        if key not in groups:
            groups[key] = {"row": row, "variants": []}
        if row.get("variation", "").strip():
            groups[key]["variants"].append(row)
        else:
            groups[key]["row"] = row

    await db.execute(delete(MenuItem).where(MenuItem.tenant_id == tenant_id))

    created = 0
    errors: list[str] = []
    for key, group in groups.items():
        row = group["row"]
        try:
            sc_val = int(row["short_code"]) if row.get("short_code", "").strip() else None
            vps = [{"vendor_slug": s, "price_paise": int(float(row[s]) * 100)} for s in VENDOR_SLUGS if row.get(s, "").strip()]
            variants_data = [
                {"name": vr["variation"].strip(), "price_paise": _paise(vr.get("base_price", "0")) or 0,
                 "parcel_price_paise": _paise(vr.get("parcel_price", "")),
                 "vendor_prices": [{"vendor_slug": s, "price_paise": int(float(vr[s]) * 100)} for s in VENDOR_SLUGS if vr.get(s, "").strip()]}
                for vr in group["variants"]
            ]
            payload = MenuItemCreate(
                name=row["name"].strip(), category=row["category"].strip(), short_code=sc_val,
                price_paise=_paise(row.get("base_price", "0")) or 0,
                parcel_price_paise=_paise(row.get("parcel_price", "")),
                food_type=row.get("food_type", "veg").strip() or "veg",
                is_available=row.get("available", "yes").strip().lower() != "no",
                vendor_prices=vps, variants=variants_data,
            )
            await create_menu_item(db, tenant_id, payload)
            created += 1
        except Exception as e:
            errors.append(f"Row '{key}': {e}")
    return {"created": created, "errors": errors}
