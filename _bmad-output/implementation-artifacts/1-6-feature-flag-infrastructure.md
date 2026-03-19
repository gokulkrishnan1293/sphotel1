# Story 1.6: Feature Flag Infrastructure

Status: review

## Story

As an **Admin**,
I want per-tenant feature flags that can enable or disable major features without code changes,
so that tenants only have access to the features they need and the platform can ship features incrementally.

## Acceptance Criteria

1. **Given** a tenant exists in the database, **When** the backend processes any request, **Then** it can read the tenant's feature flags from Valkey via `get_feature_flags(tenant_id)` returning a typed dict.

2. **And** the flags schema includes: `waiter_mode`, `suggestion_engine`, `telegram_alerts`, `gst_module`, `payroll_rewards`, `discount_complimentary`, `waiter_transfer` — all `bool`, defaulting to `False`.

3. **And** flags are cached in Valkey with a 60-second TTL; cache miss falls back to the `tenant_feature_flags` PostgreSQL table.

4. **And** the frontend reads flags from `GET /api/v1/tenants/{id}/features` on app load and stores them in a Zustand `featureFlagStore`.

5. **And** a `useFeatureFlag('waiter_mode')` hook returns `true/false` and any component wrapped in `<FeatureGate flag="waiter_mode">` renders only when the flag is enabled.

6. **And** toggling a flag in the database takes effect within 60 seconds with no deployment required.

## Tasks / Subtasks

- [x] **Task 1: Add `redis[asyncio]` dependency to backend** (AC: #1, #3)
  - [x] In `backend/pyproject.toml`, add `"redis[asyncio]>=5.0"` to `[project] dependencies`
  - [x] Run `make dev` (or `docker compose up`) to rebuild image — do NOT `pip install` directly; the Docker layer handles deps

- [x] **Task 2: Create Alembic migration 0002 — `tenant_feature_flags` table** (AC: #2, #3)
  - [x] Create `backend/alembic/versions/0002_tenant_feature_flags.py`
  - [x] `revision = "0002"`, `down_revision = "0001"` — links to migration chain
  - [x] Table: `tenant_feature_flags`
    - `tenant_id` — `UUID(as_uuid=True)` PRIMARY KEY, FK to `tenants.id` ON DELETE CASCADE
    - `waiter_mode` — `Boolean`, `server_default="false"`, `nullable=False`
    - `suggestion_engine` — `Boolean`, `server_default="false"`, `nullable=False`
    - `telegram_alerts` — `Boolean`, `server_default="false"`, `nullable=False`
    - `gst_module` — `Boolean`, `server_default="false"`, `nullable=False`
    - `payroll_rewards` — `Boolean`, `server_default="false"`, `nullable=False`
    - `discount_complimentary` — `Boolean`, `server_default="false"`, `nullable=False`
    - `waiter_transfer` — `Boolean`, `server_default="false"`, `nullable=False`
    - `updated_at` — `DateTime(timezone=True)`, `server_default=text("now()")`, `nullable=False`
  - [x] `PrimaryKeyConstraint("tenant_id", name=op.f("pk_tenant_feature_flags"))`
  - [x] `ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_tenant_feature_flags_tenant_id_tenants"), ondelete="CASCADE")`
  - [x] `downgrade()`: drop FK constraint, then drop table
  - [x] Run `make migrate` to verify migration applies cleanly and is idempotent

- [ ] **Task 3: Create `TenantFeatureFlags` SQLAlchemy model** (AC: #2)
  - [ ] Create `backend/app/models/feature_flags.py`
  - [ ] Class `TenantFeatureFlags(Base)` — does NOT use `TenantMixin` (tenant_id IS the PK)
  - [ ] `__tablename__ = "tenant_feature_flags"`
  - [ ] `tenant_id: Mapped[uuid.UUID]` — UUID PK, FK to `tenants.id`
  - [ ] All 7 flag columns: `Mapped[bool]` with `default=False`
  - [ ] `updated_at: Mapped[datetime]` — TIMESTAMPTZ, `server_default=func.now()`, `onupdate=func.now()`
  - [x] Add import to `backend/app/models/__init__.py` so Alembic autogenerate can detect it

- [x] **Task 4: Create feature flag schemas** (AC: #1, #2, #4)
  - [x] Create `backend/app/schemas/feature_flags.py`
  - [x] `FeatureFlagsDict(TypedDict)` — 7 bool keys (used internally by service/repo layer)
  - [x] `DEFAULT_FLAGS: FeatureFlagsDict` — all `False` (used when tenant has no row yet)
  - [x] `FeatureFlagsResponse(BaseModel)` — 7 bool fields with `model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)` — camelCase JSON output (e.g., `waiterMode`, `suggestionEngine`)
  - [x] Import `to_camel` from `pydantic.alias_generators`

- [x] **Task 5: Create Valkey async client + dependency** (AC: #3)
  - [x] Create `backend/app/db/valkey.py`
  - [x] Import `redis.asyncio as aioredis` — the `redis[asyncio]` package
  - [x] `async def get_valkey() -> AsyncGenerator[Any, None]` — FastAPI dependency that yields client and closes on teardown (typed Any because redis-py lacks generics)
  - [x] `VALKEY_FLAG_TTL: int = 60` — 60-second TTL constant
  - [x] Keep file ≤ 100 lines

- [x] **Task 6: Create feature flags repository** (AC: #3)
  - [x] Create `backend/app/repositories/feature_flags.py`
  - [x] `async def get_feature_flags_from_db(tenant_id: uuid.UUID, db: AsyncSession) -> FeatureFlagsDict`
    - `SELECT * FROM tenant_feature_flags WHERE tenant_id = :tenant_id`
    - If row exists: return dict from row attributes
    - If no row (tenant not yet initialized): return `DEFAULT_FLAGS`
    - Use `result.scalar_one_or_none()` pattern
  - [x] Keep `tenant_id` as first parameter (architecture rule #4)
  - [x] No raw SQL — use SQLAlchemy `select(TenantFeatureFlags).where(TenantFeatureFlags.tenant_id == tenant_id)`

- [x] **Task 7: Create feature flags service (Valkey-first with DB fallback)** (AC: #1, #3, #6)
  - [x] Create `backend/app/services/feature_flags.py`
  - [x] Valkey key format: `f"feature_flags:{tenant_id}"` (string key, JSON value)
  - [x] `async def get_feature_flags(tenant_id: uuid.UUID, db: AsyncSession, valkey: Any) -> FeatureFlagsDict`
    - Try `await valkey.get(cache_key)` — if hit, return `cast(FeatureFlagsDict, json.loads(cached))`
    - On miss: call `get_feature_flags_from_db(tenant_id, db)`
    - Store result: `await valkey.set(cache_key, json.dumps(flags), ex=VALKEY_FLAG_TTL)`
    - Return flags dict
  - [x] Handle `Exception` from Valkey gracefully — fall back to DB if Valkey is unavailable
  - [x] Keep file ≤ 100 lines

- [x] **Task 8: Implement `GET /api/v1/tenants/{tenant_id}/features` endpoint** (AC: #4)
  - [x] Update `backend/app/api/v1/routes/tenants.py`
  - [x] `@router.get("/{tenant_id}/features", response_model=DataResponse[FeatureFlagsResponse])`
  - [x] Path param: `tenant_id: uuid.UUID`
  - [x] Depends: `db: AsyncSession = Depends(get_db)`, `valkey: Any = Depends(get_valkey)`
  - [x] Call `get_feature_flags(tenant_id, db, valkey)`, wrap in `DataResponse(data=FeatureFlagsResponse(**flags))`
  - [x] Return HTTP 200 with envelope
  - [x] Note: Auth/authorization to be enforced in Epic 2 — `# TODO: auth guard added in Epic 2`

- [x] **Task 9: Create Zustand `featureFlagStore`** (AC: #4)
  - [x] Create `frontend/src/lib/featureFlagStore.ts`
  - [x] Zustand v5 API: `import { create } from 'zustand'`
  - [x] `FeatureFlagKey` union type: `'waiterMode' | 'suggestionEngine' | 'telegramAlerts' | 'gstModule' | 'payrollRewards' | 'discountComplimentary' | 'waiterTransfer'`
  - [x] `FeatureFlagsState` interface: 7 bool fields (camelCase matching API response) + `setFlags(flags: Partial<FeatureFlagsData>): void`
  - [x] Default store: all flags `false`
  - [x] Export `useFeatureFlagStore = create<FeatureFlagsState>(...)`
  - [x] Keep file ≤ 100 lines

- [x] **Task 10: Create `useFeatureFlag` hook** (AC: #5)
  - [x] Create `frontend/src/shared/hooks/useFeatureFlag.ts`
  - [x] `export function useFeatureFlag(flag: FeatureFlagKey): boolean`
  - [x] Reads from `useFeatureFlagStore` by key
  - [x] Returns the boolean value (default `false` if store not yet hydrated)
  - [x] File is tiny — keep it focused, no other logic here

- [x] **Task 11: Create `FeatureGate` component** (AC: #5)
  - [x] Create `frontend/src/shared/components/FeatureGate.tsx`
  - [x] Props: `{ flag: FeatureFlagKey; children: React.ReactNode; fallback?: React.ReactNode }`
  - [x] Uses `useFeatureFlag(flag)` — renders `children` if enabled, `fallback` (default: `null`) if not
  - [x] Full TypeScript types — no `any`
  - [x] Keep file ≤ 100 lines

- [x] **Task 12: Wire feature flags fetch on app load** (AC: #4)
  - [x] Update `frontend/src/app/providers.tsx`
  - [x] Added `FeatureFlagHydrator` inner component that uses `useQuery` from TanStack Query
  - [x] Query: `{ queryKey: ['featureFlags', tenantId], queryFn: ..., enabled: tenantId !== null, staleTime: 55_000 }`
  - [x] On success: `useEffect` watches `data` and calls `setFlags(data)` (TanStack Query v5 — no `onSuccess`)
  - [x] `tenantId` stubbed as `null` — flags stay at defaults until Epic 2 auth wires the tenant ID
  - [x] Wrapped children with `FeatureFlagHydrator` inside `QueryClientProvider`

- [x] **Task 13: Write tests** (AC: all)
  - [x] Backend: `backend/tests/unit/schemas/test_feature_flags.py` — 6 tests for TypedDict, DEFAULT_FLAGS, camelCase serialization
  - [x] Backend: `backend/tests/unit/services/test_feature_flags_service.py` — 5 tests for cache hit/miss, Valkey errors, DB fallback
  - [x] Backend: `backend/tests/integration/routes/test_tenants_features.py` — 6 tests for endpoint envelope, camelCase keys, all-false defaults, invalid UUID 422
  - [x] Frontend: `frontend/src/lib/featureFlagStore.test.ts` — 4 tests for default state, setFlags partial and full updates
  - [x] Frontend: `frontend/src/shared/components/FeatureGate.test.tsx` — 5 tests for flag-gated rendering, fallback, all 7 flag keys

## Dev Notes

### Current State (from Stories 1.1–1.5)

**Already exists — do NOT recreate:**
- `backend/app/db/session.py` — `get_db()` async generator pattern; use this SAME pattern for `get_valkey()`
- `backend/app/models/base.py` — `Base`, `TimestampMixin`, `TenantMixin`; do NOT use `TenantMixin` for `TenantFeatureFlags` (tenant_id is PK, not a regular column)
- `backend/app/schemas/common.py` — `DataResponse[T]`, `ErrorResponse`, `ErrorDetail`; import `DataResponse` from here
- `backend/app/api/v1/routes/tenants.py` — stub router with `prefix="/tenants"`, `tags=["tenants"]`; comment already says "Story 1.6"
- `backend/app/api/v1/router.py` — `tenants.router` already registered; no changes needed
- `backend/app/core/config.py` — `settings.VALKEY_URL` already present; no changes needed
- `backend/alembic/versions/0001_initial_schema_tenants_users_audit_logs.py` — chain: `0002` must set `down_revision = "0001"`
- `frontend/src/lib/api.ts` — `apiClient` with envelope unwrapper; `apiClient.get<T>(path)` returns `{ data: T }` after unwrapping
- `frontend/src/app/providers.tsx` — `QueryClientProvider` wrapping; extend this file for flag fetch
- `frontend/src/lib/queryClient.ts` — `queryClient` exported; no changes needed
- All feature folders in `frontend/src/features/` — do NOT put feature-flag code inside a feature folder; it's shared infrastructure, lives in `src/lib/` and `src/shared/`

**NOT yet existing — create in this story:**
- `backend/app/db/valkey.py`
- `backend/app/models/feature_flags.py`
- `backend/app/schemas/feature_flags.py`
- `backend/app/repositories/feature_flags.py`
- `backend/app/services/feature_flags.py`
- `backend/alembic/versions/0002_tenant_feature_flags.py`
- `frontend/src/lib/featureFlagStore.ts`
- `frontend/src/shared/hooks/useFeatureFlag.ts`
- `frontend/src/shared/components/FeatureGate.tsx`

### Critical: `redis-py` v5 Async API (Valkey is Redis 7.2-compatible)

Valkey is a Redis-compatible in-memory store. The `redis[asyncio]` Python package (v5+) works with it transparently.

```python
# backend/app/db/valkey.py
import redis.asyncio as aioredis
from collections.abc import AsyncGenerator
from app.core.config import settings

VALKEY_FLAG_TTL: int = 60

async def get_valkey() -> AsyncGenerator[aioredis.Redis, None]:  # type: ignore[type-arg]
    client = aioredis.Redis.from_url(settings.VALKEY_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()
```

**Key operations:**
```python
# Read (returns str | None when decode_responses=True)
cached: str | None = await valkey.get(key)

# Write with TTL
await valkey.set(key, json.dumps(flags), ex=VALKEY_FLAG_TTL)  # ex = seconds

# Invalidate (for future use when Admin toggles flag)
await valkey.delete(key)
```

**Cache key format:** `f"feature_flags:{tenant_id}"` — `tenant_id` as UUID string.

### Critical: Pydantic v2 camelCase Output

The architecture mandates camelCase JSON for all API responses. Use:

```python
# backend/app/schemas/feature_flags.py
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class FeatureFlagsResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    waiter_mode: bool = False
    suggestion_engine: bool = False
    telegram_alerts: bool = False
    gst_module: bool = False
    payroll_rewards: bool = False
    discount_complimentary: bool = False
    waiter_transfer: bool = False
```

This produces JSON output: `{ "waiterMode": false, "suggestionEngine": false, ... }` — matching the frontend's camelCase field names.

**The `TypedDict` is for internal Python-only use (service → repo layer).** The `BaseModel` is for FastAPI serialization only.

```python
from typing import TypedDict

class FeatureFlagsDict(TypedDict):
    waiter_mode: bool
    suggestion_engine: bool
    telegram_alerts: bool
    gst_module: bool
    payroll_rewards: bool
    discount_complimentary: bool
    waiter_transfer: bool

DEFAULT_FLAGS: FeatureFlagsDict = {
    "waiter_mode": False,
    "suggestion_engine": False,
    "telegram_alerts": False,
    "gst_module": False,
    "payroll_rewards": False,
    "discount_complimentary": False,
    "waiter_transfer": False,
}
```

### Critical: SQLAlchemy Model — No TenantMixin Here

`TenantMixin` adds `tenant_id` as a regular column. `TenantFeatureFlags` uses `tenant_id` as the PRIMARY KEY — do not use the mixin.

```python
# backend/app/models/feature_flags.py
import uuid
from datetime import datetime

from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TenantFeatureFlags(Base):
    __tablename__ = "tenant_feature_flags"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        primary_key=True,
    )
    waiter_mode: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    suggestion_engine: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    telegram_alerts: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    gst_module: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    payroll_rewards: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    discount_complimentary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    waiter_transfer: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
```

**After creating this file, add the import to `backend/app/models/__init__.py`:**
```python
from app.models.feature_flags import TenantFeatureFlags  # noqa: F401
```
This is required so Alembic's `autogenerate` can detect the model for future migrations.

### Critical: Service — Valkey Fallback on Error

The Valkey cache must NEVER break regular API traffic. If Valkey is unreachable, fall back to DB silently:

```python
# backend/app/services/feature_flags.py
import json
import uuid

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.valkey import VALKEY_FLAG_TTL
from app.repositories.feature_flags import get_feature_flags_from_db
from app.schemas.feature_flags import FeatureFlagsDict

CACHE_KEY_PREFIX = "feature_flags"


async def get_feature_flags(
    tenant_id: uuid.UUID,
    db: AsyncSession,
    valkey: aioredis.Redis,  # type: ignore[type-arg]
) -> FeatureFlagsDict:
    cache_key = f"{CACHE_KEY_PREFIX}:{tenant_id}"
    try:
        cached = await valkey.get(cache_key)
        if cached is not None:
            return json.loads(cached)  # type: ignore[return-value]
    except Exception:
        pass  # Valkey unavailable — fall through to DB

    flags = await get_feature_flags_from_db(tenant_id, db)

    try:
        await valkey.set(cache_key, json.dumps(flags), ex=VALKEY_FLAG_TTL)
    except Exception:
        pass  # Best-effort cache write — don't fail the request

    return flags
```

### Critical: Zustand v5 Store API

Zustand v5 removed the legacy `subscribeWithSelector` middleware requirement for basic stores. Use:

```typescript
// frontend/src/lib/featureFlagStore.ts
import { create } from 'zustand'

export type FeatureFlagKey =
  | 'waiterMode'
  | 'suggestionEngine'
  | 'telegramAlerts'
  | 'gstModule'
  | 'payrollRewards'
  | 'discountComplimentary'
  | 'waiterTransfer'

interface FeatureFlagsState {
  waiterMode: boolean
  suggestionEngine: boolean
  telegramAlerts: boolean
  gstModule: boolean
  payrollRewards: boolean
  discountComplimentary: boolean
  waiterTransfer: boolean
  setFlags: (flags: Partial<Omit<FeatureFlagsState, 'setFlags'>>) => void
}

export const useFeatureFlagStore = create<FeatureFlagsState>((set) => ({
  waiterMode: false,
  suggestionEngine: false,
  telegramAlerts: false,
  gstModule: false,
  payrollRewards: false,
  discountComplimentary: false,
  waiterTransfer: false,
  setFlags: (flags) => set((state) => ({ ...state, ...flags })),
}))
```

**Accessing store outside of React components** (for initialization): `useFeatureFlagStore.getState().setFlags(data)`

### Critical: TanStack Query v5 — `useQuery` in Providers

TanStack Query v5 changed `onSuccess` callback — it no longer exists on `useQuery`. Use `useEffect` + `data` watching:

```tsx
// Pattern for feature flag hydration in providers.tsx
import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { useFeatureFlagStore } from '@/lib/featureFlagStore'

// Inside a component that is a child of QueryClientProvider:
function FeatureFlagHydrator({ tenantId }: { tenantId: string | null }) {
  const setFlags = useFeatureFlagStore((s) => s.setFlags)
  const { data } = useQuery({
    queryKey: ['featureFlags', tenantId],
    queryFn: () =>
      apiClient
        .get<FeatureFlagsResponse>(`/tenants/${tenantId}/features`)
        .then((r) => r.data),
    enabled: tenantId !== null,
    staleTime: 55_000,  // 55s — slightly under Valkey 60s TTL
  })

  useEffect(() => {
    if (data) setFlags(data)
  }, [data, setFlags])

  return null
}
```

**`staleTime: 55_000`** keeps the query fresh in the browser for 55 seconds, aligning with the 60s Valkey TTL — avoids hammering the API while ensuring flags are refreshed before the cache expires.

### Critical: 100-Line File Limit

All files must stay ≤100 lines. Approximate line budgets:
- `app/db/valkey.py` — ~25 lines (client factory + dependency + TTL constant)
- `app/models/feature_flags.py` — ~35 lines (model with 7 flag columns)
- `app/schemas/feature_flags.py` — ~35 lines (TypedDict + DEFAULT_FLAGS + BaseModel)
- `app/repositories/feature_flags.py` — ~25 lines (single query function)
- `app/services/feature_flags.py` — ~40 lines (cache-first service)
- `app/api/v1/routes/tenants.py` — ~25 lines (single endpoint + imports)
- `frontend/src/lib/featureFlagStore.ts` — ~35 lines (store definition)
- `frontend/src/shared/hooks/useFeatureFlag.ts` — ~10 lines (single hook)
- `frontend/src/shared/components/FeatureGate.tsx` — ~20 lines (wrapper component)

All well within budget. If any file approaches 80 lines, consider splitting imports/types.

### Critical: Alembic Migration Pattern — Follow Existing Convention

Reference the 0001 migration for exact patterns. Key differences for 0002:

```python
# backend/alembic/versions/0002_tenant_feature_flags.py
"""add tenant_feature_flags table

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-17
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_feature_flags",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("waiter_mode", sa.Boolean(), nullable=False, server_default="false"),
        # ... all 7 flag columns
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"],
            name=op.f("fk_tenant_feature_flags_tenant_id_tenants"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("tenant_id", name=op.f("pk_tenant_feature_flags")),
    )


def downgrade() -> None:
    op.drop_table("tenant_feature_flags")
```

Note: No `op.create_index` needed since `tenant_id` IS the PK (PK has implicit index). No separate `idx_` index required.

### Architecture Compliance Notes

- **Wrapped envelope (rule #2):** `DataResponse[FeatureFlagsResponse]` — never return raw dict from endpoint
- **camelCase JSON (rule #3):** `alias_generator=to_camel` on `FeatureFlagsResponse` — `waiter_mode` → `waiterMode` in API output
- **`tenant_id` first param (rule #4):** Both `get_feature_flags_from_db(tenant_id, db)` and `get_feature_flags(tenant_id, db, valkey)` follow this rule
- **TanStack Query (rule #5):** `useQuery` in `FeatureFlagHydrator` — NOT `useState` + `useEffect` + `fetch`
- **No raw SQL (rule #6):** SQLAlchemy `select(TenantFeatureFlags).where(...)` — no string SQL
- **100-line file limit (rule #10):** All new files under budget (see estimates above)
- **Full type safety (rule #12):** `FeatureFlagKey` union type prevents invalid flag names; TypedDict for internal use; `mypy --strict` must pass

### Previous Story Intelligence (Story 1.5)

From Story 1.5 completion notes and debug log:
- `docker-compose.prod.yml` now has Traefik routing — backend accessible via HTTPS; no direct port exposure
- Frontend build uses monorepo root context (`.`) — no changes needed for this story
- `.dockerignore` excludes `_bmad*` dirs from Docker builds — no interference with story output files
- `docker-compose.dev.yml` updated to monorepo root context — `make dev` should work correctly

**Relevant for this story:**
- `settings.VALKEY_URL` is already defined in `app/core/config.py` — the Valkey container is already running in `docker-compose.yml` as `valkey/valkey:8-alpine` on port 6379 internally
- The `VALKEY_URL` in `.env` points to `redis://valkey:6379/0` (internal Docker network URL) — `redis://` scheme works with `redis[asyncio]` package for Valkey

### Project Structure Notes

**Files created by this story:**
- `backend/alembic/versions/0002_tenant_feature_flags.py`
- `backend/app/models/feature_flags.py`
- `backend/app/schemas/feature_flags.py`
- `backend/app/db/valkey.py`
- `backend/app/repositories/feature_flags.py`
- `backend/app/services/feature_flags.py`
- `frontend/src/lib/featureFlagStore.ts`
- `frontend/src/shared/hooks/useFeatureFlag.ts`
- `frontend/src/shared/components/FeatureGate.tsx`
- `backend/tests/test_feature_flags.py`
- `frontend/src/lib/featureFlagStore.test.ts`
- `frontend/src/shared/components/FeatureGate.test.tsx`

**Files modified by this story:**
- `backend/pyproject.toml` — add `redis[asyncio]>=5.0` dependency
- `backend/app/models/__init__.py` — import `TenantFeatureFlags`
- `backend/app/api/v1/routes/tenants.py` — add `GET /{tenant_id}/features` endpoint
- `frontend/src/app/providers.tsx` — add `FeatureFlagHydrator` inner component

**Files NOT touched by this story:**
- `docker-compose.yml`, `docker-compose.dev.yml`, `docker-compose.prod.yml` — Valkey already running
- `backend/app/core/config.py` — `VALKEY_URL` already present
- `backend/app/api/v1/router.py` — `tenants.router` already registered
- All other feature routes and models — no cross-module imports

### How Downstream Stories Use This Infrastructure

This story's output is consumed throughout the platform:

- **Epic 2 (Auth):** After login, auth token payload will carry `tenant_id`; `FeatureFlagHydrator` uses it to fetch flags for the session
- **Epic 3.8 (Feature Flag Admin UI):** Calls `PATCH /api/v1/tenants/me/features` to toggle flags; cache invalidation via `valkey.delete(f"feature_flags:{tenant_id}")` — takes effect within 60 seconds
- **Epic 4 (Billing):** `<FeatureGate flag="discountComplimentary">` gates the discount approval workflow (Story 4.9)
- **Epic 11 (Waiter Mode):** Entire waiter surface gated by `<FeatureGate flag="waiterMode">`
- **Epic 12 (Suggestions):** `<FeatureGate flag="suggestionEngine">` gates co-order suggestions in command palette

**The `get_feature_flags(tenant_id, db, valkey)` service function** is the canonical entry point for ALL backend feature flag checks. Any middleware or background worker that needs flag state should import and call this function.

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 1, Story 1.6]
- [Source: _bmad-output/planning-artifacts/epics.md — Epic 3.8 (feature flag admin toggle PATCH endpoint context)]
- [Source: _bmad-output/planning-artifacts/epics.md — Epic 11 (waiter_mode FeatureGate usage)]
- [Source: _bmad-output/planning-artifacts/epics.md — Epic 12 (suggestion_engine FeatureGate usage)]
- [Source: _bmad-output/planning-artifacts/architecture.md — All AI Agents MUST rules (12 rules)]
- [Source: _bmad-output/planning-artifacts/architecture.md — API patterns: wrapped envelope, camelCase JSON]
- [Source: _bmad-output/planning-artifacts/architecture.md — Naming conventions: snake_case DB, camelCase JSON, Pydantic alias_generator]
- [Source: _bmad-output/planning-artifacts/architecture.md — Internal event bus: Valkey pub/sub for real-time events]
- [Source: _bmad-output/implementation-artifacts/1-5-cicd-pipeline-production-deployment.md — Valkey container already in docker-compose.yml; VALKEY_URL in settings]
- [Source: backend/app/db/session.py — get_db() async generator pattern; replicate for get_valkey()]
- [Source: backend/app/models/base.py — Base, TimestampMixin, TenantMixin; do NOT use TenantMixin here]
- [Source: backend/app/schemas/common.py — DataResponse[T] for envelope wrapping]
- [Source: backend/app/core/config.py — settings.VALKEY_URL already declared]
- [Source: backend/pyproject.toml — current deps (redis[asyncio] NOT yet present — must be added)]
- [Source: frontend/package.json — zustand@^5.0, @tanstack/react-query@^5.0 available]
- [Source: frontend/src/lib/api.ts — apiClient with auto-unwrapping interceptor]
- [Source: frontend/src/app/providers.tsx — QueryClientProvider; extend with FeatureFlagHydrator]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- **redis-py type annotations:** `aioredis.Redis` in redis-py 7.3.0 is NOT generic (no `Generic[_StrType]`). Attempted `Redis[str]` — mypy returned `"Redis" expects no type arguments`. Used `Any` type annotation for `get_valkey()` return and `valkey` parameter throughout to satisfy `mypy --strict`. This is a known limitation of redis-py's type stubs in this version.
- **`type: ignore[type-arg]` was previously "unused":** Initial attempt used `# type: ignore[type-arg]` which mypy reported as "Unused type: ignore comment [unused-ignore]" — confirmed the type annotation without generics works fine.
- **`.env` file created for Docker Compose:** The project had no `.env` file. Docker Compose failed to read `POSTGRES_USER`/`POSTGRES_PASSWORD` variables. Created `.env` from `.env.example` content. Also fixed `CORS_ORIGINS` format from `http://localhost:5173` (plain string) to `["http://localhost:5173"]` (JSON array) — pydantic-settings v2 requires JSON format for `list[str]` fields from env vars.
- **`json.loads()` returns `Any`:** `mypy --strict` flags `no-any-return` on `return json.loads(cached)` in service. Fixed using `cast(FeatureFlagsDict, json.loads(cached))` with `from typing import cast`.
- **TanStack Query v5 — no `onSuccess`:** Story notes warned this. Used `useEffect` watching `data` to call `setFlags(data)` in `FeatureFlagHydrator`. Providers test still passes (renders children without crashing).

### Completion Notes List

- ✅ `backend/pyproject.toml` — added `redis[asyncio]>=5.0` (actual install: redis-7.3.0)
- ✅ `backend/alembic/versions/0002_tenant_feature_flags.py` — migration with 7 bool flag columns, UUID PK, FK to tenants.id CASCADE, `updated_at` TIMESTAMPTZ. Revision chain: 0001 → 0002
- ✅ `backend/app/models/feature_flags.py` — `TenantFeatureFlags(Base)` with 7 bool flags + `updated_at`. No TenantMixin (tenant_id IS the PK)
- ✅ `backend/app/models/__init__.py` — added `feature_flags` import for Alembic autogenerate detection
- ✅ `backend/app/schemas/feature_flags.py` — `FeatureFlagsDict(TypedDict)`, `DEFAULT_FLAGS` (all False), `FeatureFlagsResponse(BaseModel)` with `alias_generator=to_camel`
- ✅ `backend/app/db/valkey.py` — `get_valkey()` async generator dependency, `VALKEY_FLAG_TTL = 60`
- ✅ `backend/app/repositories/feature_flags.py` — `get_feature_flags_from_db(tenant_id, db)` with `scalar_one_or_none()` and DEFAULT_FLAGS fallback
- ✅ `backend/app/services/feature_flags.py` — Valkey cache-first service, silent error handling on both Valkey read and write failures
- ✅ `backend/app/api/v1/routes/tenants.py` — `GET /{tenant_id}/features` endpoint, `DataResponse[FeatureFlagsResponse]` envelope, auth TODO comment for Epic 2
- ✅ `frontend/src/lib/featureFlagStore.ts` — Zustand v5 store, `FeatureFlagKey` union type, all 7 flags default false, `setFlags(Partial<FeatureFlagsData>)`
- ✅ `frontend/src/shared/hooks/useFeatureFlag.ts` — single-line hook returning `state[flag]`
- ✅ `frontend/src/shared/components/FeatureGate.tsx` — renders children/fallback based on flag value
- ✅ `frontend/src/app/providers.tsx` — `FeatureFlagHydrator` with `useQuery` + `useEffect`, `staleTime: 55_000`, tenantId stubbed null until Epic 2
- ✅ `.env` — created from `.env.example` (CORS_ORIGINS in JSON format for pydantic-settings v2)
- ✅ **42 backend tests pass** (mypy strict ✓, ruff ✓, pytest 42/42 ✓)
- ✅ **17 frontend tests pass** (tsc ✓, eslint ✓, vitest 17/17 ✓)
- ✅ No regressions — all existing tests continue to pass

### File List

**Created:**
- `backend/alembic/versions/0002_tenant_feature_flags.py`
- `backend/app/models/feature_flags.py`
- `backend/app/schemas/feature_flags.py`
- `backend/app/db/valkey.py`
- `backend/app/repositories/feature_flags.py`
- `backend/app/services/feature_flags.py`
- `backend/tests/unit/services/__init__.py`
- `backend/tests/unit/schemas/test_feature_flags.py`
- `backend/tests/unit/services/test_feature_flags_service.py`
- `backend/tests/integration/routes/test_tenants_features.py`
- `frontend/src/lib/featureFlagStore.ts`
- `frontend/src/shared/hooks/useFeatureFlag.ts`
- `frontend/src/shared/components/FeatureGate.tsx`
- `frontend/src/lib/featureFlagStore.test.ts`
- `frontend/src/shared/components/FeatureGate.test.tsx`
- `.env`

**Modified:**
- `backend/pyproject.toml` — added `redis[asyncio]>=5.0`
- `backend/app/models/__init__.py` — added `feature_flags` import
- `backend/app/api/v1/routes/tenants.py` — implemented `GET /{tenant_id}/features` endpoint
- `frontend/src/app/providers.tsx` — added `FeatureFlagHydrator` component
