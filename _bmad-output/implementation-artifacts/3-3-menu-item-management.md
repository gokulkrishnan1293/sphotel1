# Story 3.3 — Menu Item Management

## Status: review

## Story

**As an** Admin,
**I want to** create, view, edit, and delete menu items with name, category, short code, price, food type, description, and availability,
**So that** staff can reference menu items when billing customers.

## Acceptance Criteria

- AC1: Admin can view all menu items for their tenant in a paginated/scrollable table
- AC2: Admin can create a new menu item (name, category, short_code, price_paise, food_type, description, is_available, display_order)
- AC3: Admin can edit any field of an existing menu item inline or via form
- AC4: Admin can toggle availability of a menu item (is_available flag)
- AC5: Admin can delete a menu item (with confirmation)
- AC6: Short code is optional integer; must be unique per tenant if provided
- AC7: Price stored as integer paise (rupees × 100); displayed as rupees in UI
- AC8: food_type must be one of: veg, egg, non_veg
- AC9: API returns 404 with NOT_FOUND code if item does not belong to tenant
- AC10: Onboarding checklist "menu_configured" key becomes complete when ≥1 active menu item exists for tenant

## Technical Context

### Database Schema

Migration: `0006_create_menu_items.py`

```sql
-- New PG enum
CREATE TYPE food_type AS ENUM ('veg', 'egg', 'non_veg');

-- New table
CREATE TABLE menu_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR NOT NULL REFERENCES tenants(slug) ON DELETE CASCADE,
    name            VARCHAR NOT NULL,
    category        VARCHAR NOT NULL,
    short_code      INTEGER NULL,
    price_paise     INTEGER NOT NULL DEFAULT 0,
    food_type       food_type NOT NULL DEFAULT 'veg',
    description     TEXT NULL,
    is_available    BOOLEAN NOT NULL DEFAULT true,
    display_order   INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_menu_items_tenant_short_code UNIQUE (tenant_id, short_code)
        DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX idx_menu_items_tenant_id ON menu_items(tenant_id);
CREATE INDEX idx_menu_items_tenant_category ON menu_items(tenant_id, category);
```

**Note on UNIQUE constraint**: The UNIQUE constraint on `(tenant_id, short_code)` must exclude NULLs — PostgreSQL NULLs are never equal, so multiple NULLs are allowed automatically. No partial index needed.

### SQLAlchemy Model

File: `backend/app/models/menu.py`

```python
import uuid

from sqlalchemy import UUID, Boolean, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.security.permissions import FoodType
from app.models.base import Base, TenantMixin, TimestampMixin


class MenuItem(Base, TenantMixin, TimestampMixin):
    __tablename__ = "menu_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    short_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_paise: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    food_type: Mapped[FoodType] = mapped_column(
        SAEnum(FoodType, name="food_type", native_enum=True, create_type=False,
               values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        server_default="veg",
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("idx_menu_items_tenant_id", "tenant_id"),
        Index("idx_menu_items_tenant_category", "tenant_id", "category"),
        UniqueConstraint("tenant_id", "short_code", name="uq_menu_items_tenant_short_code",
                         deferrable=True, initially="DEFERRED"),
    )
```

### FoodType Enum

Add to `backend/app/core/security/permissions.py`:

```python
from enum import StrEnum

class FoodType(StrEnum):
    VEG = "veg"
    EGG = "egg"
    NON_VEG = "non_veg"
```

### Pydantic Schemas

File: `backend/app/schemas/menu.py`

```python
import uuid
from typing import Optional
from pydantic import BaseModel, Field

from app.core.security.permissions import FoodType


class MenuItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=100)
    short_code: Optional[int] = Field(None, ge=1, le=9999)
    price_paise: int = Field(0, ge=0)
    food_type: FoodType = FoodType.VEG
    description: Optional[str] = Field(None, max_length=500)
    is_available: bool = True
    display_order: int = 0


class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    short_code: Optional[int] = Field(None, ge=1, le=9999)
    price_paise: Optional[int] = Field(None, ge=0)
    food_type: Optional[FoodType] = None
    description: Optional[str] = Field(None, max_length=500)
    is_available: Optional[bool] = None
    display_order: Optional[int] = None


class MenuItemResponse(BaseModel):
    id: uuid.UUID
    tenant_id: str
    name: str
    category: str
    short_code: Optional[int]
    price_paise: int
    food_type: FoodType
    description: Optional[str]
    is_available: bool
    display_order: int

    model_config = {"from_attributes": True}
```

### Service Layer

File: `backend/app/services/menu_service.py`

```python
import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.menu import MenuItem
from app.schemas.menu import MenuItemCreate, MenuItemUpdate
from app.core.exceptions import NotFoundError, ConflictError


async def list_menu_items(db: AsyncSession, tenant_id: str) -> Sequence[MenuItem]:
    result = await db.execute(
        select(MenuItem)
        .where(MenuItem.tenant_id == tenant_id)
        .order_by(MenuItem.display_order, MenuItem.name)
    )
    return result.scalars().all()


async def create_menu_item(db: AsyncSession, tenant_id: str, data: MenuItemCreate) -> MenuItem:
    item = MenuItem(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    try:
        await db.commit()
        await db.refresh(item)
    except IntegrityError as exc:
        await db.rollback()
        if "uq_menu_items_tenant_short_code" in str(exc.orig):
            raise ConflictError("Short code already used by another item in this tenant")
        raise
    return item


async def get_menu_item(db: AsyncSession, tenant_id: str, item_id: uuid.UUID) -> MenuItem:
    result = await db.execute(
        select(MenuItem).where(MenuItem.id == item_id, MenuItem.tenant_id == tenant_id)
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise NotFoundError(f"MenuItem {item_id} NOT_FOUND for tenant {tenant_id}")
    return item


async def update_menu_item(
    db: AsyncSession, tenant_id: str, item_id: uuid.UUID, data: MenuItemUpdate
) -> MenuItem:
    item = await get_menu_item(db, tenant_id, item_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    try:
        await db.commit()
        await db.refresh(item)
    except IntegrityError as exc:
        await db.rollback()
        if "uq_menu_items_tenant_short_code" in str(exc.orig):
            raise ConflictError("Short code already used by another item in this tenant")
        raise
    return item


async def delete_menu_item(db: AsyncSession, tenant_id: str, item_id: uuid.UUID) -> None:
    item = await get_menu_item(db, tenant_id, item_id)
    await db.delete(item)
    await db.commit()
```

### API Routes

File: `backend/app/api/v1/routes/menu.py` (replace stub)

```python
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.models.user import TenantUser
from app.schemas.common import DataResponse
from app.schemas.menu import MenuItemCreate, MenuItemResponse, MenuItemUpdate
from app.services import menu_service

router = APIRouter(prefix="/menu", tags=["menu"])


@router.get("/items", response_model=DataResponse[list[MenuItemResponse]])
async def list_items(
    current_user: TenantUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    items = await menu_service.list_menu_items(db, current_user.tenant_id)
    return DataResponse(data=[MenuItemResponse.model_validate(i) for i in items])


@router.post("/items", response_model=DataResponse[MenuItemResponse], status_code=201)
async def create_item(
    body: MenuItemCreate,
    current_user: TenantUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    item = await menu_service.create_menu_item(db, current_user.tenant_id, body)
    return DataResponse(data=MenuItemResponse.model_validate(item))


@router.patch("/items/{item_id}", response_model=DataResponse[MenuItemResponse])
async def update_item(
    item_id: uuid.UUID,
    body: MenuItemUpdate,
    current_user: TenantUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    item = await menu_service.update_menu_item(db, current_user.tenant_id, item_id, body)
    return DataResponse(data=MenuItemResponse.model_validate(item))


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(
    item_id: uuid.UUID,
    current_user: TenantUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    await menu_service.delete_menu_item(db, current_user.tenant_id, item_id)
```

### Onboarding Checklist Integration

In `backend/app/api/v1/routes/tenants.py`, update `_compute_checklist()` to check for at least one active menu item:

```python
# In _compute_checklist(), add this check:
from app.models.menu import MenuItem

menu_count_row = await db.execute(
    select(func.count(MenuItem.id)).where(
        MenuItem.tenant_id == tenant_id,
        MenuItem.is_available == True,
    )
)
menu_configured = (menu_count_row.scalar() or 0) > 0
```

And add the checklist entry:
```python
ChecklistItem(
    key="menu_configured",
    label="Add at least one menu item",
    completed=menu_configured,
    route="/admin/menu",
),
```

### alembic/env.py — Add model import

```python
from app.models import menu as _menu  # noqa: F401
```

### Frontend Components

**File**: `frontend/src/features/admin/pages/MenuItemsPage.tsx`

Full inline-editable table with:
- Columns: Short Code | Name | Category | Food Type (colored badge) | Price (₹) | Available (toggle) | Actions (delete)
- "Add Item" button → opens `MenuItemForm` modal
- Row click → opens `MenuItemForm` pre-filled for edit
- Delete with confirmation dialog

**File**: `frontend/src/features/admin/api/menu.ts`
```typescript
import { apiClient } from '@/shared/lib/apiClient'
import type { MenuItemCreate, MenuItemResponse, MenuItemUpdate } from '../types/menu'

export const menuApi = {
  list: () => apiClient.get<MenuItemResponse[]>('/menu/items'),
  create: (data: MenuItemCreate) => apiClient.post<MenuItemResponse>('/menu/items', data),
  update: (id: string, data: MenuItemUpdate) =>
    apiClient.patch<MenuItemResponse>(`/menu/items/${id}`, data),
  delete: (id: string) => apiClient.delete(`/menu/items/${id}`),
}
```

**File**: `frontend/src/features/admin/hooks/useMenuItems.ts`
```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { menuApi } from '../api/menu'

export const MENU_ITEMS_KEY = ['menu-items'] as const

export function useMenuItems() {
  return useQuery({ queryKey: MENU_ITEMS_KEY, queryFn: menuApi.list })
}

export function useCreateMenuItem() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: menuApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: MENU_ITEMS_KEY }),
  })
}

export function useUpdateMenuItem() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: MenuItemUpdate }) =>
      menuApi.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: MENU_ITEMS_KEY }),
  })
}

export function useDeleteMenuItem() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: menuApi.delete,
    onSuccess: () => qc.invalidateQueries({ queryKey: MENU_ITEMS_KEY }),
  })
}
```

**Types file**: `frontend/src/features/admin/types/menu.ts`
```typescript
export type FoodType = 'veg' | 'egg' | 'non_veg'

export interface MenuItemResponse {
  id: string
  tenant_id: string
  name: string
  category: string
  short_code: number | null
  price_paise: number
  food_type: FoodType
  description: string | null
  is_available: boolean
  display_order: number
}

export interface MenuItemCreate {
  name: string
  category: string
  short_code?: number | null
  price_paise: number
  food_type: FoodType
  description?: string | null
  is_available?: boolean
  display_order?: number
}

export type MenuItemUpdate = Partial<MenuItemCreate>
```

### Seed Script

File: `backend/scripts/seed_menu_items.py`

```python
"""
Seed script: Import menu items from CSV into the platform tenant.

Usage (dev):
  docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm backend \\
    sh -c "PYTHONPATH=/app python /app/scripts/seed_menu_items.py"

Usage (prod — pass credentials via env):
  SEED_TENANT_SLUG=sphotel \\
  SEED_CSV_PATH=/app/scripts/menu_seed_data.csv \\
    python /app/scripts/seed_menu_items.py

The script is idempotent — skips items that already exist by (tenant_id, name, category).
"""
import asyncio
import csv
import os
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings

SEED_TENANT_SLUG = os.getenv("SEED_TENANT_SLUG", "sphotel")
# CSV embedded inline (copied from items_114325_2025_01_01_05_38_04.csv)
# OR set SEED_CSV_PATH to an external file
SEED_CSV_PATH = os.getenv("SEED_CSV_PATH", "")

# CSV data embedded directly (237 items from the billing system export)
EMBEDDED_CSV = """Name,Short_Code,Category,Price,Attributes,Rank
...
"""  # Will be populated by dev task below


def parse_short_code(raw: str) -> int | None:
    """Return int if raw is a pure integer string, else None."""
    try:
        val = int(raw.strip())
        return val if val > 0 else None
    except (ValueError, AttributeError):
        return None


def parse_food_type(raw: str) -> str:
    raw = (raw or "").strip().lower()
    if "non" in raw:
        return "non_veg"
    if "egg" in raw:
        return "egg"
    return "veg"


async def seed() -> None:
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore[call-overload]

    async with async_session() as db:
        # Check tenant exists
        row = (await db.execute(
            text("SELECT id FROM tenants WHERE slug = :slug"),
            {"slug": SEED_TENANT_SLUG},
        )).first()
        if row is None:
            print(f"❌ Tenant '{SEED_TENANT_SLUG}' not found — run seed_super_admin.py first")
            return

        # Load CSV rows
        if SEED_CSV_PATH and os.path.exists(SEED_CSV_PATH):
            with open(SEED_CSV_PATH, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
        else:
            import io
            rows = list(csv.DictReader(io.StringIO(EMBEDDED_CSV)))

        inserted = 0
        skipped = 0

        for row_data in rows:
            name = (row_data.get("Name") or row_data.get("name") or "").strip()
            category = (row_data.get("Category") or row_data.get("category") or "").strip()
            if not name or not category:
                continue

            # Idempotency: skip if (tenant_id, name, category) already exists
            existing = (await db.execute(
                text("SELECT id FROM menu_items WHERE tenant_id = :tid AND name = :name AND category = :cat"),
                {"tid": SEED_TENANT_SLUG, "name": name, "cat": category},
            )).first()
            if existing:
                skipped += 1
                continue

            price_raw = (row_data.get("Price") or row_data.get("price") or "0").strip()
            try:
                price_paise = int(float(price_raw) * 100)
            except ValueError:
                price_paise = 0

            short_code = parse_short_code(
                row_data.get("Short_Code") or row_data.get("short_code") or ""
            )
            food_type = parse_food_type(
                row_data.get("Attributes") or row_data.get("attributes") or "veg"
            )
            rank_raw = (row_data.get("Rank") or row_data.get("rank") or "0").strip()
            try:
                display_order = int(float(rank_raw))
            except ValueError:
                display_order = 0

            await db.execute(
                text("""
                    INSERT INTO menu_items
                        (tenant_id, name, category, short_code, price_paise,
                         food_type, is_available, display_order)
                    VALUES
                        (:tenant_id, :name, :category, :short_code, :price_paise,
                         :food_type::food_type, true, :display_order)
                """),
                {
                    "tenant_id": SEED_TENANT_SLUG,
                    "name": name,
                    "category": category,
                    "short_code": short_code,
                    "price_paise": price_paise,
                    "food_type": food_type,
                    "display_order": display_order,
                },
            )
            inserted += 1

        await db.commit()
        print(f"✅ Seed complete — inserted: {inserted}, skipped (already exist): {skipped}")


if __name__ == "__main__":
    asyncio.run(seed())
```

## Tasks

### Backend

- [x] **Task 1 — FoodType enum in permissions**
  - Add `FoodType(StrEnum)` with values `veg`, `egg`, `non_veg` to `backend/app/core/security/permissions.py`

- [x] **Task 2 — SQLAlchemy model**
  - Create `backend/app/models/menu.py` with `MenuItem` model (schema above)
  - Add import to `backend/alembic/env.py`: `from app.models import menu as _menu`

- [x] **Task 3 — Alembic migration**
  - Create `backend/alembic/versions/0006_create_menu_items.py`
  - Creates `food_type` PG enum (with DO block for idempotency), `menu_items` table, indexes, unique constraint
  - Uses pure `op.execute()` raw SQL following project pattern (avoids SA Enum create_type issues)

- [x] **Task 4 — Pydantic schemas**
  - Create `backend/app/schemas/menu.py` with `MenuItemCreate`, `MenuItemUpdate`, `MenuItemResponse`

- [x] **Task 5 — Service layer**
  - Create `backend/app/services/menu_service.py` with `list_menu_items`, `create_menu_item`, `get_menu_item`, `update_menu_item`, `delete_menu_item`

- [x] **Task 6 — API routes**
  - Replaced stub in `backend/app/api/v1/routes/menu.py` with full CRUD routes (already registered in router.py)

- [x] **Task 7 — Onboarding checklist update**
  - Updated `_compute_checklist()` in `backend/app/api/v1/routes/tenants.py` to dynamically check `menu_items` count
  - Also fixed bug: lookup by `Tenant.slug` instead of `Tenant.id` (tenant_id is slug string)
  - Updated existing onboarding tests to provide 3 DB mock results (tenant + staff_count + menu_count)

- [x] **Task 8 — Backend integration tests**
  - Create `backend/tests/integration/routes/test_menu_routes.py` (10 tests)
  - Cover: list empty, list with items, create 201, duplicate short_code 409, invalid food_type 422, update 200, update wrong tenant 404, delete 204, delete wrong tenant 404, RBAC 403

### Frontend

- [x] **Task 9 — Types and API client**
  - Create `frontend/src/features/admin/types/menu.ts`
  - Create `frontend/src/features/admin/api/menu.ts`

- [x] **Task 10 — React Query hooks**
  - Create `frontend/src/features/admin/hooks/useMenuItems.ts`

- [x] **Task 11 — MenuItemForm component**
  - Create `frontend/src/features/admin/components/MenuItemForm.tsx`
  - Fields: name, category (datalist suggestions), short_code, price (rupees → paise), food_type radio, description, is_available, display_order
  - Works for both create and edit

- [x] **Task 12 — MenuItemsPage**
  - Create `frontend/src/features/admin/pages/MenuItemsPage.tsx`
  - Table with all columns, Add button, row edit, availability toggle, delete confirmation modal
  - Wired to route `/admin/menu` in `routes.tsx`

- [x] **Task 13 — Add menu route to sidebar**
  - Added "Menu Items" nav link in `Sidebar.tsx` pointing to `/admin/menu`

- [x] **Task 14 — Frontend tests**
  - Create `frontend/src/features/admin/pages/MenuItemsPage.test.tsx` (7 tests)
  - Tests: empty state, renders items list, price in rupees, open add form, open edit form, delete confirmation, delete mutation called

### Seed Script

- [x] **Task 15 — Seed script with CSV data**
  - Create `backend/scripts/seed_menu_items.py` — all 236 items embedded inline
  - Fixed: use `CAST(:food_type AS food_type)` instead of `::food_type` (asyncpg syntax)
  - Run: `docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm backend sh -c "PYTHONPATH=/app python /app/scripts/seed_menu_items.py"`
  - ✅ Successfully seeded 236 items into sphotel tenant

## Dev Notes

### Key Decisions

1. **Price in paise**: Always store as integer paise (rupees × 100) to avoid floating-point issues. UI shows ₹ by dividing by 100.

2. **Short code uniqueness**: PostgreSQL naturally allows multiple NULLs in a unique constraint — no partial index needed. Use `DEFERRABLE INITIALLY DEFERRED` so bulk inserts within one transaction can succeed.

3. **Category as free-form string**: No separate `categories` table for now (added in a later story). The UI can suggest existing categories from the items list.

4. **FoodType enum placement**: Add to `permissions.py` alongside `UserRole` for consistency with existing pattern.

5. **SAEnum `values_callable`**: Must use same pattern as `UserRole` — `values_callable=lambda obj: [e.value for e in obj]` — to send lowercase strings to PostgreSQL.

6. **Seed script CSV mapping**:
   - `Name` → `name`
   - `Short_Code` → `short_code` (integer or NULL for non-numeric values like "34(s)", "NCPA")
   - `Category` → `category`
   - `Price` (rupees) → `price_paise` = `int(float(price) * 100)`
   - `Attributes` (veg/egg/non-veg) → `food_type` ("non_veg" for "non-veg")
   - `Rank` → `display_order`

7. **Onboarding checklist AC10**: Import `MenuItem` in `tenants.py` only for the checklist query — no circular dependency since menu model has no reverse FK to tenants model.

### Migration Template

```python
"""create menu_items table

Revision ID: 0006
Revises: 0005
Create Date: 2026-03-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TYPE food_type AS ENUM ('veg', 'egg', 'non_veg')")
    op.create_table(
        "menu_items",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("short_code", sa.Integer(), nullable=True),
        sa.Column("price_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("food_type", sa.Enum("veg", "egg", "non_veg", name="food_type", create_type=False), nullable=False, server_default="veg"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.slug"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "short_code", name="uq_menu_items_tenant_short_code",
                            deferrable=True, initially="DEFERRED"),
    )
    op.create_index("idx_menu_items_tenant_id", "menu_items", ["tenant_id"])
    op.create_index("idx_menu_items_tenant_category", "menu_items", ["tenant_id", "category"])


def downgrade() -> None:
    op.drop_index("idx_menu_items_tenant_category", table_name="menu_items")
    op.drop_index("idx_menu_items_tenant_id", table_name="menu_items")
    op.drop_table("menu_items")
    op.execute("DROP TYPE food_type")
```

## Dev Agent Record

_To be filled by Dev Agent during implementation_

### Implementation Notes
- Used pure `op.execute()` raw SQL in migration (same as 0003 user_role pattern) — avoids SQLAlchemy Enum `create_type` issues with asyncpg
- Fixed Story 3.2 bug in `tenants.py`: `_compute_checklist` was called with `str(tenant.id)` (UUID) but `TenantUser.tenant_id` and `MenuItem.tenant_id` are slug strings; fixed both onboarding routes to look up by `Tenant.slug`
- Seed script uses `CAST(:food_type AS food_type)` not `::food_type` cast (asyncpg syntax limitation)
- 236/236 CSV items seeded successfully into `sphotel` tenant

### Tests Run
- Backend: 176/176 passed (10 new menu tests + 8 updated onboarding tests)
- Frontend: 29/29 passed (7 new MenuItemsPage tests)

### Change Log
- 2026-03-18: Implemented Story 3.3 — menu item CRUD, FoodType enum, migration 0006, seed script, frontend table/form

### Completion Checklist
- [x] All tasks complete
- [x] Migration runs cleanly (`alembic upgrade head`)
- [x] Backend tests pass (176 passing)
- [x] Frontend tests pass (29 passing)
- [x] Story status updated to `review` in sprint-status.yaml
