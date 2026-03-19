"""Import menu items from CSV with variant support."""
import asyncio
import csv
import os
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.menu import MenuItem

FOOD_MAP = {"non-veg": "non_veg", "veg": "veg", "egg": "egg"}


def parse_variants(row: list[str]) -> list[dict] | None:
    variants = []
    for name_col, price_col in [(22, 23), (26, 27), (30, 31)]:
        if name_col >= len(row):
            break
        v_name = row[name_col].strip()
        v_price_str = row[price_col].strip() if price_col < len(row) else ""
        if v_name and v_price_str:
            try:
                variants.append({"name": v_name, "price_paise": int(float(v_price_str) * 100)})
            except ValueError:
                pass
    return variants if variants else None


async def import_menu(csv_path: str, tenant_slug: str) -> None:
    db_url = os.environ["DATABASE_URL"]
    engine = create_async_engine(db_url, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    async with AsyncSessionLocal() as session:
        for raw in rows:
            if not raw or not raw[0].strip():
                continue
            name = raw[0].strip()
            # CSV cols: 0=Name, 3=Short_Code, 7=Category, 9=Price, 10=Attributes(food_type)
            try:
                short_code = int(raw[3].strip()) if len(raw) > 3 and raw[3].strip().isdigit() else None
            except ValueError:
                short_code = None
            category = raw[7].strip() if len(raw) > 7 and raw[7].strip() else "General"
            try:
                price_paise = int(float(raw[9].strip()) * 100) if len(raw) > 9 and raw[9].strip() else 0
            except ValueError:
                price_paise = 0
            raw_ft = raw[10].strip().lower() if len(raw) > 10 else "veg"
            food_type = FOOD_MAP.get(raw_ft, "veg")
            variants = parse_variants(raw)

            existing = None
            if short_code:
                res = await session.execute(
                    select(MenuItem).where(
                        MenuItem.tenant_id == tenant_slug,
                        MenuItem.short_code == short_code,
                    )
                )
                existing = res.scalar_one_or_none()

            if existing:
                existing.name = name
                existing.price_paise = price_paise
                existing.variants = variants
                existing.is_available = True
            else:
                session.add(MenuItem(
                    tenant_id=tenant_slug, name=name, short_code=short_code,
                    category=category, price_paise=price_paise,
                    food_type=food_type, variants=variants, is_available=True,
                ))

        await session.commit()
    await engine.dispose()
    print(f"Imported {len(rows)} rows into tenant '{tenant_slug}'.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/import_menu.py <csv_path> <tenant_slug>")
        sys.exit(1)
    asyncio.run(import_menu(sys.argv[1], sys.argv[2]))
