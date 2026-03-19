# Story 2.6: Per-User Display Theme Preference

Status: review

## Story

As any **authenticated user**,
I want to set my display theme (dark / high-contrast / light),
so that I can work comfortably across different lighting environments.

## Acceptance Criteria

1. **Given** any authenticated user, **When** they call `PATCH /api/v1/users/me/preferences` with `{ "theme": "dark" | "high_contrast" | "light" }`, **Then** the value is persisted to `tenant_users.preferences` JSONB column and the response returns the updated `MeResponse` (all roles permitted).

2. **And** `GET /api/v1/auth/me` returns `preferences: {"theme": "dark"}` (or empty dict `{}` when not yet set) as part of the `MeResponse` — allowing the frontend to read the stored preference after login.

3. **And** on next page load, the stored theme is applied before the first React render — no flash of wrong theme. An inline `<script>` in `index.html` reads `localStorage.getItem('sphotel-theme')` and sets `.dark` / `.high-contrast` classes on `<html>` before any React hydration.

4. **And** `prefers-color-scheme` system preference is the default when `localStorage` has no stored preference and no auth'd user preference exists. If system is dark → `.dark` class applied; if light → no class; high-contrast is only from explicit user selection.

5. **And** theme switching applies instantly (no page reload) — `applyTheme()` in `src/lib/theme.ts` sets `data-theme` on `<html>`, adds/removes `.dark` and `.high-contrast` CSS classes, and writes to `localStorage`. A `ThemeHydrator` component in `providers.tsx` watches `currentUser?.preferences?.theme` and calls `applyTheme()` reactively.

6. **And** the CSS supports three theme states: `dark` (existing default), `light` (`[data-theme="light"]` overrides in `sphotel-vars.css`), and `high_contrast` (`.high-contrast` CSS class overrides in `sphotel-vars.css`).

7. **And** a `ThemeSelector` component at `src/features/auth/components/ThemeSelector.tsx` renders three theme option buttons (Light / Dark / High Contrast) using only plain Tailwind (no shadcn/ui), calls `PATCH /users/me/preferences`, and updates the auth store on success.

8. **And** `mypy --strict` and `ruff check` pass with zero errors on all new/modified backend files.

## Tasks / Subtasks

- [x] **Task 1: Migration 0004 + Model update** (AC: #1, #2)
  - [x] Create `backend/alembic/versions/0004_add_preferences_to_tenant_users.py` — adds `preferences JSONB NOT NULL DEFAULT '{}'::jsonb` to `tenant_users`; downgrade drops the column
  - [x] Update `backend/app/models/user.py` — add `preferences: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))`; add `from sqlalchemy.dialects.postgresql import JSONB` to imports

- [x] **Task 2: Schema — `PreferencesUpdateRequest` + update `MeResponse`** (AC: #1, #2)
  - [x] Create `backend/app/schemas/users.py` with `PreferencesUpdateRequest(BaseModel)`: `theme: Literal["dark", "high_contrast", "light"]`
  - [x] Update `backend/app/schemas/auth.py` — add `preferences: dict[str, object]` field to `MeResponse`
  - [x] Update `backend/tests/integration/routes/test_auth_logout_me.py` — add `fake_user.preferences = {}` to ALL `MagicMock()` fake user instances to prevent `MeResponse.model_validate()` failures

- [x] **Task 3: `PATCH /api/v1/users/me/preferences` endpoint** (AC: #1)
  - [x] Create `backend/app/api/v1/routes/users.py`
  - [x] Update `backend/app/api/v1/router.py` — import `users` module and `api_router.include_router(users.router)`

- [x] **Task 4: Frontend CSS — light and high-contrast themes** (AC: #6)
  - [x] Update `frontend/src/styles/sphotel-vars.css` — add `[data-theme="light"]` block with light overrides and `.high-contrast` block with high-contrast overrides

- [x] **Task 5: FOUC prevention + theme utility** (AC: #3, #4, #5)
  - [x] Update `frontend/index.html` — added inline `<script>` in `<head>`; removed hardcoded `class="dark"` from `<html>` tag
  - [x] Create `frontend/src/lib/theme.ts` — `applyTheme()`, `getSystemTheme()`, `getStoredTheme()`

- [x] **Task 6: Frontend integration — ThemeHydrator + ThemeSelector** (AC: #5, #7)
  - [x] Update `frontend/src/app/providers.tsx` — added `ThemeHydrator` component
  - [x] Create `frontend/src/features/auth/components/ThemeSelector.tsx` — 3 plain Tailwind buttons with optimistic theme apply
  - [x] Extend `frontend/src/features/auth/api/auth.ts` — added `updatePreferences()` and `preferences` field to `MeResponse` interface

- [x] **Task 7: Tests** (AC: #8)
  - [x] Create `backend/tests/unit/test_user_schemas.py` — 6 unit tests for `PreferencesUpdateRequest`
  - [x] Create `backend/tests/integration/routes/test_users_routes.py` — 7 integration tests for `PATCH /users/me/preferences`
  - [x] Run: `docker compose build backend && docker compose run --rm --no-deps backend sh -c "cd /app && mypy app --strict && ruff check app && pytest"`
  - [x] All prior 124 tests pass; 137 total (13 new)

## Dev Notes

### Task 1 — Exact migration file

```python
"""add preferences jsonb to tenant_users

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-18
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tenant_users",
        sa.Column(
            "preferences",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("tenant_users", "preferences")
```

### Task 1 — `user.py` model update

```python
# Add to imports at top:
from sqlalchemy.dialects.postgresql import JSONB

# Add to TenantUser class (after is_active):
preferences: Mapped[dict[str, object]] = mapped_column(
    JSONB, nullable=False, server_default=text("'{}'::jsonb")
)
```

**`Mapped[dict[str, object]]`** — mypy strict requires `dict[str, object]` (not `dict[str, Any]`). SQLAlchemy JSONB maps to Python dict; `object` is the correct upper bound.

### Task 2 — `PreferencesUpdateRequest` exact schema

Create **`backend/app/schemas/users.py`**:

```python
from typing import Literal

from pydantic import BaseModel


class PreferencesUpdateRequest(BaseModel):
    theme: Literal["dark", "high_contrast", "light"]
```

**`Literal["dark", "high_contrast", "light"]`** — mypy strict: requires `from typing import Literal`. Pydantic validates that the value is one of the three strings; any other value → 422. `high_contrast` uses underscore (not hyphen) to match the CSS class name and avoid URL encoding issues.

### Task 2 — Update `MeResponse` in `auth.py`

Add `preferences: dict[str, object]` field to `MeResponse` **after** `is_active`:

```python
class MeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    tenant_id: str
    name: str
    role: UserRole
    email: str | None
    is_active: bool
    preferences: dict[str, object]   # ← NEW: Story 2.6
```

### Task 2 — Fix Story 2.5 test mocks (CRITICAL — prevents regressions)

In `backend/tests/integration/routes/test_auth_logout_me.py`, ALL `MagicMock()` fake user instances used with `MeResponse.model_validate()` must have `preferences` set. MagicMock auto-returns a `MagicMock` for unset attributes — Pydantic v2 `dict[str, object]` validation will fail on a MagicMock.

**Fix every fake_user mock block:**
```python
fake_user = MagicMock()
fake_user.user_id = USER_ID
# ... existing fields ...
fake_user.preferences = {}   # ← ADD THIS LINE
```

Similarly fix `backend/tests/unit/test_auth_schemas.py` — the `_FakeUser` class:
```python
class _FakeUser:
    user_id = uuid.uuid4()
    tenant_id = "sphotel"
    name = "Alice Admin"
    role = UserRole.ADMIN
    email = "alice@sphotel.com"
    is_active = True
    preferences: dict[str, object] = {}   # ← ADD THIS
```

### Task 3 — Exact `users.py` route

```python
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, get_current_user
from app.db.session import get_db
from app.models.user import TenantUser
from app.schemas.auth import MeResponse
from app.schemas.common import DataResponse
from app.schemas.users import PreferencesUpdateRequest

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me/preferences", response_model=DataResponse[MeResponse])
async def update_my_preferences(
    body: PreferencesUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[MeResponse]:
    """Update authenticated user's display preference. All roles permitted."""
    result = await db.execute(
        select(TenantUser).where(TenantUser.id == current_user["user_id"])
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "User not found"},
        )

    # Merge into existing preferences dict (preserves any future keys)
    current_prefs: dict[str, object] = dict(user.preferences or {})
    current_prefs["theme"] = body.theme

    await db.execute(
        update(TenantUser)
        .where(TenantUser.id == current_user["user_id"])
        .values(preferences=current_prefs)
    )
    await db.commit()

    result2 = await db.execute(
        select(TenantUser).where(TenantUser.id == current_user["user_id"])
    )
    user2 = result2.scalar_one()
    return DataResponse(data=MeResponse.model_validate(user2))
```

**No `require_role` here** — all 6 roles (biller through super_admin) should be able to set their own display preference. `get_current_user` alone is sufficient.

**Merging dict** — `dict(user.preferences or {})` creates a mutable copy. After merge, the entire dict is written back with `.values(preferences=current_prefs)`. This is safe for Story 2.6 (only `theme` key) and forward-compatible for future preference keys.

### Task 3 — Update `router.py`

```python
from app.api.v1.routes import (
    analytics,
    auth,
    bills,
    expenses,
    gst,
    health,
    kot,
    menu,
    payments,
    print_jobs,
    staff,
    super_admin,
    tenants,
    users,   # ← NEW
)

# After staff.router:
api_router.include_router(users.router)   # ← NEW
```

**Route resolves to `/api/v1/users/me/preferences`** — the `prefix="/users"` in `users.py` router + `/api/v1` prefix from main app.

### Task 4 — CSS additions to `sphotel-vars.css`

Append to `frontend/src/styles/sphotel-vars.css`:

```css
/* ── Light theme ───────────────────────────────────────────────────────── */
[data-theme="light"] {
  --bg-base: #ffffff;
  --bg-surface: #f4f4f5;      /* zinc-100 */
  --bg-elevated: #e4e4e7;     /* zinc-200 */
  --sphotel-border: #d4d4d8;  /* zinc-300 */
  --text-primary: #09090b;    /* zinc-950 */
  --text-secondary: #3f3f46;  /* zinc-700 */
  --text-muted: #71717a;      /* zinc-500 */
  --sphotel-accent: #7c3aed;  /* violet-600 — darker for light bg contrast */
  --sphotel-accent-hover: #6d28d9; /* violet-700 */
  --sphotel-accent-subtle: #ede9fe; /* violet-100 */
  --sphotel-accent-fg: #ffffff;
}

/* ── High contrast (applied alongside .dark) ───────────────────────────── */
.high-contrast {
  --bg-base: #000000;
  --bg-surface: #0d0d0d;
  --bg-elevated: #1a1a1a;
  --sphotel-border: #ffffff;
  --text-primary: #ffffff;
  --text-secondary: #e4e4e7;  /* zinc-200 */
  --text-muted: #a1a1aa;      /* zinc-400 */
  --sphotel-accent: #a78bfa;  /* violet-400 — higher visibility on black */
  --sphotel-accent-hover: #c4b5fd; /* violet-300 */
  --sphotel-accent-subtle: #2e1065; /* violet-950 */
  --status-success: #34d399;  /* emerald-400 — brighter */
  --status-warning: #fcd34d;  /* amber-300 — brighter */
  --status-error: #f87171;    /* red-400 — brighter */
}
```

**CSS selector strategy:**
- `dark` theme: `.dark` on `<html>` (Tailwind `dark:` utilities + shadcn `.dark` vars)
- `light` theme: `[data-theme="light"]` on `<html>` (overrides `sphotel-vars.css :root` dark defaults)
- `high_contrast` theme: `.dark` + `.high-contrast` classes on `<html>`

**Why `[data-theme="light"]` not `[data-theme="dark"]`:** The existing `:root` in `sphotel-vars.css` is already dark. The `[data-theme="light"]` selector provides the light override. This avoids duplicating the full dark token set.

### Task 5 — `index.html` inline script

Insert in `<head>`, **before the closing `</head>` tag**:

```html
<script>
  (function () {
    var t = localStorage.getItem('sphotel-theme')
    var h = document.documentElement
    h.classList.remove('dark', 'high-contrast')
    h.removeAttribute('data-theme')
    if (t === 'dark') {
      h.classList.add('dark')
      h.setAttribute('data-theme', 'dark')
    } else if (t === 'high_contrast') {
      h.classList.add('dark', 'high-contrast')
      h.setAttribute('data-theme', 'high_contrast')
    } else if (t === 'light') {
      h.setAttribute('data-theme', 'light')
    } else {
      // No stored preference — use system preference
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        h.classList.add('dark')
        h.setAttribute('data-theme', 'dark')
      } else {
        h.setAttribute('data-theme', 'light')
      }
    }
  })()
</script>
```

**Why inline (not module script):** Module scripts (`type="module"`) are deferred — they execute after HTML parsing. An inline sync `<script>` in `<head>` executes immediately, before any rendering. This eliminates FOUC.

**Hardcoded `class="dark"` in `<html>` tag:** Remove it — the inline script handles the initial class. Keeping it would cause a brief flash if the stored preference is `light`.

### Task 5 — `frontend/src/lib/theme.ts`

```typescript
export type Theme = 'dark' | 'high_contrast' | 'light'

const STORAGE_KEY = 'sphotel-theme'

export function applyTheme(theme: Theme): void {
  const html = document.documentElement
  html.classList.remove('dark', 'high-contrast')
  html.setAttribute('data-theme', theme)

  if (theme === 'dark') {
    html.classList.add('dark')
  } else if (theme === 'high_contrast') {
    html.classList.add('dark', 'high-contrast')
  }
  // 'light': no classes — [data-theme="light"] CSS handles styling

  localStorage.setItem(STORAGE_KEY, theme)
}

export function getSystemTheme(): 'dark' | 'light' {
  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light'
}

export function getStoredTheme(): Theme | null {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'dark' || stored === 'high_contrast' || stored === 'light') {
    return stored
  }
  return null
}
```

**`applyTheme` is pure** — no React dependencies; can be called from the FOUC inline script pattern and from React components alike.

### Task 6 — `ThemeHydrator` in `providers.tsx`

```typescript
import { applyTheme, getStoredTheme, getSystemTheme, type Theme } from '@/lib/theme'

function ThemeHydrator(): null {
  const preferences = useAuthStore((s) => s.currentUser?.preferences)

  useEffect(() => {
    const storedTheme = preferences?.theme as Theme | undefined
    if (storedTheme) {
      applyTheme(storedTheme)
    }
    // If no user preference, the FOUC script already applied system default
    // Nothing to do here — avoids flicker by not overriding system preference
  }, [preferences])

  return null
}
```

Add `<ThemeHydrator />` inside the `Providers` component return (alongside `<FeatureFlagHydrator />`).

**Why only apply when `storedTheme` exists:** The FOUC script already set the correct initial theme (from localStorage or system). `ThemeHydrator` only needs to act when the DB preference differs from what's cached in localStorage (e.g., user changed theme on another device). This prevents the double-apply on first load.

### Task 6 — `ThemeSelector.tsx` with `updatePreferences` API

Extend `frontend/src/features/auth/api/auth.ts` with:
```typescript
updatePreferences: (theme: 'dark' | 'high_contrast' | 'light'): Promise<MeResponse> =>
  apiClient
    .patch<MeResponse>('/api/v1/users/me/preferences', { theme })
    .then((r) => r.data),
```

`ThemeSelector.tsx` — plain Tailwind, three buttons:
```typescript
import { useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import { authApi } from '../api/auth'
import { applyTheme, type Theme } from '../../../lib/theme'

const THEMES: { value: Theme; label: string }[] = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'high_contrast', label: 'High Contrast' },
]

export function ThemeSelector() {
  const currentUser = useAuthStore((s) => s.currentUser)
  const setCurrentUser = useAuthStore((s) => s.setCurrentUser)
  const currentTheme = (currentUser?.preferences?.theme as Theme | undefined) ?? null
  const [pending, setPending] = useState(false)

  async function handleSelect(theme: Theme) {
    if (pending) return
    setPending(true)
    try {
      applyTheme(theme)  // Apply instantly (optimistic)
      const updated = await authApi.updatePreferences(theme)
      setCurrentUser(updated)
    } finally {
      setPending(false)
    }
  }

  return (
    <div className="flex gap-2">
      {THEMES.map(({ value, label }) => (
        <button
          key={value}
          onClick={() => handleSelect(value)}
          disabled={pending}
          className={[
            'px-3 py-1.5 rounded text-sm font-medium transition-colors',
            currentTheme === value
              ? 'bg-[var(--sphotel-accent)] text-white'
              : 'bg-[var(--bg-elevated)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]',
          ].join(' ')}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
```

**Optimistic apply** — `applyTheme(theme)` fires immediately before the API call. This gives instant visual feedback. If the API fails, the theme is already changed (acceptable trade-off for a non-critical preference). Could add rollback on error if desired (not required by ACs).

### Project Structure Notes

**Files to CREATE:**
- `backend/alembic/versions/0004_add_preferences_to_tenant_users.py`
- `backend/app/schemas/users.py`
- `backend/app/api/v1/routes/users.py`
- `frontend/src/lib/theme.ts`
- `frontend/src/features/auth/components/ThemeSelector.tsx`
- `backend/tests/unit/test_user_schemas.py`
- `backend/tests/integration/routes/test_users_routes.py`

**Files to MODIFY:**
- `backend/app/models/user.py` — add `preferences` JSONB column
- `backend/app/schemas/auth.py` — add `preferences` field to `MeResponse`
- `backend/app/api/v1/router.py` — import and register `users` router
- `frontend/src/styles/sphotel-vars.css` — add light and high-contrast CSS blocks
- `frontend/index.html` — add FOUC prevention inline script; remove hardcoded `class="dark"` from `<html>` tag
- `frontend/src/app/providers.tsx` — add `ThemeHydrator` component
- `frontend/src/features/auth/api/auth.ts` — add `updatePreferences` method
- `backend/tests/integration/routes/test_auth_logout_me.py` — add `fake_user.preferences = {}` to all mocks
- `backend/tests/unit/test_auth_schemas.py` — add `preferences: dict[str, object] = {}` to `_FakeUser`

**Files confirmed NO changes needed:**
- `backend/app/core/dependencies.py` ✓
- `backend/app/core/security/` ✓ (no auth changes)
- `backend/alembic/env.py` ✓
- No new DB migrations for audit_logs ✓ (preferences change is not audit-logged in this story)

### Architecture Compliance

1. **Tailwind v4 dark mode** — uses `@custom-variant dark (&:is(.dark *))` class strategy defined in `index.css`. Setting `.dark` on `<html>` activates all `dark:` utilities. No `tailwind.config.js` exists — Tailwind v4 via `@tailwindcss/vite` plugin.
2. **No shadcn/ui components** — `ThemeSelector` uses plain Tailwind. The `shadcn-vars.css` and `sphotel-vars.css` CSS variables ARE present and used for theming, but no Radix UI component packages are installed.
3. **`dict[str, object]` for JSONB** — consistent with Story 2.5's `AuditLog.payload` pattern. Never use `dict[str, Any]` under mypy strict.
4. **`DataResponse[T]` envelope** — all new endpoints use standard `{data: T, error: null}` envelope.
5. **Max 100 lines per file** — `users.py` route is ~50 lines, `ThemeSelector.tsx` is ~50 lines. Both within limit.
6. **No cross-feature imports** — `ThemeSelector` imports from its own feature's stores/api. `applyTheme` is in `src/lib/` (shared utilities), not in a feature folder.
7. **Zustand v5** — use `create<T>()((set) => ...)` pattern. Auth store already follows this.

### Gotchas & Known Pitfalls

**`preferences` JSONB SQLAlchemy null handling:** Even though the column is `NOT NULL DEFAULT '{}'`, newly loaded rows that existed before migration will have `{}` from the server default. `user.preferences or {}` safely handles any edge case where the ORM returns `None` before DB sync.

**`Mapped[dict[str, object]]` vs `dict[str, Any]`:** mypy strict requires `object` not `Any`. SQLAlchemy JSONB returns `dict[str, Any]` at runtime but is typed as `dict[str, object]` in the model. The `dict(user.preferences or {})` copy and `current_prefs["theme"] = body.theme` assignment is valid since `body.theme` is `str` (subtype of `object`).

**`MeResponse.model_validate()` failing on MagicMock:** Pydantic v2 with `from_attributes=True` calls `getattr(obj, field)` for each field. For the new `preferences` field, `MagicMock().preferences` returns a `MagicMock`, not a `dict`. Pydantic will fail validation. Fix: explicitly set `fake_user.preferences = {}` in all integration test mocks.

**FOUC script removes hardcoded `class="dark"`:** The `index.html` currently has `<html lang="en" class="dark">`. After adding the FOUC script, remove `class="dark"` from the `<html>` tag — the script sets the correct class. If both are present, the script's `classList.remove('dark')` call handles it, but it's cleaner to remove the hardcoded class.

**`data-theme` attribute on `<html>`:** The Tailwind custom variant uses class strategy, not data attributes. The `data-theme` attribute is for CSS `[data-theme="light"]` selectors in `sphotel-vars.css`. Both mechanisms work together: `.dark` class activates Tailwind dark utilities; `[data-theme="light"]` selects the light CSS token overrides.

**`localStorage.getItem` in SSR:** Not applicable here — this is a Vite SPA with no SSR. `localStorage` is always available in the browser environment.

**`updatePreferences` API in `auth.ts`:** The `apiClient` already has `withCredentials: true` and unwraps the `DataResponse` envelope via the response interceptor. So `apiClient.patch<MeResponse>('/api/v1/users/me/preferences', {theme}).then(r => r.data)` returns the inner `MeResponse` directly (not the envelope).

**Route registration order in `router.py`:** Add `users.router` after `staff.router`. The `prefix="/users"` means no conflicts with `/staff` or `/auth`.

**`ThemeHydrator` vs localStorage caching:** On first load after login, `currentUser.preferences.theme` from the API might differ from the localStorage cache (e.g., user changed theme on another device). `ThemeHydrator`'s `useEffect` handles this by calling `applyTheme()` whenever `preferences` changes, keeping the local state in sync with the server.

### Previous Story Intelligence (Stories 2.4, 2.5)

- **Story 2.5 established `MeResponse`** — add `preferences` field to existing class; do NOT create a new response schema
- **`dict[str, object]` for audit payloads** — same pattern used in `AuditLog.payload` and `update_credentials` changes dict
- **`db.execute(update(...).values(...))` + `db.commit()` + re-fetch** — established pattern in `update_credentials` and `admin_reset_credentials` in Story 2.5
- **`DataResponse[T]` envelope** — all new endpoints use it; `apiClient` interceptor unwraps automatically in frontend
- **Docker rebuild required** after any new file additions: `docker compose build backend`
- **Line length 88 chars** — ruff default; `f"session_revoked:{user_id_str}"` patterns are fine; watch long import lines
- **mypy `# type: ignore[arg-type]`** — Story 2.5 showed SQLAlchemy `.values(**dict[str, object])` does NOT need `type: ignore` — mypy strict accepts it directly

### References

- Story ACs: [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 2 > Story 2.6]
- FR72 (theme preference): [Source: `_bmad-output/planning-artifacts/prd.md`]
- FR72 accessibility: All surfaces support system dark/light mode preference [Source: `_bmad-output/planning-artifacts/prd.md` lines 725-734]
- Tailwind v4 dark variant: `@custom-variant dark (&:is(.dark *))` [Source: `frontend/src/index.css`]
- shadcn `.dark` CSS vars: [Source: `frontend/src/styles/shadcn-vars.css`]
- sphotel dark-first tokens: [Source: `frontend/src/styles/sphotel-vars.css`]
- `TenantUser` model (no preferences yet): [Source: `backend/app/models/user.py`]
- Migration chain `0001→0002→0003`: [Source: `backend/alembic/versions/`]
- `DataResponse`/`MessageResponse` envelope: [Source: `backend/app/schemas/common.py`]
- `apiClient` with `withCredentials: true`: [Source: `frontend/src/lib/api.ts`]
- `useAuthStore` Zustand store: [Source: `frontend/src/features/auth/stores/authStore.ts`]
- `MeResponse` (Story 2.5): [Source: `backend/app/schemas/auth.py`]
- `router.py` registration pattern: [Source: `backend/app/api/v1/router.py`]
- Architecture naming patterns: [Source: `_bmad-output/planning-artifacts/architecture.md`]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6 (2026-03-18)

### Debug Log References

- **MagicMock `preferences` regression**: After adding `preferences: dict[str, object]` to `MeResponse`, all Story 2.5 integration tests using `MagicMock()` for `fake_user` began failing because `MagicMock().preferences` returns a `MagicMock` object, which Pydantic v2 `dict[str, object]` validation rejects. Fixed by explicitly setting `fake_user.preferences = {}` in every mock block in `test_auth_logout_me.py` and adding `preferences: dict[str, object] = {}` to `_FakeUser` in `test_auth_schemas.py`.

### Completion Notes List

- All 137 tests pass (124 pre-existing + 13 new); 0 mypy strict errors; 0 ruff errors
- Used `dict[str, object]` (not `dict[str, Any]`) for JSONB field — required under mypy strict
- Preferences merge pattern `dict(user.preferences or {})` preserves future preference keys beyond `theme`
- Three-theme CSS strategy: `dark` = `.dark` class; `light` = `[data-theme="light"]` selector; `high_contrast` = `.dark` + `.high-contrast` classes
- FOUC prevention via inline `<script>` in `<head>` — executes synchronously before React mounts; hardcoded `class="dark"` removed from `<html>` tag
- `ThemeHydrator` only applies theme when user preference exists — avoids overriding system default on first load
- `ThemeSelector` uses optimistic `applyTheme()` before API call for instant visual feedback

### File List

**Created:**
- `backend/alembic/versions/0004_add_preferences_to_tenant_users.py`
- `backend/app/schemas/users.py`
- `backend/app/api/v1/routes/users.py`
- `frontend/src/lib/theme.ts`
- `frontend/src/features/auth/components/ThemeSelector.tsx`
- `backend/tests/unit/test_user_schemas.py`
- `backend/tests/integration/routes/test_users_routes.py`

**Modified:**
- `backend/app/models/user.py` — added `preferences: Mapped[dict[str, object]]` JSONB column
- `backend/app/schemas/auth.py` — added `preferences: dict[str, object]` to `MeResponse`
- `backend/app/api/v1/router.py` — imported and registered `users.router`
- `frontend/src/styles/sphotel-vars.css` — added `[data-theme="light"]` and `.high-contrast` CSS blocks
- `frontend/index.html` — added FOUC prevention inline script; removed hardcoded `class="dark"` from `<html>` tag
- `frontend/src/app/providers.tsx` — added `ThemeHydrator` component
- `frontend/src/features/auth/api/auth.ts` — added `updatePreferences()` method and `preferences` field to `MeResponse` interface
- `backend/tests/integration/routes/test_auth_logout_me.py` — added `fake_user.preferences = {}` to all MagicMock instances
- `backend/tests/unit/test_auth_schemas.py` — added `preferences: dict[str, object] = {}` to `_FakeUser`

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-03-18 | 1.0 | Initial implementation — migration, endpoint, CSS themes, FOUC prevention, ThemeSelector | claude-sonnet-4-6 |
