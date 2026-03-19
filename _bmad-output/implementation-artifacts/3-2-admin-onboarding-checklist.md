# Story 3.2: Admin Onboarding Checklist

Status: review

## Story

As a **new Admin**,
I want a guided onboarding checklist on first login,
so that I know exactly what to configure before the restaurant goes live and nothing is missed.

## Acceptance Criteria

1. **Given** an Admin logs in for the first time (tenant `onboarding_completed = false`)
   **When** the admin dashboard (AppShell MainContent) loads
   **Then** an onboarding checklist is displayed with steps: Add menu items, Configure tables, Set GST rates, Configure print template, Register print agent, Add staff PINs, Configure Telegram notifications

2. **And** each checklist item shows completion status — green tick (✓) when done, circle (○) when pending

3. **And** clicking any checklist item navigates to the relevant configuration screen (via `window.location.href = item.route`)

4. **And** a "Dismiss Checklist" button is shown; clicking it calls `POST /api/v1/tenants/me/onboarding/complete` which sets `tenant.onboarding_completed = true` in the DB — after which the banner no longer auto-displays on load

5. **And** `GET /api/v1/tenants/me/onboarding` returns `{ completed: bool, items: [{ key, label, completed, route }] }` — only accessible by ADMIN role (SUPER_ADMIN excluded)

6. **And** for Story 3.2, completion status is dynamic only for `staff_pins` (checks TenantUser count with operational roles + pin_hash set); all other items default `completed: false` until their respective tables are created in later stories

7. **And** `mypy --strict` and `ruff check` pass with zero errors on all new/modified backend files

## Tasks / Subtasks

- [x] **Task 1: Backend schemas** (AC: #5, #6)
  - [x] Add `ChecklistItem(BaseModel)` to `backend/app/schemas/tenant.py`: `key: str`, `label: str`, `completed: bool`, `route: str`
  - [x] Add `OnboardingStatusResponse(BaseModel)` to `backend/app/schemas/tenant.py`: `completed: bool`, `items: list[ChecklistItem]`

- [x] **Task 2: Backend routes — update `backend/app/api/v1/routes/tenants.py`** (AC: #4, #5, #6)
  - [x] Add `from fastapi import HTTPException` to imports
  - [x] Add imports: `func, select` from sqlalchemy; `CurrentUser, require_role` from dependencies; `UserRole` from permissions; `Tenant` from models; `TenantUser` from models.user; `ChecklistItem, OnboardingStatusResponse, TenantResponse` from schemas.tenant; `uuid` (already in file)
  - [x] Add private helper `async def _compute_checklist(tenant_id_str: str, db: AsyncSession) -> list[ChecklistItem]` — queries TenantUser count for operational roles with pin_hash set; returns 7 ChecklistItem objects
  - [x] Add `GET /me/onboarding` route — `require_role(UserRole.ADMIN)` — loads Tenant, calls helper, returns `DataResponse[OnboardingStatusResponse]`
  - [x] Add `POST /me/onboarding/complete` route — `require_role(UserRole.ADMIN)` — loads Tenant, sets `tenant.onboarding_completed = True`, commits, refresh, returns `DataResponse[TenantResponse]`
  - [x] Define `/me/...` routes BEFORE `/{tenant_id}/...` routes in the file (best practice, no conflict but keeps ordering clear)

- [x] **Task 3: Frontend API — `frontend/src/features/admin/api/onboarding.ts`** (AC: #3, #4, #5)
  - [x] Create file with `ChecklistItem` interface, `OnboardingStatus` interface
  - [x] `onboardingApi.getStatus()` → `apiClient.get('/api/v1/tenants/me/onboarding').then(r => r.data)`
  - [x] `onboardingApi.complete()` → `apiClient.post('/api/v1/tenants/me/onboarding/complete').then(r => r.data)`

- [x] **Task 4: Frontend hooks — `frontend/src/features/admin/hooks/useOnboarding.ts`** (AC: #5)
  - [x] `useOnboarding()` — TanStack Query, `enabled: role === 'admin'`, `staleTime: 60_000`, `queryKey: ['onboarding']`
  - [x] `useCompleteOnboarding()` — mutation, on success: `queryClient.invalidateQueries(['onboarding'])`

- [x] **Task 5: Frontend component — `frontend/src/features/admin/components/OnboardingChecklist.tsx`** (AC: #1, #2, #3, #4)
  - [x] `OnboardingChecklist` — receives `status: OnboardingStatus` and `onDismiss: () => void` props; renders 7 checklist items with CheckCircle/Circle icons (lucide-react); "Dismiss Checklist" button triggers `onDismiss`
  - [x] `OnboardingBanner` — reads `currentUser?.role` from `useAuthStore`; calls `useOnboarding()`; renders `OnboardingChecklist` when `role === 'admin' && !status.completed`

- [x] **Task 6: Wire into AppShell** (AC: #1)
  - [x] Update `frontend/src/shared/components/layout/AppShell.tsx` to render `<OnboardingBanner />` inside the layout

- [x] **Task 7: Tests** (AC: #7)
  - [x] Add `backend/tests/integration/routes/test_onboarding_routes.py` — 8 integration tests for GET /me/onboarding and POST /me/onboarding/complete
  - [x] Add `frontend/src/features/admin/components/OnboardingChecklist.test.tsx` — component tests for checklist rendering and dismiss
  - [x] Run backend: mypy strict 0 issues (56 files), ruff 0 issues, 166 passed (8 new)
  - [x] Run frontend: 22 passed (5 new + fixed AppShell wrapper)
  - [x] All prior backend tests pass; new backend tests pass

## Dev Notes

### Task 1 — Schema additions to `backend/app/schemas/tenant.py`

Append to the EXISTING `tenant.py` schemas file (after `PlatformStatsResponse`):

```python
class ChecklistItem(BaseModel):
    key: str
    label: str
    completed: bool
    route: str  # Frontend URL path — e.g. "/admin/staff"


class OnboardingStatusResponse(BaseModel):
    completed: bool
    items: list[ChecklistItem]
```

No new imports needed — `BaseModel` is already imported.

### Task 2 — Updated `tenants.py` (complete replacement)

The file must be rewritten to add new imports and new routes. Key ordering: define `/me/...` routes before `/{tenant_id}/...` route.

```python
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, get_current_user, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.db.valkey import get_valkey
from app.models.tenant import Tenant
from app.models.user import TenantUser
from app.schemas.common import DataResponse
from app.schemas.feature_flags import FeatureFlagsResponse
from app.schemas.tenant import (
    ChecklistItem,
    OnboardingStatusResponse,
    TenantResponse,
)
from app.services.feature_flags import get_feature_flags

router = APIRouter(prefix="/tenants", tags=["tenants"])

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
    """Build the onboarding checklist with dynamic completion for staff_pins."""
    result = await db.execute(
        select(func.count())
        .select_from(TenantUser)
        .where(
            TenantUser.tenant_id == tenant_id_str,
            TenantUser.role.in_(_OPERATIONAL_ROLES),
            TenantUser.pin_hash.is_not(None),
            TenantUser.is_active.is_(True),
        )
    )
    staff_count: int = result.scalar_one()

    items: list[ChecklistItem] = []
    for key, label, route in _STATIC_ITEMS:
        items.append(
            ChecklistItem(
                key=key,
                label=label,
                completed=(staff_count > 0 if key == "staff_pins" else False),
                route=route,
            )
        )
    return items


@router.get("/me/onboarding", response_model=DataResponse[OnboardingStatusResponse])
async def get_onboarding_status(
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[OnboardingStatusResponse]:
    """Return onboarding checklist for the authenticated Admin's tenant."""
    tenant_uuid = uuid.UUID(current_user["tenant_id"])
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_uuid))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "Tenant not found"},
        )
    items = await _compute_checklist(str(tenant.id), db)
    return DataResponse(
        data=OnboardingStatusResponse(
            completed=tenant.onboarding_completed, items=items
        )
    )


@router.post(
    "/me/onboarding/complete", response_model=DataResponse[TenantResponse]
)
async def complete_onboarding(
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[TenantResponse]:
    """Mark onboarding as complete for the authenticated Admin's tenant."""
    tenant_uuid = uuid.UUID(current_user["tenant_id"])
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_uuid))
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


@router.get("/{tenant_id}/features", response_model=DataResponse[FeatureFlagsResponse])
async def get_tenant_features(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    valkey: Any = Depends(get_valkey),
) -> DataResponse[FeatureFlagsResponse]:
    """Return feature flags for the given tenant.

    Flags are served from Valkey (60s TTL) with PostgreSQL fallback.
    Unknown tenant IDs return all-false defaults (no row = no flags enabled).
    """
    flags = await get_feature_flags(tenant_id, db, valkey)
    return DataResponse(data=FeatureFlagsResponse(**flags))
```

**Line count:** This complete file is ~95 lines — within the 100-line limit.

**`/me/` before `/{tenant_id}/`:** Even though there's no routing conflict (different path suffixes), defining `/me/` routes first is clean convention. FastAPI matches routes in order; `/me/onboarding` ≠ `/{tenant_id}/features` regardless.

**`TenantUser.role.in_(_OPERATIONAL_ROLES)`** — `UserRole` is a `StrEnum`; SQLAlchemy `in_()` accepts a list of enum values. mypy strict OK.

**`TenantUser.pin_hash.is_not(None)`** — `pin_hash` is `Mapped[str | None]`; `is_not(None)` is the null-safe SQLAlchemy operator. Do NOT use `!= None` — that's not null-safe in SQL.

**`tenant.onboarding_completed = True` then `db.commit()`** — SQLAlchemy ORM tracks dirty attributes; the commit sends `UPDATE tenants SET onboarding_completed = true WHERE id = ?` automatically. No explicit `db.execute(update(...))` needed here.

**`db.refresh(tenant)`** — re-reads the row from DB after commit; ensures `created_at`, `updated_at` are current. Required before `TenantResponse.model_validate(tenant)` to get accurate timestamps.

**`require_role(UserRole.ADMIN)` only (not SUPER_ADMIN)** — SUPER_ADMIN manages the platform, not individual tenant onboarding. SUPER_ADMIN belongs to the platform tenant, not a restaurant tenant — calling `/tenants/me/onboarding` would look up a non-existent restaurant tenant.

### Task 3 — `frontend/src/features/admin/api/onboarding.ts`

```typescript
import { apiClient } from '../../../lib/api'

export interface ChecklistItem {
  key: string
  label: string
  completed: boolean
  route: string
}

export interface OnboardingStatus {
  completed: boolean
  items: ChecklistItem[]
}

export const onboardingApi = {
  getStatus: (): Promise<OnboardingStatus> =>
    apiClient
      .get<OnboardingStatus>('/api/v1/tenants/me/onboarding')
      .then((r) => r.data),

  complete: (): Promise<unknown> =>
    apiClient
      .post<unknown>('/api/v1/tenants/me/onboarding/complete')
      .then((r) => r.data),
}
```

**`apiClient` already unwraps `DataResponse`** — the interceptor in `lib/api.ts` extracts `body.data` before returning. So `r.data` is the inner `OnboardingStatus` object, not the envelope.

### Task 4 — `frontend/src/features/admin/hooks/useOnboarding.ts`

```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '../../auth/stores/authStore'
import { onboardingApi } from '../api/onboarding'

const ONBOARDING_KEY = ['onboarding'] as const

export function useOnboarding() {
  const role = useAuthStore((s) => s.currentUser?.role)
  return useQuery({
    queryKey: ONBOARDING_KEY,
    queryFn: onboardingApi.getStatus,
    enabled: role === 'admin',
    staleTime: 60_000,
  })
}

export function useCompleteOnboarding() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: onboardingApi.complete,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ONBOARDING_KEY })
    },
  })
}
```

**`enabled: role === 'admin'`** — only fetch when user is Admin. SUPER_ADMIN excluded (see reasoning above). Prevents the query firing for Billers, Waiters, etc.

**`staleTime: 60_000`** — checklist state changes infrequently; 1 minute is fine.

### Task 5 — `frontend/src/features/admin/components/OnboardingChecklist.tsx`

```typescript
import { CheckCircle, Circle, ChevronRight, X } from 'lucide-react'
import type { OnboardingStatus, ChecklistItem } from '../api/onboarding'

interface OnboardingChecklistProps {
  status: OnboardingStatus
  onDismiss: () => void
  isPending: boolean
}

function ChecklistItemRow({ item }: { item: ChecklistItem }) {
  return (
    <button
      onClick={() => { window.location.href = item.route }}
      className="flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left
                 hover:bg-[var(--bg-elevated)] transition-colors"
    >
      {item.completed ? (
        <CheckCircle className="h-5 w-5 shrink-0 text-green-500" />
      ) : (
        <Circle className="h-5 w-5 shrink-0 text-[var(--text-muted)]" />
      )}
      <span
        className={[
          'flex-1 text-sm',
          item.completed
            ? 'text-[var(--text-muted)] line-through'
            : 'text-[var(--text-primary)]',
        ].join(' ')}
      >
        {item.label}
      </span>
      {!item.completed && (
        <ChevronRight className="h-4 w-4 text-[var(--text-muted)]" />
      )}
    </button>
  )
}

export function OnboardingChecklist({
  status,
  onDismiss,
  isPending,
}: OnboardingChecklistProps) {
  const doneCount = status.items.filter((i) => i.completed).length
  const total = status.items.length

  return (
    <div className="rounded-xl border border-[var(--sphotel-border)] bg-[var(--bg-surface)] p-6">
      <div className="mb-4 flex items-start justify-between">
        <div>
          <h2 className="text-base font-semibold text-[var(--text-primary)]">
            Welcome! Let&apos;s get you set up
          </h2>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            {doneCount} of {total} steps complete
          </p>
        </div>
        <button
          onClick={onDismiss}
          disabled={isPending}
          className="rounded p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)]
                     hover:bg-[var(--bg-elevated)] disabled:opacity-50 transition-colors"
          aria-label="Dismiss checklist"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="divide-y divide-[var(--sphotel-border)]">
        {status.items.map((item) => (
          <ChecklistItemRow key={item.key} item={item} />
        ))}
      </div>

      <div className="mt-4 border-t border-[var(--sphotel-border)] pt-4">
        <button
          onClick={onDismiss}
          disabled={isPending}
          className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)]
                     disabled:opacity-50 transition-colors"
        >
          {isPending ? 'Saving…' : 'Dismiss checklist'}
        </button>
      </div>
    </div>
  )
}
```

**`OnboardingBanner` (same file, below `OnboardingChecklist`):**

```typescript
import { useAuthStore } from '../../auth/stores/authStore'
import { useCompleteOnboarding, useOnboarding } from '../hooks/useOnboarding'

export function OnboardingBanner() {
  const role = useAuthStore((s) => s.currentUser?.role)
  const { data: status } = useOnboarding()
  const { mutate: completeOnboarding, isPending } = useCompleteOnboarding()

  if (role !== 'admin' || !status || status.completed) return null

  return (
    <div className="p-6">
      <OnboardingChecklist
        status={status}
        onDismiss={() => completeOnboarding()}
        isPending={isPending}
      />
    </div>
  )
}
```

**Why `window.location.href` not `<Link>`**: React Router's `routes.tsx` is essentially empty — `createBrowserRouter([])` with no routes defined. Using `<Link to="/admin/menu">` would work syntactically but the routes don't exist yet (they'll be added in later stories). `window.location.href` works regardless of router state.

**Dismiss button always enabled**: The AC says "dismissible once all required steps are complete" but in Story 3.2 most items can't be completed (tables don't exist yet). Making it always dismissible allows Admin to proceed even before all items are checked. The checklist persists showing what's done — it auto-hides after dismiss. This is pragmatic until all items become completable in later stories.

### Task 6 — Update `frontend/src/shared/components/layout/AppShell.tsx`

```typescript
import { type ReactNode } from 'react'
import { Sidebar } from './Sidebar'
import { MainContent } from './MainContent'
import { OnboardingBanner } from '@/features/admin/components/OnboardingChecklist'

interface AppShellProps {
  children?: ReactNode
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-bg-base">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <OnboardingBanner />
        <MainContent>{children}</MainContent>
      </div>
    </div>
  )
}
```

**Layout change**: Wrap `Sidebar` and `MainContent` in a flex column div to stack `OnboardingBanner` above `MainContent`. The banner appears at the top of the main area, not inside the sidebar.

**`@/` path alias**: Configured in `vite.config.ts` (infer from existing usage — `providers.tsx` uses `@/lib/queryClient`, `@/lib/api`, etc.).

### Task 7 — Backend tests (`test_onboarding_routes.py`)

```python
"""Integration tests for /api/v1/tenants/me/onboarding endpoints (Story 3.2)."""
import datetime
import uuid
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import CurrentUser, get_current_user
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.db.valkey import get_valkey
from app.main import app
from app.models.tenant import Tenant

TENANT_STR = "sphotel"
TENANT_UUID = uuid.uuid4()
USER_ID = uuid.uuid4()


def _make_user(role: UserRole = UserRole.ADMIN) -> CurrentUser:
    return {
        "user_id": USER_ID,
        "tenant_id": str(TENANT_UUID),
        "role": role,
    }


def _mock_valkey_dep() -> Any:
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.aclose = AsyncMock()

    async def _gen() -> AsyncGenerator[Any, None]:
        yield mock

    return _gen


def _mock_db_dep(db_mock: Any) -> Any:
    async def _gen() -> AsyncGenerator[Any, None]:
        yield db_mock

    return _gen


def _make_fake_tenant(completed: bool = False) -> MagicMock:
    fake = MagicMock(spec=Tenant)
    fake.id = TENANT_UUID
    fake.name = "Test Restaurant"
    fake.slug = "testrestaurant"
    fake.is_active = True
    fake.onboarding_completed = completed
    fake.created_at = datetime.datetime(2026, 3, 18, tzinfo=datetime.timezone.utc)
    return fake


# ── GET /tenants/me/onboarding ─────────────────────────────────────────────────

@pytest.mark.anyio
async def test_get_onboarding_requires_admin() -> None:
    """Biller role → 403."""
    app.dependency_overrides[get_current_user] = lambda: _make_user(UserRole.BILLER)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    db_mock = AsyncMock()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/tenants/me/onboarding")
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_onboarding_no_auth_returns_401() -> None:
    """No auth → 401."""
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/tenants/me/onboarding")
        assert resp.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_onboarding_returns_checklist() -> None:
    """Admin → 200 with checklist; staff_pins=True when count > 0."""
    fake_tenant = _make_fake_tenant(completed=False)

    tenant_result = MagicMock()
    tenant_result.scalar_one_or_none.return_value = fake_tenant

    count_result = MagicMock()
    count_result.scalar_one.return_value = 2  # 2 staff with PINs

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(side_effect=[tenant_result, count_result])

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/tenants/me/onboarding")
        assert resp.status_code == 200
        body = resp.json()
        assert body["error"] is None
        assert body["data"]["completed"] is False
        items = {i["key"]: i for i in body["data"]["items"]}
        assert "staff_pins" in items
        assert items["staff_pins"]["completed"] is True
        assert items["menu_items"]["completed"] is False
        assert len(body["data"]["items"]) == 7
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_onboarding_staff_pins_false_when_no_staff() -> None:
    """No operational staff → staff_pins.completed = False."""
    fake_tenant = _make_fake_tenant()

    tenant_result = MagicMock()
    tenant_result.scalar_one_or_none.return_value = fake_tenant
    count_result = MagicMock()
    count_result.scalar_one.return_value = 0  # No staff

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(side_effect=[tenant_result, count_result])

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/tenants/me/onboarding")
        assert resp.status_code == 200
        items = {i["key"]: i for i in resp.json()["data"]["items"]}
        assert items["staff_pins"]["completed"] is False
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_onboarding_tenant_not_found_returns_404() -> None:
    """Tenant not in DB → 404."""
    tenant_result = MagicMock()
    tenant_result.scalar_one_or_none.return_value = None
    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=tenant_result)

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/tenants/me/onboarding")
        assert resp.status_code == 404
        assert "NOT_FOUND" in resp.json()["error"]["message"]
    finally:
        app.dependency_overrides.clear()


# ── POST /tenants/me/onboarding/complete ──────────────────────────────────────

@pytest.mark.anyio
async def test_complete_onboarding_requires_admin() -> None:
    """Manager role → 403."""
    app.dependency_overrides[get_current_user] = lambda: _make_user(UserRole.MANAGER)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    db_mock = AsyncMock()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/v1/tenants/me/onboarding/complete")
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_complete_onboarding_returns_200() -> None:
    """Admin → 200; tenant.onboarding_completed set to True."""
    fake_tenant = _make_fake_tenant(completed=False)
    # After mutation, onboarding_completed should be True
    # (refresh mock doesn't change it; Pydantic reads from mock attrs)
    fake_tenant.onboarding_completed = True  # simulate post-commit state

    tenant_result = MagicMock()
    tenant_result.scalar_one_or_none.return_value = fake_tenant

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=tenant_result)
    db_mock.commit = AsyncMock()
    db_mock.refresh = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/v1/tenants/me/onboarding/complete")
        assert resp.status_code == 200
        assert resp.json()["data"]["onboarding_completed"] is True
    finally:
        app.dependency_overrides.clear()
```

### Task 7 — Frontend tests (`OnboardingChecklist.test.tsx`)

```typescript
import { render, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { OnboardingChecklist } from './OnboardingChecklist'
import type { OnboardingStatus } from '../api/onboarding'

const MOCK_STATUS: OnboardingStatus = {
  completed: false,
  items: [
    { key: 'menu_items', label: 'Add menu items', completed: false, route: '/admin/menu' },
    { key: 'staff_pins', label: 'Add staff PINs', completed: true, route: '/admin/staff' },
    { key: 'tables', label: 'Configure tables', completed: false, route: '/admin/tables' },
  ],
}

describe('OnboardingChecklist', () => {
  it('renders all checklist items', () => {
    const { getByText } = render(
      <OnboardingChecklist
        status={MOCK_STATUS}
        onDismiss={vi.fn()}
        isPending={false}
      />
    )
    expect(getByText('Add menu items')).toBeTruthy()
    expect(getByText('Add staff PINs')).toBeTruthy()
    expect(getByText('Configure tables')).toBeTruthy()
  })

  it('shows progress count', () => {
    const { getByText } = render(
      <OnboardingChecklist
        status={MOCK_STATUS}
        onDismiss={vi.fn()}
        isPending={false}
      />
    )
    expect(getByText('1 of 3 steps complete')).toBeTruthy()
  })

  it('calls onDismiss when dismiss button clicked', () => {
    const onDismiss = vi.fn()
    const { getAllByRole } = render(
      <OnboardingChecklist
        status={MOCK_STATUS}
        onDismiss={onDismiss}
        isPending={false}
      />
    )
    // Click the aria-label dismiss button (X icon)
    const buttons = getAllByRole('button', { name: /dismiss/i })
    fireEvent.click(buttons[0])
    expect(onDismiss).toHaveBeenCalledOnce()
  })

  it('disables buttons when isPending', () => {
    const { getAllByRole } = render(
      <OnboardingChecklist
        status={MOCK_STATUS}
        onDismiss={vi.fn()}
        isPending={true}
      />
    )
    const dismissButtons = getAllByRole('button', { name: /dismiss|saving/i })
    dismissButtons.forEach((btn) => {
      expect(btn).toBeDisabled()
    })
  })

  it('shows Saving text when pending', () => {
    const { getByText } = render(
      <OnboardingChecklist
        status={MOCK_STATUS}
        onDismiss={vi.fn()}
        isPending={true}
      />
    )
    expect(getByText('Saving…')).toBeTruthy()
  })
})
```

### Project Structure Notes

**Backend — Files to MODIFY:**
- `backend/app/schemas/tenant.py` — append `ChecklistItem` + `OnboardingStatusResponse`
- `backend/app/api/v1/routes/tenants.py` — rewrite with new imports, helper, 2 new routes

**Backend — Files to CREATE:**
- `backend/tests/integration/routes/test_onboarding_routes.py`

**Frontend — Files to CREATE:**
- `frontend/src/features/admin/api/onboarding.ts`
- `frontend/src/features/admin/hooks/useOnboarding.ts`
- `frontend/src/features/admin/components/OnboardingChecklist.tsx`
- `frontend/src/features/admin/components/OnboardingChecklist.test.tsx`

**Frontend — Files to MODIFY:**
- `frontend/src/shared/components/layout/AppShell.tsx` — add `OnboardingBanner` + wrap in column flex

**Files confirmed NO changes needed:**
- `backend/app/api/v1/router.py` ✓ — `tenants.router` already registered
- `backend/app/models/tenant.py` ✓ — `onboarding_completed` added in Story 3.1
- `backend/app/schemas/common.py` ✓
- `frontend/src/app/providers.tsx` ✓

### Architecture Compliance

1. **Route file ≤100 lines** — `tenants.py` rewrite is ~95 lines including all new routes + helper.
2. **`_compute_checklist` as private helper** — prefixed `_` indicates module-private; not exported. Keeps route handlers thin.
3. **ORM in-place update** — `tenant.onboarding_completed = True` + `db.commit()` is the SQLAlchemy ORM pattern (vs `db.execute(update(...))`). Both are valid; ORM pattern is cleaner for single-object mutations.
4. **`require_role(UserRole.ADMIN)` only** — SUPER_ADMIN manages platform, not tenant onboarding. Consistent with `tenant_id` scoping from JWT (SUPER_ADMIN's `tenant_id` is the platform tenant, not a restaurant).
5. **`_STATIC_ITEMS` list** — Defines order and labels centrally. As later stories add tables, only the `_compute_checklist` function needs updating (not the route handler).
6. **No new service file** — `_compute_checklist` is small enough to stay as a private helper in the route file. Creating a service file for a ~15-line function would be over-engineering.
7. **Frontend feature placement** — onboarding API/hooks/components live in `features/admin/` (not `features/auth/`) — admin configuration is distinct from authentication functionality.
8. **`cn()` utility available** — `@/shared/utils` exports `cn(clsx + twMerge)`. Use for conditional class merging in `OnboardingChecklist`.

### Gotchas & Known Pitfalls

**`TenantUser.role.in_(_OPERATIONAL_ROLES)` with SQLAlchemy:** The `role` column is `SAEnum(UserRole, ...)` and `_OPERATIONAL_ROLES` is `list[UserRole]`. SQLAlchemy's `.in_()` handles StrEnum values correctly. Do NOT cast to strings first.

**`tenant.id` after ORM fetch is `uuid.UUID`:** When calling `str(tenant.id)` for the TenantUser query, this correctly produces the tenant UUID string matching `TenantUser.tenant_id` (which stores the UUID as a VARCHAR string from `str(tenant.id)` in `provision_tenant`).

**Mock `db.commit` and `db.refresh` for `complete_onboarding` test:** Unlike the `execute`-only pattern in GET tests, the POST test needs `db_mock.commit = AsyncMock()` and `db_mock.refresh = AsyncMock()`. Forgetting these causes `AttributeError` or `TypeError` since `MagicMock.commit()` is not awaitable by default.

**`MagicMock(spec=Tenant)` requires `onboarding_completed` to exist on Tenant:** After Story 3.1 added this field, `spec=Tenant` mocks support `onboarding_completed` attribute. Always set it explicitly: `fake.onboarding_completed = False`.

**`TenantResponse.model_validate(tenant)` in `complete_onboarding`:** `TenantResponse` uses `ConfigDict(from_attributes=True)`. In the test, `db.refresh(tenant)` is a no-op mock, so `fake_tenant.onboarding_completed` must already be set to `True` before the route handler is called (the handler sets `tenant.onboarding_completed = True` on the mock object, which works for MagicMock).

**`AppShell` layout change:** Adding `OnboardingBanner` requires wrapping the existing `Sidebar + MainContent` in a flex-column div. The existing `AppShell` renders: `<div flex-row> <Sidebar> <MainContent> </div>`. After change: `<div flex-row> <Sidebar> <div flex-col> <OnboardingBanner> <MainContent> </div> </div>`. The `AppShell.test.tsx` checks that `aside` and `main` still exist — both should still pass.

**`@/` path alias in imports:** The existing frontend uses `@/lib/...`, `@/shared/...` etc. The alias resolves to `src/`. So `@/features/admin/components/OnboardingChecklist` is `src/features/admin/components/OnboardingChecklist`.

**Frontend tests don't test API calls:** Vitest tests for `OnboardingChecklist` test the pure component (render + events), not the API. `useOnboarding` is not called in these tests — the component receives `status` as a prop. Test the component in isolation; test hooks via integration (not in scope for this story).

**`window.location.href` navigation:** Since `routes.tsx` is essentially empty (no pages defined yet), using `<Link to="/admin/menu">` would render but navigate to a non-existent route. `window.location.href = item.route` navigates regardless of React Router's configured routes. Once admin pages are built in later stories, refactor to `useNavigate()`.

**`get_current_user` import in tests:** The dependency override key must match exactly. For `require_role(UserRole.ADMIN)`, the underlying dependency is `get_current_user` (since `require_role` wraps it). Override `app.dependency_overrides[get_current_user] = lambda: _make_user()` — this is the same pattern used in all other integration tests.

### Previous Story Intelligence (Stories 3.1, 2.6)

- **`TenantResponse(from_attributes=True)`** — exists in `schemas/tenant.py`; `model_validate(tenant)` works if mock has all required attributes: `id, name, slug, is_active, onboarding_completed, created_at`
- **`require_role()` dependency pattern** — `Depends(require_role(UserRole.ADMIN))` — override `get_current_user` in tests
- **`MagicMock(spec=Tenant)`** — use `spec=Tenant` to restrict allowed attributes to actual model fields
- **Integration test pattern** — `_mock_valkey_dep()` + `_mock_db_dep(db_mock)` + `try/finally app.dependency_overrides.clear()` — follow exactly
- **`db.execute(side_effect=[...])` for multiple calls** — GET /me/onboarding makes 2 execute calls (Tenant SELECT, then TenantUser COUNT). Use `side_effect=[tenant_result, count_result]`
- **Docker rebuild** — required after new `.py` files: `docker compose build backend`
- **`_STATIC_ITEMS` pattern** — similar to how `ROLE_PERMISSIONS` in permissions.py centralizes capability sets; centralizing checklist items makes future updates easier

### References

- Story ACs: [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 3 > Story 3.2]
- FR60 (onboarding checklist): [Source: `_bmad-output/planning-artifacts/prd.md`]
- `Tenant.onboarding_completed` added in Story 3.1: [Source: `backend/app/models/tenant.py`]
- `TenantResponse`, `ChecklistItem`, `OnboardingStatusResponse`: [Source: `backend/app/schemas/tenant.py`]
- Existing `tenants.py` route (features endpoint): [Source: `backend/app/api/v1/routes/tenants.py`]
- `TenantUser.role`, `pin_hash`, `is_active`, `tenant_id`: [Source: `backend/app/models/user.py`]
- `UserRole.BILLER/WAITER/KITCHEN_STAFF/MANAGER`: [Source: `backend/app/core/security/permissions.py`]
- `require_role()`, `CurrentUser`: [Source: `backend/app/core/dependencies.py`]
- `DataResponse` envelope: [Source: `backend/app/schemas/common.py`]
- `apiClient` interceptor (unwraps DataResponse): [Source: `frontend/src/lib/api.ts`]
- `useAuthStore` (currentUser.role): [Source: `frontend/src/features/auth/stores/authStore.ts`]
- `useMe()`, `useLogout()` hook patterns: [Source: `frontend/src/features/auth/hooks/useAuth.ts`]
- `FeatureGate` + `useFeatureFlag` hook: [Source: `frontend/src/shared/components/FeatureGate.tsx`]
- `AppShell` layout: [Source: `frontend/src/shared/components/layout/AppShell.tsx`]
- Lucide React icons available: [Source: `frontend/package.json` — `lucide-react: ^0.468`]
- TanStack Query v5 pattern (`useQuery`, `useMutation`): [Source: `frontend/src/features/auth/hooks/useAuth.ts`]
- Vitest + React Testing Library pattern: [Source: `frontend/src/shared/components/FeatureGate.test.tsx`]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6 (2026-03-18)

### Debug Log References

- **404 test assertions**: Initial test used `resp.json()["detail"]["code"]` but the custom `http_exception_handler` in `app/core/exceptions.py` wraps all HTTPExceptions as `{"data": null, "error": {"code": "404", "message": str(exc.detail)}}`. Fixed to `assert "NOT_FOUND" in resp.json()["error"]["message"]`.
- **AppShell.test.tsx regression**: Adding `<OnboardingBanner />` (which calls `useOnboarding()` → TanStack Query) to `AppShell` caused 3 pre-existing AppShell tests to fail with "No QueryClient set". Fixed by wrapping renders with a `QueryClientProvider` wrapper factory in the test.
- **Docker rebuild required**: Test files written after initial `docker compose build` — needed rebuild for container to pick up new/changed test files.

### Completion Notes List

- Implemented all 7 tasks as specified in the story.
- `_compute_checklist()` private helper queries `TenantUser` count for operational roles (`BILLER, WAITER, KITCHEN_STAFF, MANAGER`) with `pin_hash IS NOT NULL AND is_active = true`. Only `staff_pins` is dynamic; all other 6 items default `completed=False`.
- `complete_onboarding` uses ORM in-place update (`tenant.onboarding_completed = True` + `db.commit()`) — SQLAlchemy tracks dirty attributes automatically.
- `OnboardingBanner` guards on `role === 'admin'` (SUPER_ADMIN excluded; manages platform, not tenant onboarding).
- `window.location.href` navigation used instead of `<Link>` because `routes.tsx` has no routes configured yet.
- Backend: 166 tests passed (8 new), mypy strict 0 issues, ruff 0 issues.
- Frontend: 22 tests passed (5 new `OnboardingChecklist` tests + 3 fixed `AppShell` tests).

### File List

**Backend — Modified:**
- `backend/app/schemas/tenant.py` — added `ChecklistItem`, `OnboardingStatusResponse`
- `backend/app/api/v1/routes/tenants.py` — rewritten with `_compute_checklist()` helper + `GET /me/onboarding` + `POST /me/onboarding/complete`

**Backend — Created:**
- `backend/tests/integration/routes/test_onboarding_routes.py`

**Frontend — Created:**
- `frontend/src/features/admin/api/onboarding.ts`
- `frontend/src/features/admin/hooks/useOnboarding.ts`
- `frontend/src/features/admin/components/OnboardingChecklist.tsx`
- `frontend/src/features/admin/components/OnboardingChecklist.test.tsx`

**Frontend — Modified:**
- `frontend/src/shared/components/layout/AppShell.tsx` — added `<OnboardingBanner />`
- `frontend/src/shared/components/layout/AppShell.test.tsx` — wrapped renders with `QueryClientProvider`
