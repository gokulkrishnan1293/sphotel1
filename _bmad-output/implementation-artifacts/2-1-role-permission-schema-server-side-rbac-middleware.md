# Story 2.1: Role & Permission Schema + Server-Side RBAC Middleware

Status: review

## Story

As a **developer**,
I want the six-role schema defined and RBAC middleware enforced at the API layer,
so that every future endpoint can declare its required role and the server rejects unauthorized requests — never trusting the client.

## Acceptance Criteria

1. **Given** the migration runs, **When** the `tenant_users.role` column is queried, **Then** it is constrained to exactly six valid values: `biller`, `waiter`, `kitchen_staff`, `manager`, `admin`, `super_admin` — enforced at the PostgreSQL level via a native `user_role` ENUM type.

2. **And** a `ROLE_PERMISSIONS` config in `app/core/security/permissions.py` explicitly declares the capability set for each role — this config is the single source of truth; no role logic is hardcoded in individual endpoint handlers.

3. **And** a `require_role(*roles)` FastAPI dependency factory raises HTTP 403 (with `{"code": "FORBIDDEN", "message": "Insufficient permissions"}` envelope) if the authenticated user's role is not in the allowed list; raises HTTP 401 until Story 2.2 wires the actual token validation.

4. **And** role checks are enforced server-side via `require_role()` Depends — client-side role state is decorative only.

5. **And** a `can_assign_role(assigner_role, target_role) -> bool` function returns `False` when the target role's hierarchy level is greater than or equal to the assigner's level (FR87).

6. **And** each role has explicitly documented data visibility boundaries in `ROLE_DATA_SCOPE` in `permissions.py`, used by repository functions to scope queries (FR89).

7. **And** `mypy --strict` and `ruff check` pass with zero errors on all new files.

## Tasks / Subtasks

- [x] **Task 1: Migration 0003 — add `user_role` PostgreSQL ENUM type** (AC: #1)
  - [x] Create `backend/alembic/versions/0003_add_user_role_enum.py`
  - [x] `revision = "0003"`, `down_revision = "0002"` — links into migration chain
  - [x] `upgrade()`: create PG ENUM type `user_role` with values `('biller', 'waiter', 'kitchen_staff', 'manager', 'admin', 'super_admin')` via `op.execute("CREATE TYPE user_role AS ENUM (...)")`
  - [x] `upgrade()`: `ALTER TABLE tenant_users ALTER COLUMN role TYPE user_role USING role::user_role` via `op.execute()`
  - [x] `downgrade()`: `ALTER TABLE tenant_users ALTER COLUMN role TYPE VARCHAR USING role::text`
  - [x] `downgrade()`: `DROP TYPE IF EXISTS user_role`
  - [x] Run `make migrate` to verify migration applies cleanly and is idempotent

- [x] **Task 2: Update `TenantUser` model to use `UserRole` enum type** (AC: #1)
  - [x] Create `backend/app/core/security/__init__.py` — empty, marks package
  - [x] After Task 3 creates `permissions.py`, update `backend/app/models/user.py`
  - [x] Change `role: Mapped[str]` to `role: Mapped[UserRole]` using `SAEnum(UserRole, name="user_role", native_enum=True, create_type=False)`
  - [x] Import `UserRole` from `app.core.security.permissions`
  - [x] Import `Enum as SAEnum` from `sqlalchemy`
  - [x] `create_type=False` is CRITICAL — prevents SA from trying to create the PG ENUM (migration owns that)
  - [x] Run `make migrate` after model update to verify no autogenerate drift

- [x] **Task 3: Create `app/core/security/permissions.py`** (AC: #2, #5, #6)
  - [x] Create `backend/app/core/security/permissions.py`
  - [x] Define `class UserRole(enum.StrEnum)` with 6 values (snake_case values, UPPER_CASE Python names)
  - [x] Define `ROLE_HIERARCHY: Final[dict[UserRole, int]]` — maps each role to its authorization level (see Dev Notes)
  - [x] Define `ROLE_PERMISSIONS: Final[dict[UserRole, frozenset[str]]]` — maps each role to its explicit capability set (see Dev Notes)
  - [x] Define `ROLE_DATA_SCOPE: Final[dict[UserRole, str]]` — maps each role to its data visibility boundary (see Dev Notes)
  - [x] Define `def can_assign_role(assigner: UserRole, target: UserRole) -> bool` — returns `ROLE_HIERARCHY[assigner] > ROLE_HIERARCHY[target]` (FR87)
  - [x] Keep file ≤ 100 lines; no business logic — pure config + one helper function

- [x] **Task 4: Create `app/core/dependencies.py`** (AC: #3, #4)
  - [x] Create `backend/app/core/dependencies.py`
  - [x] Define `class CurrentUser(TypedDict)` with fields: `user_id: uuid.UUID`, `tenant_id: str`, `role: UserRole`
  - [x] Define `async def get_current_user(request: Request) -> CurrentUser` — stub that always raises `HTTPException(status_code=401, detail={"code": "UNAUTHORIZED", "message": "Authentication required"})`. Story 2.2 replaces this with real JWT cookie extraction.
  - [x] Define `def require_role(*allowed_roles: UserRole) -> Callable[..., Awaitable[CurrentUser]]` — returns an async dependency function (see Dev Notes for exact implementation)
  - [x] The returned inner function calls `Depends(get_current_user)` and checks `current_user["role"] in allowed_roles`, raising `HTTPException(403, ...)` on mismatch
  - [x] Keep file ≤ 100 lines

- [x] **Task 5: Unit tests** (AC: #1–#7)
  - [x] Create `backend/tests/unit/test_permissions.py`
  - [x] Test: `UserRole` enum has exactly 6 members with correct string values
  - [x] Test: `ROLE_PERMISSIONS` contains an entry for every `UserRole` member (no missing roles)
  - [x] Test: `can_assign_role(ADMIN, MANAGER)` returns `True`
  - [x] Test: `can_assign_role(ADMIN, ADMIN)` returns `False`
  - [x] Test: `can_assign_role(ADMIN, SUPER_ADMIN)` returns `False`
  - [x] Test: `can_assign_role(MANAGER, BILLER)` returns `True`
  - [x] Test: `can_assign_role(BILLER, WAITER)` returns `False` (same level)
  - [x] Create `backend/tests/unit/test_require_role.py`
  - [x] Test: `require_role(ADMIN)` dependency returns 401 when `get_current_user` is not overridden (no auth token)
  - [x] Test: `require_role(ADMIN)` returns 403 when user has `BILLER` role (via `dependency_overrides`)
  - [x] Test: `require_role(ADMIN, MANAGER)` returns 200 when user has `ADMIN` role (via `dependency_overrides`)
  - [x] Test: `require_role(ADMIN, MANAGER)` returns 200 when user has `MANAGER` role (via `dependency_overrides`)

- [x] **Task 6: Run full test suite** (AC: #7)
  - [x] `docker compose run --rm --no-deps backend sh -c "cd /app && mypy app --strict && ruff check app && pytest"`
  - [x] All existing 48 tests pass (no regressions) — 68/68 total tests pass
  - [x] New tests pass: 13 in test_permissions.py + 6 in test_require_role.py

## Dev Notes

### Task 1 — Migration 0003 exact implementation

```python
"""add user_role enum type to tenant_users

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-17
"""
from typing import Sequence, Union
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the PostgreSQL ENUM type
    op.execute("""
        CREATE TYPE user_role AS ENUM (
            'biller', 'waiter', 'kitchen_staff',
            'manager', 'admin', 'super_admin'
        )
    """)
    # Alter existing VARCHAR column to use the new enum type
    op.execute("""
        ALTER TABLE tenant_users
        ALTER COLUMN role TYPE user_role
        USING role::user_role
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE tenant_users
        ALTER COLUMN role TYPE VARCHAR
        USING role::text
    """)
    op.execute("DROP TYPE IF EXISTS user_role")
```

**Why `op.execute()` and not `op.alter_column()`?**
- Alembic's `op.alter_column()` does not handle PG ENUM type changes cleanly.
- Raw SQL via `op.execute()` gives exact control over the `USING` cast clause.
- The `USING role::user_role` clause tells PostgreSQL how to cast existing string values to the enum.
- Any existing rows with role values outside the 6 valid values will cause migration failure — this is intentional (data integrity guard).

**Migration chain after this story:** `0001 → 0002 → 0003`

### Task 3 — `backend/app/core/security/permissions.py` full implementation

```python
import enum
from typing import Final


class UserRole(str, enum.Enum):
    """Six roles with non-overlapping capability boundaries (FR32)."""
    BILLER = "biller"
    WAITER = "waiter"
    KITCHEN_STAFF = "kitchen_staff"
    MANAGER = "manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# Authorization level — used for role assignment guard (FR87).
# A user may only assign roles with a level STRICTLY LESS than their own.
ROLE_HIERARCHY: Final[dict[UserRole, int]] = {
    UserRole.BILLER: 1,
    UserRole.WAITER: 1,
    UserRole.KITCHEN_STAFF: 1,
    UserRole.MANAGER: 2,
    UserRole.ADMIN: 3,
    UserRole.SUPER_ADMIN: 4,
}

# Explicit capability sets per role — the single source of truth (FR32, FR89).
# Endpoints declare which capabilities they require; never hardcode roles per handler.
ROLE_PERMISSIONS: Final[dict[UserRole, frozenset[str]]] = {
    UserRole.BILLER: frozenset({
        "bills:create", "bills:read_own", "bills:modify_own",
        "kot:fire", "payments:collect", "menu:read",
        "print:trigger", "templates:use",
    }),
    UserRole.WAITER: frozenset({
        "bills:create", "bills:read_own", "kot:fire", "menu:read",
        "bills:transfer",
    }),
    UserRole.KITCHEN_STAFF: frozenset({
        "kot:read", "kot:mark_ready", "menu:toggle_availability",
    }),
    UserRole.MANAGER: frozenset({
        "bills:read", "staff:attendance", "payroll:view",
        "expenses:record", "kot:read", "menu:read", "shifts:manage",
    }),
    UserRole.ADMIN: frozenset({
        "bills:read", "bills:void_approve", "bills:audit",
        "menu:manage", "staff:manage", "payroll:manage",
        "expenses:manage", "reports:view", "settings:manage",
        "print_agents:manage", "telegram:configure", "gst:report",
        "feature_flags:read",
    }),
    UserRole.SUPER_ADMIN: frozenset({
        "tenants:manage", "platform:analytics",
    }),
}

# Data visibility scope per role (FR89).
# Repositories use this to scope queries — enforced structurally, not in handlers.
# Values: "own_session" | "tenant_staff" | "full_tenant" | "platform"
ROLE_DATA_SCOPE: Final[dict[UserRole, str]] = {
    UserRole.BILLER: "own_session",       # Only bills from own active session
    UserRole.WAITER: "own_session",        # Own bills only
    UserRole.KITCHEN_STAFF: "full_tenant", # All KOTs for tenant
    UserRole.MANAGER: "tenant_staff",      # Staff, payroll, expenses for tenant
    UserRole.ADMIN: "full_tenant",         # All data for their tenant
    UserRole.SUPER_ADMIN: "platform",      # Tenant management — no individual tenant data
}


def can_assign_role(assigner: UserRole, target: UserRole) -> bool:
    """Return True only if assigner's level is strictly greater than target's level.

    Implements FR87: no user can grant a role at or above their own level.
    Admin (3) can assign Manager (2), Biller/Waiter/KitchenStaff (1).
    Admin (3) cannot assign Admin (3) or Super-Admin (4).
    """
    return ROLE_HIERARCHY[assigner] > ROLE_HIERARCHY[target]
```

**`UserRole(str, enum.Enum)` pattern:**
- Inheriting from `str` means `UserRole.BILLER == "biller"` is `True` — SQLAlchemy and JSON serialization work transparently.
- mypy --strict: using `str` base class means `UserRole` values satisfy `str` type hints without explicit `.value` access.

### Task 2 — Updated `backend/app/models/user.py`

```python
import uuid

from sqlalchemy import UUID, Boolean, Enum as SAEnum, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.security.permissions import UserRole
from app.models.base import Base, TenantMixin, TimestampMixin


class TenantUser(Base, TenantMixin, TimestampMixin):
    __tablename__ = "tenant_users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    # tenant_id inherited from TenantMixin (VARCHAR, NOT NULL, indexed)
    name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role", native_enum=True, create_type=False),
        nullable=False,
    )
    pin_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    totp_secret: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (Index("idx_tenant_users_email", "email"),)
```

**`create_type=False` is CRITICAL** — without it, SQLAlchemy will try to `CREATE TYPE user_role` when the model is used, causing a "type already exists" error at runtime (migration already created it).

**Import order:** `UserRole` import from `app.core.security.permissions` creates a circular import risk only if `permissions.py` ever imports from `models/`. It must not — `permissions.py` is pure config with no DB dependencies.

### Task 4 — `backend/app/core/dependencies.py` full implementation

```python
import uuid
from collections.abc import Awaitable, Callable
from typing import TypedDict

from fastapi import Depends, HTTPException, Request

from app.core.security.permissions import UserRole


class CurrentUser(TypedDict):
    """Authenticated user context injected by require_role() into endpoints."""
    user_id: uuid.UUID
    tenant_id: str  # VARCHAR in DB — TenantMixin uses str, not UUID
    role: UserRole


async def get_current_user(request: Request) -> CurrentUser:
    """Extract and validate JWT from httpOnly cookie.

    Stub implementation — raises 401 always until Story 2.2 (PIN auth) and
    Story 2.3 (Admin/TOTP auth) implement actual cookie extraction and JWT
    validation via app.core.security.jwt.
    """
    raise HTTPException(
        status_code=401,
        detail={"code": "UNAUTHORIZED", "message": "Authentication required"},
    )


def require_role(
    *allowed_roles: UserRole,
) -> Callable[..., Awaitable[CurrentUser]]:
    """FastAPI dependency factory for role-based access control.

    Usage:
        @router.get("/protected")
        async def endpoint(user: CurrentUser = Depends(require_role(UserRole.ADMIN))):
            ...

    Raises:
        401 if no valid session token is present (from get_current_user stub).
        403 if the authenticated user's role is not in allowed_roles.
    """
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

**`tenant_id: str` in `CurrentUser`** — not `uuid.UUID`. The `TenantMixin` defines `tenant_id: Mapped[str]` (established in Story 1.2 migration). The JWT payload will carry `tenant_id` as the string UUID. Repositories that need `uuid.UUID` can call `uuid.UUID(current_user["tenant_id"])`.

**Why `Callable[..., Awaitable[CurrentUser]]`?**
- `_check_role` is an async function with FastAPI Depends injection — its true signature is complex.
- `Callable[..., Awaitable[CurrentUser]]` is the mypy --strict-compatible annotation for "async callable with any args returning CurrentUser".
- Alternative `Callable[[CurrentUser], Awaitable[CurrentUser]]` doesn't compile because the parameter is injected by Depends.

**Dependency override pattern for tests:**
```python
from app.core.dependencies import get_current_user, CurrentUser
from app.core.security.permissions import UserRole
import uuid

def make_user(role: UserRole) -> CurrentUser:
    return {
        "user_id": uuid.uuid4(),
        "tenant_id": str(uuid.uuid4()),
        "role": role,
    }

# In test:
app.dependency_overrides[get_current_user] = lambda: make_user(UserRole.ADMIN)
# ... run test ...
app.dependency_overrides.clear()
```

### Task 5 — Test patterns

**`tests/unit/test_permissions.py`** — pure unit tests, no HTTP client needed:
```python
from app.core.security.permissions import (
    ROLE_HIERARCHY, ROLE_PERMISSIONS, UserRole, can_assign_role,
)

def test_user_role_has_six_members() -> None:
    assert len(UserRole) == 6

def test_user_role_values_are_snake_case() -> None:
    for member in UserRole:
        assert member.value == member.value.lower()
        assert " " not in member.value

def test_role_permissions_covers_all_roles() -> None:
    for role in UserRole:
        assert role in ROLE_PERMISSIONS

def test_can_assign_role_admin_to_manager() -> None:
    assert can_assign_role(UserRole.ADMIN, UserRole.MANAGER) is True

def test_can_assign_role_admin_to_admin_is_false() -> None:
    assert can_assign_role(UserRole.ADMIN, UserRole.ADMIN) is False

def test_can_assign_role_admin_to_super_admin_is_false() -> None:
    assert can_assign_role(UserRole.ADMIN, UserRole.SUPER_ADMIN) is False

def test_can_assign_role_biller_to_waiter_is_false() -> None:
    # Same level — not strictly greater
    assert can_assign_role(UserRole.BILLER, UserRole.WAITER) is False
```

**`tests/unit/test_require_role.py`** — uses a real test app route with dependency overrides:
```python
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.dependencies import CurrentUser, get_current_user, require_role
from app.core.security.permissions import UserRole

# Minimal test app with one protected route
test_app = FastAPI()

@test_app.get("/admin-only")
async def admin_route(user: CurrentUser = Depends(require_role(UserRole.ADMIN))) -> JSONResponse:
    return JSONResponse({"role": user["role"]})

@pytest.mark.anyio
async def test_require_role_returns_401_without_auth() -> None:
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/admin-only")
    assert response.status_code == 401

@pytest.mark.anyio
async def test_require_role_returns_403_for_wrong_role() -> None:
    def override_user() -> CurrentUser:
        return {"user_id": uuid.uuid4(), "tenant_id": str(uuid.uuid4()), "role": UserRole.BILLER}
    test_app.dependency_overrides[get_current_user] = override_user
    try:
        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get("/admin-only")
        assert response.status_code == 403
    finally:
        test_app.dependency_overrides.clear()

@pytest.mark.anyio
async def test_require_role_returns_200_for_correct_role() -> None:
    def override_user() -> CurrentUser:
        return {"user_id": uuid.uuid4(), "tenant_id": str(uuid.uuid4()), "role": UserRole.ADMIN}
    test_app.dependency_overrides[get_current_user] = override_user
    try:
        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get("/admin-only")
        assert response.status_code == 200
    finally:
        test_app.dependency_overrides.clear()
```

### Project Structure Notes

**Files to CREATE:**
- `backend/alembic/versions/0003_add_user_role_enum.py` — migration: PG ENUM type + ALTER column
- `backend/app/core/security/__init__.py` — empty package marker
- `backend/app/core/security/permissions.py` — UserRole, ROLE_HIERARCHY, ROLE_PERMISSIONS, ROLE_DATA_SCOPE, can_assign_role()
- `backend/app/core/dependencies.py` — CurrentUser TypedDict, get_current_user() stub, require_role() factory
- `backend/tests/unit/test_permissions.py` — 7 unit tests
- `backend/tests/unit/test_require_role.py` — 3 integration-style tests

**Files to MODIFY:**
- `backend/app/models/user.py` — role column changed from `Mapped[str]` to `Mapped[UserRole]` with SAEnum

**Files confirmed NO changes needed:**
- `backend/app/api/v1/routes/auth.py` — stub only; routes added in Stories 2.2/2.3
- `backend/app/api/v1/router.py` — `auth` router already mounted
- `backend/app/models/audit_log.py` — append-only, no changes; Story 2.4 uses it for role changes
- `backend/app/core/config.py` — no new settings needed

### Architecture Compliance

1. **No file > 100 lines** — `permissions.py` ≈ 65 lines, `dependencies.py` ≈ 55 lines ✓
2. **mypy --strict** — `UserRole(str, enum.Enum)` satisfies type checker; `Callable[..., Awaitable[CurrentUser]]` for factory return type ✓
3. **No raw SQL in app code** — migration SQL is in Alembic migration file (correct) ✓
4. **`tenant_id` first param** — repositories that add scoped queries in later stories must put `tenant_id` first ✓
5. **Pydantic + SQLAlchemy** — `UserRole(str, enum.Enum)` works with both natively ✓
6. **No secrets hardcoded** — N/A for this story ✓

### Gotchas & Known Pitfalls

**Circular import risk:** `user.py` imports `UserRole` from `app.core.security.permissions`. If any other file in `app.core.security` ever imports from `app.models`, a circular import will occur. `permissions.py` must remain pure Python with zero framework imports.

**`create_type=False` on SAEnum:** If this is omitted, SQLAlchemy will attempt `CREATE TYPE user_role` on first connection, raising `ProgrammingError: type "user_role" already exists`. Always set `create_type=False` when the PG ENUM is created by a migration.

**Migration 0003 on existing data:** If any existing `tenant_users` rows have `role` values outside the 6 valid values, the `USING role::user_role` cast will raise `ERROR: invalid input value for enum user_role`. This is intentional — it ensures data integrity before the ENUM constraint is applied.

**`get_current_user` stub in Story 2.1:** Every endpoint using `require_role()` will return 401 until Story 2.2. This is correct — no auth infrastructure exists yet. All existing tests that hit `/api/v1/health` and `/api/v1/tenants/{id}/features` do NOT use `require_role()`, so they remain unaffected.

**`Depends` inside factory vs. `Depends` as parameter:**
- CORRECT: `async def _check_role(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser`
- WRONG: `async def require_role(...) -> ...: current_user = await get_current_user(request)` — bypasses FastAPI DI

**Test isolation:** `test_require_role.py` creates its own mini `FastAPI()` app to avoid mutating `app.dependency_overrides` on the production `app` instance and causing test cross-contamination. Always call `dependency_overrides.clear()` in `finally`.

### Previous Story Intelligence (Stories 1.1–1.7)

- `docker compose run --rm --no-deps backend pytest` — test runner (not local)
- `docker compose run --rm --no-deps backend sh -c "cd /app && mypy app --strict && ruff check app && pytest"` — full CI equivalent
- `from collections.abc import Callable, Awaitable` — not `typing.Callable` (ruff UP006 flag)
- `mypy --strict` treats `enum.Enum` subclasses correctly — no special annotations needed
- Migration chain: `0001 → 0002 → 0003` — always verify `down_revision` matches previous revision id
- After model changes, rebuild Docker image: `docker compose build backend` — otherwise tests hit stale image
- `asyncio_mode = "auto"` in `pyproject.toml` — use `@pytest.mark.anyio` for async tests

### References

- Story ACs: [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 2 > Story 2.1]
- FR87 (role assignment guard): [Source: `_bmad-output/planning-artifacts/prd.md` — Security requirements]
- FR89 (data visibility): [Source: `_bmad-output/planning-artifacts/epics.md` — Story 2.1 AC]
- Architecture security layer: [Source: `_bmad-output/planning-artifacts/architecture.md` — Security section]
- Backend folder structure: [Source: `_bmad-output/planning-artifacts/architecture.md` — `app/core/security/`, `app/core/dependencies.py`]
- DB naming conventions: [Source: `_bmad-output/planning-artifacts/architecture.md` — "Enums (PG type): snake_case"]
- TenantMixin `tenant_id: Mapped[str]`: [Source: `backend/app/models/base.py:27`]
- Existing `tenant_users` schema (role as VARCHAR): [Source: `backend/alembic/versions/0001_initial_schema_tenants_users_audit_logs.py:63`]
- Previous story patterns (mypy --strict): [Source: `_bmad-output/implementation-artifacts/1-6-feature-flag-infrastructure.md` — Dev Notes]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- ruff UP042: `class UserRole(str, enum.Enum)` → changed to `class UserRole(enum.StrEnum)` (Python 3.11+ pattern)
- ruff E501: docstring line in `can_assign_role` exceeded 88 chars → split across two lines
- ruff I001: `from sqlalchemy import UUID, Boolean, Enum as SAEnum, Index, String, text` — aliased import must be on its own line → split into two import lines
- mypy --strict: used `from collections.abc import Callable, Awaitable` (not `typing`) per UP035

### Completion Notes List

- Used `enum.StrEnum` (not `str, enum.Enum`) per ruff UP042 / Python 3.11+ best practice
- `CurrentUser.tenant_id` is `str` (not `uuid.UUID`) — matches `TenantMixin.Mapped[str]` established in Story 1.2
- `create_type=False` on `SAEnum` is critical — migration 0003 owns the PG ENUM type creation
- Tests use an isolated `_test_app = FastAPI()` (not the production app) to avoid cross-test contamination
- All 68 tests pass: 48 pre-existing + 13 (test_permissions.py) + 6 (test_require_role.py) + 1 (bonus multi-role biller rejected test)

### File List

**Created:**
- `backend/alembic/versions/0003_add_user_role_enum.py`
- `backend/app/core/security/__init__.py`
- `backend/app/core/security/permissions.py`
- `backend/app/core/dependencies.py`
- `backend/tests/unit/test_permissions.py`
- `backend/tests/unit/test_require_role.py`

**Modified:**
- `backend/app/models/user.py` — role column changed to `Mapped[UserRole]` with `SAEnum(..., create_type=False)`
