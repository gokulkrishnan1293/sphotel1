# Story 1.2: Database Migration Framework & Schema Conventions

Status: review

## Story

As a **developer**,
I want Alembic migrations configured with naming conventions and a base schema locked,
so that all future stories have a consistent, predictable way to evolve the database schema.

## Acceptance Criteria

1. **Given** `make migrate` is run against a fresh PostgreSQL instance, **When** all existing migrations are applied, **Then** the database contains: `tenants`, `tenant_users`, `audit_logs` tables with correct column types.

2. **And** all monetary columns use `INTEGER` (paise) — no `FLOAT` or `DECIMAL` for currency anywhere in the schema.

3. **And** all timestamp columns use `TIMESTAMPTZ` (UTC) — no `TIMESTAMP WITHOUT TIME ZONE`.

4. **And** table names are `snake_case` plural; column names `snake_case`; foreign keys `{singular_table}_id`; indexes `idx_{table}_{column}`.

5. **And** `audit_logs` is append-only with a DB-level trigger that raises an exception on UPDATE or DELETE.

6. **And** Alembic's `env.py` is configured for async SQLAlchemy and runs migrations in a transaction.

7. **And** `make migrate` is idempotent — running it twice produces no errors.

## Tasks / Subtasks

- [x] **Task 1: Expand `backend/app/models/base.py`** (AC: #4)
  - [x] Add `MetaData` with Alembic naming convention dict (see Dev Notes for exact convention)
  - [x] Update `Base = DeclarativeBase` to use the named metadata: `class Base(DeclarativeBase): metadata = named_metadata`
  - [x] Add `TenantMixin` with `tenant_id: Mapped[str]` as a non-nullable column
  - [x] Add `TimestampMixin` with `created_at: Mapped[datetime]` (TIMESTAMPTZ, server_default=now()) and `updated_at: Mapped[datetime]` (TIMESTAMPTZ, onupdate=now())
  - [x] Keep file ≤100 lines — these mixins are concise

- [x] **Task 2: Create `backend/app/models/tenant.py`** (AC: #1, #2, #3, #4)
  - [x] Table name: `tenants`
  - [x] Columns: `id` (UUID, primary key, server_default=gen_random_uuid()), `name` (VARCHAR NOT NULL), `slug` (VARCHAR UNIQUE NOT NULL — URL-safe tenant identifier), `is_active` (BOOLEAN, default=True), `created_at` (TIMESTAMPTZ), `updated_at` (TIMESTAMPTZ)
  - [x] Index: `idx_tenants_slug` on `slug`
  - [x] Does NOT use TenantMixin (tenants table itself has no tenant_id FK — it IS the tenant)
  - [x] Uses TimestampMixin

- [x] **Task 3: Create `backend/app/models/user.py`** (AC: #1, #2, #3, #4)
  - [x] Table name: `tenant_users`
  - [x] Columns: `id` (UUID PK), `tenant_id` (VARCHAR NOT NULL), `name` (VARCHAR NOT NULL), `role` (VARCHAR NOT NULL — enum-like; full Postgres ENUM added in Story 2.1), `pin_hash` (VARCHAR NULLABLE — operational roles), `email` (VARCHAR NULLABLE — admin roles), `password_hash` (VARCHAR NULLABLE), `totp_secret` (VARCHAR NULLABLE), `is_active` (BOOLEAN default=True), `created_at` (TIMESTAMPTZ), `updated_at` (TIMESTAMPTZ)
  - [x] Index: `idx_tenant_users_tenant_id` on `tenant_id`
  - [x] Index: `idx_tenant_users_email` on `email` (for admin login lookup)
  - [x] Uses TenantMixin + TimestampMixin

- [x] **Task 4: Create `backend/app/models/audit_log.py`** (AC: #1, #3, #4, #5)
  - [x] Table name: `audit_logs`
  - [x] Columns: `id` (UUID PK), `tenant_id` (VARCHAR NOT NULL — NOT a FK, denormalized for immutability), `actor_id` (UUID NULLABLE — NULL for system events), `action` (VARCHAR NOT NULL — e.g. "staff.pin_reset", "bill.void_approved"), `target_id` (UUID NULLABLE — the resource acted upon), `payload` (JSONB NULLABLE — additional context), `created_at` (TIMESTAMPTZ, server_default=now(), NOT NULL)
  - [x] **NO `updated_at`** — append-only records have no updates
  - [x] Index: `idx_audit_logs_tenant_id` on `tenant_id`
  - [x] Index: `idx_audit_logs_actor_id` on `actor_id`
  - [x] DB-level trigger to prevent UPDATE and DELETE — added manually in migration upgrade()
  - [x] Trigger added in migration (not `__table_args__`) — DB-only DDL

- [x] **Task 5: Update `backend/alembic/env.py`** (AC: #6)
  - [x] Add model imports: `from app.models import tenant, user, audit_log  # noqa: F401`
  - [x] Remove/replace the `# Story 1.2 will add:` comment with actual imports
  - [x] Pass `transaction_per_migration=True` to `context.configure()` for transactional DDL
  - [x] Keep the async pattern from Story 1.1 intact

- [x] **Task 6: Generate and write the initial Alembic migration** (AC: #1–#7)
  - [x] Migration written manually as `0001_initial_schema_tenants_users_audit_logs.py`
  - [x] Migration includes append-only trigger DDL for `audit_logs` in `upgrade()`
  - [x] Migration fully reversible: `downgrade()` drops trigger + function first, then tables in reverse order
  - [x] Deleted `backend/alembic/versions/.gitkeep`
  - [x] Migration uses `sa.DateTime(timezone=True)` for all timestamp columns (TIMESTAMPTZ)

- [x] **Task 7: Update `backend/app/models/__init__.py`** (AC: #6)
  - [x] Imports all model modules so `Base.metadata` registers all tables
  - [x] Comment explains purpose for Alembic autogenerate

- [x] **Task 8: End-to-end verification** (AC: #1–#7)
  - [x] mypy --strict: 0 errors across 20 source files
  - [x] ruff check app: all checks passed
  - [x] pytest 15/15 tests pass (ORM structure tests verify schema conventions, TIMESTAMPTZ, no FK on audit_logs, no Float columns, all tables registered)
  - [ ] `make migrate` against live DB: to be verified when Docker environment is available
  - [ ] Verify trigger via psql: to be verified when Docker environment is available

---

## Dev Notes

### Critical Architecture Constraints (Read First)

- **100-line file limit:** Every file in `backend/app/` must stay under 100 lines. Split immediately when violated.
- **Money = integer paise ALWAYS:** No `FLOAT` or `DECIMAL` columns for money — use `INTEGER` (paise). This is enforced at schema level.
- **TIMESTAMPTZ UTC only:** Every timestamp column uses `TIMESTAMPTZ`. Never `TIMESTAMP` or `TIMESTAMP WITHOUT TIME ZONE`.
- **tenant_id on every entity:** Every future model (except `tenants` itself) must have `tenant_id`. Use `TenantMixin`.
- **No raw SQL in services:** SQLAlchemy ORM only for application queries. The trigger DDL in the migration is an exception (DDL executed once at migration time, not in application code).
- **No `any` in Python:** `mypy --strict` must pass — all model columns fully typed.

---

### `base.py` — Naming Convention + Mixins

The current `backend/app/models/base.py` is a minimal stub. Story 1.2 **replaces** its content entirely:

```python
from datetime import datetime
from sqlalchemy import MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Alembic naming convention — ensures auto-generated constraint names are
# deterministic and migration-safe across databases.
# Index pattern uses "idx_" prefix to match project convention.
NAMING_CONVENTION: dict[str, str] = {
    "ix": "idx_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

named_metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Base(DeclarativeBase):
    metadata = named_metadata


class TenantMixin:
    """Adds tenant_id to any model. EVERY model except Tenant itself uses this."""
    tenant_id: Mapped[str] = mapped_column(nullable=False, index=True)


class TimestampMixin:
    """Adds created_at and updated_at (both TIMESTAMPTZ UTC)."""
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )
```

> **Why replace the stub?** The `MetaData(naming_convention=...)` must be set on `Base.metadata` *before* any model is defined. Without it, Alembic autogenerate produces unnamed constraints — unmergeable across branches.

---

### Alembic `env.py` Changes

Add exactly these lines to the imports section (replacing the comment):
```python
from app.models import base as _base  # noqa: F401 — registers Base.metadata
from app.models import tenant as _tenant  # noqa: F401
from app.models import user as _user  # noqa: F401
from app.models import audit_log as _audit_log  # noqa: F401
```

Add `transaction_per_migration=True` to `context.configure()`:
```python
context.configure(
    connection=conn,
    target_metadata=target_metadata,
    transaction_per_migration=True,  # DDL in atomic transactions
)
```

---

### Append-Only Trigger for `audit_logs`

Alembic autogenerate **does not** produce PostgreSQL trigger DDL. Add this manually in the migration's `upgrade()` function:

```python
from alembic import op

def upgrade() -> None:
    # ... (autogenerated table creation code) ...

    # Append-only enforcement for audit_logs
    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_audit_log_modification()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'audit_logs are append-only: % on % is forbidden',
                TG_OP, TG_TABLE_NAME;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER audit_logs_no_update_delete
        BEFORE UPDATE OR DELETE ON audit_logs
        FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_modification();
    """)

def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS audit_logs_no_update_delete ON audit_logs;")
    op.execute("DROP FUNCTION IF EXISTS prevent_audit_log_modification;")
    # ... (autogenerated table drop code) ...
```

> Drop tables in reverse FK order in `downgrade()`: `audit_logs` → `tenant_users` → `tenants`.

---

### UUID Primary Keys — PostgreSQL `gen_random_uuid()`

Use `server_default` with `gen_random_uuid()` for all UUID PKs:

```python
import uuid
from sqlalchemy import UUID, text
from sqlalchemy.orm import Mapped, mapped_column

class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
```

> `gen_random_uuid()` is built into PostgreSQL 13+. Do NOT use Python `uuid.uuid4()` as `default=` — that bypasses DB-level generation and breaks bulk inserts.

---

### `tenants` Table Schema

```
tenants
  id          UUID PK (gen_random_uuid())
  name        VARCHAR NOT NULL
  slug        VARCHAR NOT NULL UNIQUE   -- URL-safe, e.g. "sphotel-goa"
  is_active   BOOLEAN NOT NULL DEFAULT TRUE
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()

Indexes: idx_tenants_slug (on slug)
```

---

### `tenant_users` Table Schema

```
tenant_users
  id            UUID PK (gen_random_uuid())
  tenant_id     VARCHAR NOT NULL (denormalized string, not UUID FK — simplifies RLS later)
  name          VARCHAR NOT NULL
  role          VARCHAR NOT NULL    -- 'biller'|'waiter'|'kitchen_staff'|'manager'|'admin'|'super_admin'
  pin_hash      VARCHAR NULLABLE   -- bcrypt hash, operational roles only
  email         VARCHAR NULLABLE   -- admin/super_admin only
  password_hash VARCHAR NULLABLE   -- admin/super_admin only
  totp_secret   VARCHAR NULLABLE   -- admin/super_admin TOTP
  is_active     BOOLEAN NOT NULL DEFAULT TRUE
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()

Indexes:
  idx_tenant_users_tenant_id (on tenant_id)
  idx_tenant_users_email (on email)
```

> `tenant_id` is `VARCHAR` (not `UUID FK`) on `tenant_users` to allow future RLS `SET LOCAL app.current_tenant_id = '...'` using `current_setting()`. The architecture team chose string-typed tenant context variables for RLS compatibility.

---

### `audit_logs` Table Schema

```
audit_logs
  id         UUID PK (gen_random_uuid())
  tenant_id  VARCHAR NOT NULL    -- denormalized string (not FK)
  actor_id   UUID NULLABLE       -- NULL for system events
  action     VARCHAR NOT NULL    -- e.g. "staff.pin_reset", "bill.void_approved"
  target_id  UUID NULLABLE       -- resource acted upon
  payload    JSONB NULLABLE      -- extra context
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
  -- NO updated_at — append-only

Indexes:
  idx_audit_logs_tenant_id (on tenant_id)
  idx_audit_logs_actor_id (on actor_id)

Trigger: audit_logs_no_update_delete — RAISES EXCEPTION on UPDATE or DELETE
```

---

### models/__init__.py

The `__init__.py` in `app/models/` must import all model modules so that `Base.metadata` is populated when `alembic/env.py` imports `base`:

```python
# app/models/__init__.py
# IMPORTANT: Import all model modules here so Base.metadata registers all tables.
# Alembic autogenerate reads Base.metadata — missing imports = missing tables in migrations.
from app.models import base  # noqa: F401
from app.models import tenant  # noqa: F401
from app.models import user  # noqa: F401
from app.models import audit_log  # noqa: F401
```

---

### Story 1.1 Learnings — Relevant to This Story

From Story 1.1 Dev Agent completion notes:
- `backend/alembic/versions/.gitkeep` was created as a placeholder — **delete it** when the first real migration file is created.
- The async Alembic pattern in `env.py` uses `asyncio.run(do_run())` — do NOT change this pattern.
- `backend/tests/conftest.py` has `# TODO: add test DB fixtures in Story 2.1` — no test fixtures needed in this story; keep conftest.py unchanged.
- All backend files must be ≤100 lines — the new model files should each be well under this limit.
- `pyproject.toml` already has `asyncpg>=0.29` and `alembic>=1.13` in dependencies — no new deps needed.

---

### Files to Create/Modify

**Modify:**
- `backend/app/models/base.py` — expand with naming convention, TenantMixin, TimestampMixin (replaces stub)
- `backend/app/models/__init__.py` — add model imports
- `backend/alembic/env.py` — add model imports + `transaction_per_migration=True`

**Create:**
- `backend/app/models/tenant.py` — Tenant model
- `backend/app/models/user.py` — TenantUser model
- `backend/app/models/audit_log.py` — AuditLog model (append-only)
- `backend/alembic/versions/XXXX_initial_schema_tenants_users_audit_logs.py` — first migration

**Delete:**
- `backend/alembic/versions/.gitkeep` — replaced by the actual migration file

---

### Project Structure Notes

- All model files go in `backend/app/models/` — one file per model (per architecture spec)
- Alembic migration files go in `backend/alembic/versions/` — Alembic auto-names them with timestamp prefix
- No frontend changes in this story
- `make migrate` = `cd backend && alembic upgrade head` (from Story 1.1 Makefile)

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 1, Story 1.2, lines 439–456]
- [Source: _bmad-output/planning-artifacts/architecture.md — Naming Patterns (line 250), Structure Patterns (line 355), All AI Agents MUST (line 452)]
- [Source: _bmad-output/implementation-artifacts/1-1-monorepo-scaffold-docker-dev-environment.md — Alembic env.py pattern, Dev Notes, Completion Notes]
- [SQLAlchemy MetaData naming_convention: https://docs.sqlalchemy.org/en/20/core/constraints.html#configuring-constraint-naming-conventions]
- [Alembic async cookbook: https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic]
- [Alembic autogenerate: https://alembic.sqlalchemy.org/en/latest/autogenerate.html]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- ✅ `backend/app/models/base.py` — replaced stub with `MetaData(naming_convention=...)`, `TenantMixin`, `TimestampMixin`. All timestamps use `DateTime(timezone=True)` explicitly for TIMESTAMPTZ.
- ✅ `backend/app/models/tenant.py` — `Tenant` model with UUID PK (`gen_random_uuid()`), `slug` (UNIQUE), `TimestampMixin`. No `TenantMixin` (tenants table IS the tenant).
- ✅ `backend/app/models/user.py` — `TenantUser` model with `TenantMixin` + `TimestampMixin`. All credential fields nullable. Used `str | None` (UP045 compliant).
- ✅ `backend/app/models/audit_log.py` — `AuditLog` append-only model. No `updated_at`. `tenant_id` is plain `VARCHAR` (not FK) for immutability.
- ✅ `backend/alembic/env.py` — Added model imports, `transaction_per_migration=True`.
- ✅ `backend/alembic/versions/0001_initial_schema_tenants_users_audit_logs.py` — Full migration with all 3 tables + append-only trigger DDL for `audit_logs`. Fully reversible `downgrade()`.
- ✅ `backend/alembic/versions/.gitkeep` — Deleted (replaced by actual migration).
- ✅ `backend/app/models/__init__.py` — Updated to import all model modules for Alembic autogenerate.
- ✅ `backend/pyproject.toml` — Added `[build-system]` section + `version = "0.1.0"` + `[tool.setuptools.packages.find]` for local venv install. Also fixed import ordering in `main.py` and `session.py` (pre-existing ruff violations).
- ✅ 15 unit tests written validating naming conventions, TIMESTAMPTZ, no Float money columns, no FK on audit_logs, all tables registered.
- ✅ mypy --strict: 0 errors | ruff: all checks passed | pytest: 15/15

### File List

**Modified:**
- `backend/app/models/base.py`
- `backend/app/models/__init__.py`
- `backend/alembic/env.py`
- `backend/pyproject.toml`
- `backend/app/db/session.py` (import sort fix from Story 1.1)
- `backend/app/main.py` (import sort fix from Story 1.1)

**Created:**
- `backend/app/models/tenant.py`
- `backend/app/models/user.py`
- `backend/app/models/audit_log.py`
- `backend/alembic/versions/0001_initial_schema_tenants_users_audit_logs.py`
- `backend/tests/test_models_schema.py`
- `backend/.venv/` (local development venv — not committed)

**Deleted:**
- `backend/alembic/versions/.gitkeep`
