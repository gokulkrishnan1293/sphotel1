# Story 2.4: Staff PIN Management (Admin)

Status: review

## Story

As an **Admin**,
I want to create, edit, deactivate, and reset PINs for all staff accounts in my tenant,
so that I have full control over who can access the system and can immediately revoke access when needed.

## Acceptance Criteria

1. **Given** an authenticated Admin sends `POST /api/v1/staff` with `{name, role, pin}`, **When** the target role is strictly below the Admin's own role (FR87), **Then** a new `TenantUser` row is created with `pin_hash = bcrypt(pin)`, scoped to `current_user["tenant_id"]`, and the response returns the created user (no credential fields).

2. **And** `GET /api/v1/staff` returns all `TenantUser` records for the Admin's tenant (both active and inactive); Admin and Super-Admin only.

3. **And** `PATCH /api/v1/staff/{id}/pin` resets a staff member's PIN with the provided new PIN (bcrypt-hashed before storage); Admin can only reset PINs for staff whose role is strictly below their own.

4. **And** `PATCH /api/v1/staff/{id}/deactivate` sets `is_active = False` on the target record AND sets `auth_locked:{user_id}` in Valkey (no TTL) — immediately blocking new logins.

5. **And** `DELETE /api/v1/staff/{id}/sessions` sets `session_revoked:{user_id}` = current epoch timestamp in Valkey with TTL = `JWT_EXPIRY_HOURS * 3600`, causing `get_current_user` to reject any existing JWTs issued before the revocation timestamp. Also sets `auth_locked:{user_id}` to block re-login.

6. **And** `get_current_user` in `dependencies.py` is extended to check Valkey for `session_revoked:{user_id}` after JWT decode — raises HTTP 401 `SESSION_REVOKED` if the token's `iat` ≤ the revocation timestamp.

7. **And** Admin cannot create or modify staff at or above their own role level — enforced via `can_assign_role()` from `permissions.py`, returning HTTP 403 `ROLE_HIERARCHY_VIOLATION`.

8. **And** all five operations (`staff_create`, `pin_reset`, `staff_deactivate`, `sessions_revoke`) write an `AuditLog` entry with `actor_id`, `action`, `target_id`, and `tenant_id`.

9. **And** the frontend renders a staff management table at `src/features/auth/StaffManagement.tsx` with create/reset-PIN/deactivate/revoke-sessions actions, accessible only to Admin and Super-Admin roles.

10. **And** `mypy --strict` and `ruff check` pass with zero errors on all new/modified files.

## Tasks / Subtasks

- [x] **Task 1: Create `backend/app/schemas/staff.py`** (AC: #1, #2, #3)
  - [x] `CreateStaffRequest(BaseModel)`: `name: str = Field(min_length=1, max_length=100)`, `role: UserRole`, `pin: str = Field(min_length=4, max_length=8)`
  - [x] `ResetPinRequest(BaseModel)`: `pin: str = Field(min_length=4, max_length=8)`
  - [x] `StaffResponse(BaseModel)`: `id: uuid.UUID`, `tenant_id: str`, `name: str`, `role: UserRole`, `is_active: bool`, `created_at: datetime`; with `model_config = ConfigDict(from_attributes=True)`
  - [x] Do NOT expose `pin_hash`, `password_hash`, `totp_secret` in any response schema

- [x] **Task 2: Implement staff endpoints in `backend/app/api/v1/routes/staff.py`** (AC: #1, #2, #3, #4, #7, #8)
  - [x] `GET /api/v1/staff` — list all tenant staff; `require_role(ADMIN, SUPER_ADMIN)`
  - [x] `POST /api/v1/staff` — create with role guard + audit log; `require_role(ADMIN, SUPER_ADMIN)`; `db.flush()` before audit to get server-generated `id`
  - [x] `PATCH /api/v1/staff/{staff_id}/pin` — reset PIN with role guard + audit log; `require_role(ADMIN, SUPER_ADMIN)`
  - [x] `PATCH /api/v1/staff/{staff_id}/deactivate` — set `is_active=False` + `auth_locked:{id}` + audit log; `require_role(ADMIN, SUPER_ADMIN)`
  - [x] ALL endpoints: scope DB queries by `TenantUser.tenant_id == current_user["tenant_id"]`; 404 if target not in same tenant
  - [x] Helper `_get_staff_in_tenant(staff_id, tenant_id, db)` — shared lookup with 404 guard

- [x] **Task 3: Implement `DELETE /api/v1/staff/{staff_id}/sessions`** (AC: #5, #8)
  - [x] `require_role(ADMIN, SUPER_ADMIN)`
  - [x] Verify target staff is in same tenant via `_get_staff_in_tenant()`
  - [x] Set `session_revoked:{target.id}` = `str(time.time())` in Valkey with TTL = `settings.JWT_EXPIRY_HOURS * 3600`
  - [x] Also set `auth_locked:{target.id}` = `"1"` (no TTL)
  - [x] Write `AuditLog(action="sessions_revoke", target_id=target.id, ...)`
  - [x] Return `{"message": "Sessions revoked"}` via `DataResponse[MessageResponse]`

- [x] **Task 4: Modify `backend/app/core/dependencies.py`** (AC: #6)
  - [x] Add `valkey: Any = Depends(get_valkey)` parameter to `get_current_user()`
  - [x] Add `from app.db.valkey import get_valkey` and `typing.Any` imports
  - [x] After successful JWT decode, check `await valkey.get(f"session_revoked:{user_id_str}")`
  - [x] If `revoked_at` exists and `float(revoked_at) >= float(str(payload.get("iat", 0)))` → raise HTTP 401 `SESSION_REVOKED`
  - [x] No changes needed to `require_role()` — it calls `get_current_user` via `Depends()`

- [x] **Task 5: Frontend staff management table** (AC: #9)
  - [x] Inspected `frontend/src/features/auth/` — only placeholder `.gitkeep` and stub `types.ts`
  - [x] Created `frontend/src/features/auth/api/staff.ts` — API client for 5 endpoints using `apiClient`
  - [x] Created `frontend/src/features/auth/hooks/useStaff.ts` — TanStack Query hooks
  - [x] Created `frontend/src/features/auth/StaffManagement.tsx` — table + create/reset-PIN modals
  - [x] Table: Name, Role badge, Status, Actions (Reset PIN | Deactivate | Revoke Sessions)
  - [x] Create-staff modal: name, role dropdown (ASSIGNABLE_ROLES = biller/waiter/kitchen_staff/manager), PIN
  - [x] Reset-PIN modal: new PIN field
  - [x] Plain Tailwind (no shadcn — not installed in this project)

- [x] **Task 6: Tests** (AC: #10)
  - [x] `backend/tests/unit/test_staff_schema.py` — 8 tests (validation, ORM mode, no-credentials check)
  - [x] `backend/tests/unit/test_session_revocation.py` — 4 tests (Valkey mock, revoked/valid/past-revocation/no-cookie)
  - [x] `backend/tests/integration/routes/test_staff_routes.py` — 9 tests covering all 5 endpoints
  - [x] `docker compose build backend && pytest` — 102 passed, 0 failed
  - [x] Prior 81 tests still pass (no regressions)

## Dev Notes

### No new migration needed

`TenantUser` at `backend/app/models/user.py` already has every column this story needs:
- `name: Mapped[str]` ✓
- `role: Mapped[UserRole]` ✓
- `pin_hash: Mapped[str | None]` ✓
- `is_active: Mapped[bool]` ✓
- `tenant_id` inherited from `TenantMixin` (VARCHAR, not UUID) ✓

Migration chain stays: `0001 → 0002 → 0003`. No migration 0004 in this story.

### Task 1 — Exact `app/schemas/staff.py`

```python
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.security.permissions import UserRole


class CreateStaffRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    role: UserRole
    pin: str = Field(min_length=4, max_length=8)


class ResetPinRequest(BaseModel):
    pin: str = Field(min_length=4, max_length=8)


class StaffResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: str
    name: str
    role: UserRole
    is_active: bool
    created_at: datetime
```

**`from_attributes=True`** — enables `StaffResponse.model_validate(db_obj)` for SQLAlchemy ORM objects. Without this, pydantic raises `ValidationError` when trying to construct from an ORM model.

**`created_at: datetime`** — `TenantUser` inherits `TimestampMixin` which provides `created_at`. Confirm it exists in `app/models/base.py` (`TimestampMixin`).

### Task 2 — `app/api/v1/routes/staff.py` core structure

```python
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole, can_assign_role
from app.core.security.pin import hash_pin
from app.db.session import get_db
from app.db.valkey import get_valkey
from app.models.audit_log import AuditLog
from app.models.user import TenantUser
from app.schemas.staff import CreateStaffRequest, ResetPinRequest, StaffResponse

router = APIRouter(prefix="/staff", tags=["staff"])

_MANAGEABLE_ROLES = frozenset({
    UserRole.ADMIN,
    UserRole.SUPER_ADMIN,
})


async def _get_staff_in_tenant(
    staff_id: uuid.UUID,
    tenant_id: str,
    db: AsyncSession,
) -> TenantUser:
    """Load a TenantUser scoped to the caller's tenant. Raises 404 if not found."""
    result = await db.execute(
        select(TenantUser).where(
            TenantUser.id == staff_id,
            TenantUser.tenant_id == tenant_id,
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "Staff member not found"},
        )
    return user


@router.get("", response_model=list[StaffResponse])
async def list_staff(
    current_user: CurrentUser = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
    db: AsyncSession = Depends(get_db),
) -> list[StaffResponse]:
    """Return all staff in the caller's tenant."""
    result = await db.execute(
        select(TenantUser).where(
            TenantUser.tenant_id == current_user["tenant_id"]
        )
    )
    users = result.scalars().all()
    return [StaffResponse.model_validate(u) for u in users]


@router.post("", response_model=StaffResponse, status_code=201)
async def create_staff(
    body: CreateStaffRequest,
    current_user: CurrentUser = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
    db: AsyncSession = Depends(get_db),
) -> StaffResponse:
    """Create a new staff member. Admin cannot assign role at or above their own."""
    if not can_assign_role(current_user["role"], body.role):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ROLE_HIERARCHY_VIOLATION",
                "message": "Cannot assign role at or above your own level",
            },
        )
    new_user = TenantUser(
        tenant_id=current_user["tenant_id"],
        name=body.name,
        role=body.role,
        pin_hash=hash_pin(body.pin),
    )
    db.add(new_user)
    await db.flush()  # get server-generated id before audit log
    db.add(AuditLog(
        tenant_id=current_user["tenant_id"],
        actor_id=current_user["user_id"],
        action="staff_create",
        target_id=new_user.id,
        payload={"role": str(body.role), "name": body.name},
    ))
    await db.commit()
    await db.refresh(new_user)
    return StaffResponse.model_validate(new_user)


@router.patch("/{staff_id}/pin", response_model=StaffResponse)
async def reset_pin(
    staff_id: uuid.UUID,
    body: ResetPinRequest,
    current_user: CurrentUser = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
    db: AsyncSession = Depends(get_db),
) -> StaffResponse:
    """Reset a staff member's PIN."""
    target = await _get_staff_in_tenant(staff_id, current_user["tenant_id"], db)
    if not can_assign_role(current_user["role"], target.role):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ROLE_HIERARCHY_VIOLATION",
                "message": "Cannot modify staff at or above your own role level",
            },
        )
    await db.execute(
        update(TenantUser)
        .where(TenantUser.id == staff_id)
        .values(pin_hash=hash_pin(body.pin))
    )
    db.add(AuditLog(
        tenant_id=current_user["tenant_id"],
        actor_id=current_user["user_id"],
        action="pin_reset",
        target_id=staff_id,
    ))
    await db.commit()
    await db.refresh(target)
    return StaffResponse.model_validate(target)


@router.patch("/{staff_id}/deactivate", response_model=StaffResponse)
async def deactivate_staff(
    staff_id: uuid.UUID,
    current_user: CurrentUser = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
    db: AsyncSession = Depends(get_db),
    valkey: Any = Depends(get_valkey),
) -> StaffResponse:
    """Deactivate a staff member — blocks new logins immediately."""
    target = await _get_staff_in_tenant(staff_id, current_user["tenant_id"], db)
    if not can_assign_role(current_user["role"], target.role):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ROLE_HIERARCHY_VIOLATION",
                "message": "Cannot modify staff at or above your own role level",
            },
        )
    await db.execute(
        update(TenantUser)
        .where(TenantUser.id == staff_id)
        .values(is_active=False)
    )
    await valkey.set(f"auth_locked:{staff_id}", "1")  # no TTL — admin must re-enable
    db.add(AuditLog(
        tenant_id=current_user["tenant_id"],
        actor_id=current_user["user_id"],
        action="staff_deactivate",
        target_id=staff_id,
    ))
    await db.commit()
    await db.refresh(target)
    return StaffResponse.model_validate(target)
```

### Task 3 — `DELETE /api/v1/staff/{staff_id}/sessions`

```python
import time


@router.delete("/{staff_id}/sessions")
async def revoke_sessions(
    staff_id: uuid.UUID,
    current_user: CurrentUser = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
    db: AsyncSession = Depends(get_db),
    valkey: Any = Depends(get_valkey),
) -> dict[str, str]:
    """Immediately invalidate all active JWT sessions for a staff member."""
    target = await _get_staff_in_tenant(staff_id, current_user["tenant_id"], db)
    if not can_assign_role(current_user["role"], target.role):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ROLE_HIERARCHY_VIOLATION",
                "message": "Cannot revoke sessions of staff at or above your own role level",
            },
        )
    ttl = settings.JWT_EXPIRY_HOURS * 3600
    await valkey.set(
        f"session_revoked:{staff_id}", str(time.time()), ex=ttl
    )
    await valkey.set(f"auth_locked:{staff_id}", "1")  # block re-login; no TTL
    db.add(AuditLog(
        tenant_id=current_user["tenant_id"],
        actor_id=current_user["user_id"],
        action="sessions_revoke",
        target_id=staff_id,
    ))
    await db.commit()
    return {"message": "Sessions revoked"}
```

**Add to imports at top:** `import time` and `from app.core.config import settings`.

**Why both `session_revoked` AND `auth_locked`?**
- `session_revoked:{id}` invalidates the currently live JWT (checked in `get_current_user`)
- `auth_locked:{id}` prevents immediate re-login (checked in `pin_login` / `admin_login`)
- Together they ensure complete session termination with no re-entry window

### Task 4 — Modified `app/core/dependencies.py`

```python
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any, TypedDict

import jwt
from fastapi import Depends, HTTPException, Request

from app.core.security.jwt import decode_access_token
from app.core.security.permissions import UserRole
from app.db.valkey import get_valkey


class CurrentUser(TypedDict):
    """Authenticated user context injected by require_role() into endpoints."""

    user_id: uuid.UUID
    tenant_id: str
    role: UserRole


async def get_current_user(
    request: Request,
    valkey: Any = Depends(get_valkey),
) -> CurrentUser:
    """Extract and validate JWT from httpOnly access_token cookie."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Authentication required"},
        )
    try:
        payload = decode_access_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Authentication required"},
        )

    user_id_str = str(payload["user_id"])

    # Check if admin explicitly revoked all sessions for this user
    revoked_at = await valkey.get(f"session_revoked:{user_id_str}")
    if revoked_at is not None:
        token_iat = float(str(payload.get("iat", 0)))
        if float(revoked_at) >= token_iat:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "SESSION_REVOKED",
                    "message": "Session has been revoked. Please log in again.",
                },
            )

    return CurrentUser(
        user_id=uuid.UUID(user_id_str),
        tenant_id=str(payload["tenant_id"]),
        role=UserRole(str(payload["role"])),
    )


def require_role(
    *allowed_roles: UserRole,
) -> Callable[..., Awaitable[CurrentUser]]:
    """FastAPI dependency factory for role-based access control. (unchanged)"""

    async def _check_role(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail={"code": "FORBIDDEN", "message": "Insufficient permissions"},
            )
        return current_user

    return _check_role
```

**`float(revoked_at) >= token_iat`** — revocation time at or after issue time means token was active before revocation. New tokens issued after revocation will have `iat > revoked_at`, so they pass.

**Valkey TTL = 4 hours** — after this, all JWTs issued before revocation have naturally expired via `exp` claim, so the Valkey key auto-deletes (no manual cleanup needed).

**Existing test compatibility:** Tests overriding `get_current_user` via `app.dependency_overrides[get_current_user] = lambda: CurrentUser(...)` still work — they bypass this function entirely. Tests that test `get_current_user` directly must mock `get_valkey`.

### Task 5 — Frontend structure

**Before writing frontend files, read what already exists:**
```bash
ls frontend/src/features/auth/
```
Login page and related components may already be here from Story 2.2 / 2.3.

**`frontend/src/features/auth/api/staff.ts`** — use the same HTTP client pattern as existing API files. Check `frontend/src/lib/` for the API client setup (likely `axios` instance with cookie credentials).

**Key API calls:**
```typescript
// Use credentials: "include" to send httpOnly cookies
const apiFetch = (url: string, options?: RequestInit) =>
  fetch(url, { credentials: "include", ...options });

export const staffApi = {
  list: () =>
    apiFetch("/api/v1/staff").then((r) => r.json()),
  create: (data: CreateStaffRequest) =>
    apiFetch("/api/v1/staff", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }).then((r) => r.json()),
  resetPin: (id: string, data: { pin: string }) =>
    apiFetch(`/api/v1/staff/${id}/pin`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }).then((r) => r.json()),
  deactivate: (id: string) =>
    apiFetch(`/api/v1/staff/${id}/deactivate`, {
      method: "PATCH",
    }).then((r) => r.json()),
  revokeSessions: (id: string) =>
    apiFetch(`/api/v1/staff/${id}/sessions`, {
      method: "DELETE",
    }).then((r) => r.json()),
};
```

**`frontend/src/features/auth/StaffManagement.tsx`** structure:
- `StaffManagement` — main component; fetches staff list, renders table
- `CreateStaffDialog` — modal for creating staff (name, role dropdown, PIN)
- `ResetPinDialog` — modal for resetting PIN (new PIN field)
- Role dropdown in CreateStaffDialog must filter to roles below current user's level (enforce FR87 in UI, API enforces it too)
- Use shadcn `Table`, `Dialog`, `Button`, `Badge`, `Form` — all available in this project
- Use `useQuery(["staff"], staffApi.list)` and `useMutation(staffApi.create, { onSuccess: () => queryClient.invalidateQueries(["staff"]) })`

### Project Structure Notes

**Files to CREATE:**
- `backend/app/schemas/staff.py`
- `backend/tests/unit/test_staff_schema.py`
- `backend/tests/unit/test_session_revocation.py`
- `backend/tests/integration/test_staff_routes.py`
- `frontend/src/features/auth/api/staff.ts`
- `frontend/src/features/auth/hooks/useStaff.ts`
- `frontend/src/features/auth/StaffManagement.tsx`

**Files to MODIFY:**
- `backend/app/api/v1/routes/staff.py` — currently a stub (`router = APIRouter(prefix="/staff", tags=["staff"])`); add all 5 endpoints
- `backend/app/core/dependencies.py` — add `valkey` dependency and session revocation check to `get_current_user`

**Files confirmed NO changes needed:**
- `backend/app/models/user.py` — all columns already exist ✓
- `backend/app/core/security/permissions.py` — `can_assign_role()` already implemented ✓
- `backend/app/core/security/pin.py` — `hash_pin()` / `verify_pin()` already exist ✓
- `backend/app/models/audit_log.py` — `target_id` field already exists ✓
- `backend/app/api/v1/routes/auth.py` — no changes (lockout checks stay as-is) ✓
- **No new migration** — chain stays `0001 → 0002 → 0003` ✓

### Architecture Compliance

1. **Tenant isolation is mandatory** — every DB query must filter by `TenantUser.tenant_id == current_user["tenant_id"]`. Never expose users from other tenants.
2. **`can_assign_role()` is the single source of FR87** — located in `permissions.py`, already correctly implemented. Never hardcode role comparisons elsewhere.
3. **`hash_pin()` for all new PINs** — use `from app.core.security.pin import hash_pin`. Never store plaintext PINs under any circumstance.
4. **Parameterized SQLAlchemy** — `select(TenantUser).where(...)` — no raw SQL strings. Use `update(TenantUser).where(...).values(...)` for updates.
5. **`db.flush()` before audit log** — required to get the server-generated `new_user.id` (UUID via `gen_random_uuid()`) within the same transaction before commit.
6. **`require_role()` from `dependencies.py`** — do not re-implement JWT parsing in staff handlers. Use `Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN))`.
7. **Valkey TTL on `session_revoked`** — always set `ex=settings.JWT_EXPIRY_HOURS * 3600`. Without TTL, keys accumulate forever.
8. **`StaffResponse.model_validate(db_obj)`** — pydantic v2 ORM mode requires `ConfigDict(from_attributes=True)`. Forgetting this causes `ValidationError`.

### Gotchas & Known Pitfalls

**`db.flush()` vs `db.commit()`:** `flush()` executes the INSERT within the current transaction without committing, populating server defaults like `id`. Both the new user and the audit log then commit atomically. If `flush()` is skipped, `new_user.id` will be `None` when the audit log is created.

**`result.scalars().all()` for list queries:** Returns `list[TenantUser]`. The `scalars()` call is needed to unwrap the `Row` objects when selecting ORM models.

**`await db.refresh(target)` after `db.execute(update(...))`:** After an ORM `update()` statement, the local `target` object is stale. Call `refresh()` to reload from DB before returning it in the response.

**`require_role()` factory pattern:** Always wrap with `Depends()`. The factory returns a coroutine function, not a value:
```python
# CORRECT:
current_user: CurrentUser = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN))
# WRONG — will fail at runtime:
current_user: CurrentUser = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
```

**`time.time()` returns `float`:** mypy strict accepts this without `# type: ignore`. Store as `str(time.time())` in Valkey (decode_responses=True means Valkey returns str).

**Session revocation check timing:** If `float(revoked_at) >= token_iat` — the `>=` is intentional. If someone revokes sessions at exactly the same second a token was issued (unlikely but possible in tests), we reject it. Better to force a re-login than allow a borderline token.

**Frontend: check `credentials: "include"` on all fetch calls** — httpOnly cookies are NOT sent by browsers unless `credentials: "include"` (or `withCredentials: true` in axios) is set. This is a common bug when frontend calls omit this flag.

**Role dropdown in CreateStaffDialog — FR87 in UI:** Filter the role options shown to the user so they cannot attempt to submit a role above their own (the API enforces it too, but the UX should not show forbidden options). Use the same `ROLE_HIERARCHY` values — filter to roles where `ROLE_HIERARCHY[option] < ROLE_HIERARCHY[currentUserRole]`.

**mypy strict and `list[StaffResponse]` return type:** `result.scalars().all()` returns `Sequence[TenantUser]`. `[StaffResponse.model_validate(u) for u in users]` produces `list[StaffResponse]`. mypy should accept this without issues.

**ruff line length (88 chars):** Long `detail={"code": ..., "message": ...}` arguments may exceed 88 chars — use multi-line dict format:
```python
detail={
    "code": "ROLE_HIERARCHY_VIOLATION",
    "message": "Cannot assign role at or above your own level",
},
```

**Docker rebuild before test run:** After adding new files (`schemas/staff.py`, test files), rebuild the image:
```bash
docker compose build backend
docker compose run --rm --no-deps backend sh -c "cd /app && mypy app --strict && ruff check app && pytest"
```

### Previous Story Intelligence (Stories 2.2, 2.3)

- **`valkey: Any = Depends(get_valkey)`** — annotate valkey as `Any`, `get_valkey` is typed as `AsyncGenerator[Any, None]`
- **`from collections.abc import Callable, Awaitable`** — ruff UP006/UP035 enforces this import style; never `typing.Callable`
- **`# type: ignore[arg-type]`** — needed only on `add_exception_handler(RateLimitExceeded, ...)` in `main.py`; no new type ignores expected in this story
- **`asyncio_mode = "auto"`** in pytest.ini — async test functions run automatically without `@pytest.mark.anyio`
- **`tenant_id: str` everywhere** — TenantMixin stores `tenant_id` as VARCHAR, not UUID. Always annotate as `str`.
- **`assert x is not None` for mypy narrowing** — use `assert` to narrow `str | None` when you're certain the value exists
- **Generic 401 for auth failures** — but for staff CRUD, specific 404/403 error codes (NOT 401) are correct

### References

- Story ACs: [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 2 > Story 2.4]
- FR87 (role hierarchy enforcement): [Source: `_bmad-output/planning-artifacts/prd.md` — FR87]
- FR85 (session invalidation across devices): [Source: `_bmad-output/planning-artifacts/prd.md` — FR85]
- `can_assign_role()` implementation: [Source: `backend/app/core/security/permissions.py`]
- `ROLE_HIERARCHY` constants: [Source: `backend/app/core/security/permissions.py`]
- `hash_pin()` / `verify_pin()`: [Source: `backend/app/core/security/pin.py`]
- `TenantUser` all columns: [Source: `backend/app/models/user.py`]
- `AuditLog` with `target_id` field: [Source: `backend/app/models/audit_log.py`]
- `require_role()` / `get_current_user()` / `CurrentUser`: [Source: `backend/app/core/dependencies.py`]
- Valkey key patterns (`auth_locked:`, `auth_attempts:`): [Source: `backend/app/api/v1/routes/auth.py`]
- Staff router stub: [Source: `backend/app/api/v1/routes/staff.py`]
- Architecture multi-tenancy rules: [Source: `_bmad-output/planning-artifacts/architecture.md`]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Test failure: `resp.json()["detail"]["code"]` → fixed to `resp.json()["error"]["message"]` because `app.main` has custom exception handler that wraps HTTPException detail in `{"data": null, "error": {"code": "<status>", "message": "<detail_str>", "details": {}}}` envelope

### Completion Notes List

- `MessageResponse` added to `app/schemas/common.py` for mutation confirmations
- All staff endpoints use `DataResponse[T]` envelope (consistent with health route)
- `get_current_user` now takes `valkey: Any = Depends(get_valkey)` — session revocation checked on every authenticated request; Valkey connection is lazy (no actual network I/O until `.get()` is called)
- `_check_can_manage()` helper centralizes FR87 role hierarchy enforcement across all 5 endpoints
- `db.flush()` used in `create_staff` to get server-generated UUID before writing audit log in same transaction
- Frontend uses plain Tailwind (shadcn/ui not installed in this project)
- ASSIGNABLE_ROLES in frontend limits to roles strictly below Admin level (biller, waiter, kitchen_staff, manager)
- 102 tests total: 81 prior + 21 new (8 schema + 4 revocation + 9 route integration)
- mypy --strict: 52 source files, 0 errors
- ruff check: 0 errors

### File List

**Created:**
- `backend/app/schemas/staff.py`
- `backend/app/api/v1/routes/staff.py` (was stub)
- `backend/tests/unit/test_staff_schema.py`
- `backend/tests/unit/test_session_revocation.py`
- `backend/tests/integration/routes/test_staff_routes.py`
- `frontend/src/features/auth/api/staff.ts`
- `frontend/src/features/auth/hooks/useStaff.ts`
- `frontend/src/features/auth/StaffManagement.tsx`

**Modified:**
- `backend/app/schemas/common.py` — added `MessageResponse`
- `backend/app/core/dependencies.py` — added Valkey session revocation check to `get_current_user`
