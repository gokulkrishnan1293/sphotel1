# Story 1.3: Backend Module Scaffold, API Baseline & Health Endpoint

Status: review

## Story

As a **developer**,
I want a modular FastAPI backend with a working health endpoint, response envelope, and module structure,
so that all future backend stories have a consistent, importable pattern to build on.

## Acceptance Criteria

1. **Given** the backend is running, **When** `GET /api/v1/health` is called, **Then** it returns `{ "data": { "status": "ok", "version": "0.1.0" }, "error": null }` with HTTP 200.

2. **And** all API responses use the envelope: `{ "data": {...}, "error": null }` for success or `{ "data": null, "error": { "code": "...", "message": "...", "details": {} } }` for errors — enforced via shared Pydantic models and FastAPI exception handlers.

3. **And** stub route files exist under `app/api/v1/routes/` for all resource domains: `auth.py`, `bills.py`, `kot.py`, `payments.py`, `print_jobs.py`, `menu.py`, `staff.py`, `expenses.py`, `analytics.py`, `gst.py`, `tenants.py`, `super_admin.py` — each declaring an empty `APIRouter` ready for future stories to add endpoints.

4. **And** no route file imports from another route file; cross-domain logic is routed through `app/events/bus.py` (scaffolded as a placeholder) or `app/db/` — no direct service-to-service imports.

5. **And** OpenAPI docs are accessible at `/api/v1/docs` (already configured in `main.py` — verify no regression).

6. **And** `mypy --strict` passes on the entire `app/` directory with zero errors.

7. **And** Ruff linting passes with rules `E,F,I,UP` and `line-length=88`.

## Tasks / Subtasks

- [x] **Task 1: Create `app/schemas/common.py`** (AC: #2)
  - [x] Define `ErrorDetail` Pydantic model: `code: str`, `message: str`, `details: dict[str, object] = {}`
  - [x] Define `DataResponse(BaseModel, Generic[T])`: `data: T`, `error: None = None`
  - [x] Define `ErrorResponse(BaseModel)`: `data: None = None`, `error: ErrorDetail`
  - [x] Add to `app/schemas/__init__.py` exports
  - [x] Keep file ≤100 lines

- [x] **Task 2: Create `app/api/v1/routes/health.py`** (AC: #1, #2)
  - [x] Define `HealthStatus(BaseModel)`: `status: str`, `version: str`
  - [x] Create `router = APIRouter(tags=["health"])`
  - [x] Implement `GET /health` — reads version from `settings.VERSION`, returns `DataResponse[HealthStatus]`
  - [x] Return: `DataResponse(data=HealthStatus(status="ok", version=settings.VERSION))`
  - [x] Keep file ≤100 lines

- [x] **Task 3: Add `VERSION` to `app/core/config.py`** (AC: #1)
  - [x] Add `VERSION: str = "0.1.0"` to `Settings` class
  - [x] Update `app/main.py` to use `version=settings.VERSION` instead of hardcoded string
  - [x] Keep both files ≤100 lines

- [x] **Task 4: Create `app/core/exceptions.py`** (AC: #2)
  - [x] Define `http_exception_handler(request, exc)` → `JSONResponse` in error envelope format
  - [x] Define `validation_exception_handler(request, exc)` → `JSONResponse` for 422 `RequestValidationError`
  - [x] Define `internal_exception_handler(request, exc)` → `JSONResponse` for unhandled 500 errors
  - [x] All handlers return `{"data": null, "error": {"code": "...", "message": "...", "details": {}}}`
  - [x] Keep file ≤100 lines

- [x] **Task 5: Update `app/main.py`** (AC: #2, #5)
  - [x] Register exception handlers from `app/core/exceptions.py`
  - [x] `add_exception_handler(StarletteHTTPException, http_exception_handler)`
  - [x] `add_exception_handler(RequestValidationError, validation_exception_handler)`
  - [x] `add_exception_handler(Exception, internal_exception_handler)`
  - [x] Keep file ≤100 lines

- [x] **Task 6: Update `app/api/v1/router.py`** (AC: #3)
  - [x] Import and mount `health.router` with no prefix (health endpoint is at `/health` under the `/api/v1` prefix)
  - [x] Import all 12 stub routers with `include_router` — each with their appropriate prefix and tags
  - [x] Keep file ≤100 lines (stubs have empty routers so no route conflicts)

- [x] **Task 7: Scaffold stub route files** (AC: #3, #4) — one file per resource domain under `app/api/v1/routes/`
  - [x] `auth.py` — `router = APIRouter(prefix="/auth", tags=["auth"])`
  - [x] `bills.py` — `router = APIRouter(prefix="/bills", tags=["bills"])`
  - [x] `kot.py` — `router = APIRouter(prefix="/kot", tags=["kot"])`
  - [x] `payments.py` — `router = APIRouter(prefix="/payments", tags=["payments"])`
  - [x] `print_jobs.py` — `router = APIRouter(prefix="/print-jobs", tags=["print"])`
  - [x] `menu.py` — `router = APIRouter(prefix="/menu", tags=["menu"])`
  - [x] `staff.py` — `router = APIRouter(prefix="/staff", tags=["staff"])`
  - [x] `expenses.py` — `router = APIRouter(prefix="/expenses", tags=["expenses"])`
  - [x] `analytics.py` — `router = APIRouter(prefix="/analytics", tags=["analytics"])`
  - [x] `gst.py` — `router = APIRouter(prefix="/gst", tags=["gst"])`
  - [x] `tenants.py` — `router = APIRouter(prefix="/tenants", tags=["tenants"])`
  - [x] `super_admin.py` — `router = APIRouter(prefix="/super-admin", tags=["super-admin"])`
  - [x] Each file: router declaration + `# Routes added in Story X.Y` comment, ≤15 lines each

- [x] **Task 8: Scaffold `app/events/bus.py`** (AC: #4)
  - [x] Create `app/events/__init__.py`
  - [x] Create `app/events/bus.py` as a placeholder with a `publish(event_type: str, payload: dict[str, object]) -> None` stub and a `# TODO: implement Valkey pub/sub in Story X.X` comment
  - [x] Keep file ≤50 lines

- [x] **Task 9: Write tests** (AC: #1, #2)
  - [x] Create `tests/integration/routes/` directory with `__init__.py`
  - [x] Create `tests/integration/__init__.py`
  - [x] Create `tests/integration/routes/test_health.py`
    - [x] Test `GET /api/v1/health` → HTTP 200
    - [x] Test response body matches `{"data": {"status": "ok", "version": "0.1.0"}, "error": null}`
    - [x] Test that response Content-Type is `application/json`
  - [x] Create `tests/unit/` and `tests/unit/schemas/` directories with `__init__.py` files
  - [x] Create `tests/unit/schemas/test_common.py`
    - [x] Test `DataResponse` serializes to `{"data": ..., "error": null}`
    - [x] Test `ErrorResponse` serializes to `{"data": null, "error": {"code": "...", "message": "...", "details": {}}}`
    - [x] Test `ErrorDetail` default `details` is `{}`
  - [x] Use `httpx.AsyncClient` with `ASGITransport(app=app)` for route tests (no real DB needed for health)
  - [x] Verify `httpx` is in `pyproject.toml` dev dependencies — add `httpx>=0.27` if missing

- [x] **Task 10: Verify quality gates** (AC: #6, #7)
  - [x] `mypy --strict` passes on entire `app/` directory: 0 errors (38 source files checked)
  - [x] `ruff check app` passes: 0 violations
  - [x] All new tests pass: 10/10 — pytest `tests/unit/schemas/` + `tests/integration/routes/test_health.py`

## Dev Notes

### Architecture — Layer-Based Structure (Authoritative)

**IMPORTANT DISCREPANCY:** The epics.md story 1.3 acceptance criteria reference `app/modules/{domain}/` (module-per-feature layout). The architecture document — which is more detailed and authoritative — specifies a **layer-based** structure: `app/api/v1/routes/`, `app/models/`, `app/schemas/`, `app/services/`, `app/repositories/`. Stories 1.1 and 1.2 already scaffolded this layer structure. This story **follows the architecture**, not the epics literal text.

The semantic intent of "module scaffold" from epics is fulfilled by creating stub route files for each domain under `app/api/v1/routes/` — these are the entry points future stories will populate.

### Response Envelope Pattern

Every API response MUST use the wrapped envelope. Architecture mandate:

```python
# Success
{"data": {"id": "...", "status": "draft"}, "error": None}

# Error
{"data": None, "error": {"code": "HEALTH_CHECK_FAILED", "message": "...", "details": {}}}
```

The `DataResponse[T]` generic in `app/schemas/common.py` is the canonical type for all success responses. Pydantic v2 generics require `Generic[T]` mixin:

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class DataResponse(BaseModel, Generic[T]):  # noqa: UP046
    data: T
    error: None = None
```

**mypy note:** With `mypy --strict`, returning `DataResponse(data=HealthStatus(...))` must be fully typed. Annotate the endpoint return type as `DataResponse[HealthStatus]`, not just `dict`.

### Exception Handlers

FastAPI exception handlers must be registered on the `app` instance in `main.py`. The handlers format all errors into the envelope:

```python
# app/core/exceptions.py
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"data": None, "error": {"code": str(exc.status_code), "message": str(exc.detail), "details": {}}},
    )

async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"data": None, "error": {"code": "VALIDATION_ERROR", "message": "Request validation failed", "details": {"errors": exc.errors()}}},
    )
```

**Note:** `exc.errors()` on `RequestValidationError` returns `list[dict]` — the `details` field accepts `dict[str, object]` so use `{"errors": exc.errors()}`.

### Pydantic Alias Generator — NOT needed for this story

The architecture mandates `alias_generator=to_camel` for **API response fields** that need camelCase JSON output (e.g., `billNumber` not `bill_number`). The health response fields (`status`, `version`) are already single-word, so no alias is needed here. Future stories (billing, auth) will use it. Do not add it to `HealthStatus` or `DataResponse`.

### VERSION field

The health endpoint must return `"version": "0.1.0"` (from Story 1.2, `pyproject.toml` already sets `version = "0.1.0"`). Add `VERSION: str = "0.1.0"` to `Settings` as a simple default. This ensures the health response is driven by config, not hardcoded in the route.

### OpenAPI Docs

`app/main.py` already sets `docs_url="/api/v1/docs"`. This satisfies AC #5. Verify it's accessible at runtime — no new code needed.

### Cross-Module Isolation Rule

From epics: "modules do not import from each other directly — cross-module communication uses a shared `app/events/` bus or `app/db/` layer only."

In the layer-based architecture, this means:
- `app/api/v1/routes/bills.py` MUST NOT import from `app/api/v1/routes/payments.py`
- `app/services/bill_create_service.py` MUST NOT import from `app/services/payment_service.py` directly
- Cross-domain events (e.g., billing triggers a Telegram alert) go through `app/events/bus.py`
- Shared DB access goes through `app/db/session.py`

The `app/events/bus.py` placeholder created in this story satisfies the scaffolding requirement. Full implementation (Valkey pub/sub) is deferred to a later story.

### Test Approach — No Real DB Required

The health endpoint has no DB dependency. Use `httpx.AsyncClient` with `ASGITransport`:

```python
import pytest
import httpx
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_returns_200() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
```

**Note on anyio marker:** `pytest.ini_options` has `asyncio_mode = "auto"` — use `@pytest.mark.asyncio` (from `pytest-asyncio`) or simply write `async def test_...` with no marker if asyncio_mode auto handles it. Both work — `@pytest.mark.asyncio` was used in this story for explicitness.

### Recommended `conftest.py` update for test env vars

```python
# tests/conftest.py
import os

# Set required env vars before any app import to avoid pydantic-settings failures
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("VALKEY_URL", "redis://localhost:6379")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-only-not-for-production")
```

This is a one-time setup that keeps tests runnable in CI without a real DB when the endpoint under test doesn't use the DB. Story 2.1 will replace this with proper test DB fixtures.

### Files to Create/Modify

**Create:**
- `backend/app/schemas/common.py` — DataResponse, ErrorDetail, ErrorResponse generics
- `backend/app/api/v1/routes/__init__.py` — empty
- `backend/app/api/v1/routes/health.py` — health endpoint
- `backend/app/api/v1/routes/auth.py` — stub
- `backend/app/api/v1/routes/bills.py` — stub
- `backend/app/api/v1/routes/kot.py` — stub
- `backend/app/api/v1/routes/payments.py` — stub
- `backend/app/api/v1/routes/print_jobs.py` — stub
- `backend/app/api/v1/routes/menu.py` — stub
- `backend/app/api/v1/routes/staff.py` — stub
- `backend/app/api/v1/routes/expenses.py` — stub
- `backend/app/api/v1/routes/analytics.py` — stub
- `backend/app/api/v1/routes/gst.py` — stub
- `backend/app/api/v1/routes/tenants.py` — stub
- `backend/app/api/v1/routes/super_admin.py` — stub
- `backend/app/core/exceptions.py` — HTTP/validation/500 exception handlers
- `backend/app/events/__init__.py` — empty
- `backend/app/events/bus.py` — placeholder event bus
- `backend/tests/integration/__init__.py` — empty
- `backend/tests/integration/routes/__init__.py` — empty
- `backend/tests/integration/routes/test_health.py` — health endpoint integration tests
- `backend/tests/unit/__init__.py` — empty
- `backend/tests/unit/schemas/__init__.py` — empty
- `backend/tests/unit/schemas/test_common.py` — envelope schema unit tests

**Modify:**
- `backend/app/schemas/__init__.py` — export common schemas
- `backend/app/core/config.py` — add `VERSION: str = "0.1.0"`
- `backend/app/api/v1/router.py` — mount health + all stub routers
- `backend/app/main.py` — register exception handlers, use `settings.VERSION`
- `backend/tests/conftest.py` — add env var defaults (replaced TODO comment)

### Project Structure Notes

- `app/api/v1/routes/` directory does NOT exist yet — Task 7 creates it along with the 12 stub files
- All new files must be ≤100 lines each — stubs will be 10-15 lines, well within limit
- `app/events/` directory does NOT exist yet — Task 8 creates it
- `tests/unit/` and `tests/integration/` directories do NOT exist yet — Task 9 creates them
- No frontend changes in this story
- No new DB migrations in this story (no new models)
- The `app/api/v1/router.py` currently has 4 lines — mounting all 13 routers will push it toward the 100-line limit; keep imports tidy using a list comprehension or group them

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 1, Story 1.3, lines 457–474]
- [Source: _bmad-output/planning-artifacts/architecture.md — API Patterns, Structure Patterns, All AI Agents MUST rules]
- [Source: _bmad-output/planning-artifacts/architecture.md — `app/api/v1/routes/` directory layout]
- [Source: _bmad-output/planning-artifacts/architecture.md — Response Envelope (Format Patterns section)]
- [Source: _bmad-output/implementation-artifacts/1-1-monorepo-scaffold-docker-dev-environment.md — pyproject.toml deps, asyncio_mode=auto]
- [Source: _bmad-output/implementation-artifacts/1-2-database-migration-framework-schema-conventions.md — conftest.py TODO note, mypy --strict pattern]
- [FastAPI Exception Handlers: https://fastapi.tiangolo.com/tutorial/handling-errors/]
- [Pydantic v2 Generics: https://docs.pydantic.dev/latest/concepts/postponed_annotations/]
- [httpx ASGI transport: https://www.python-httpx.org/async/]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Ruff UP046 (`Generic` subclass vs type parameters): Since the auto-fix is marked `--unsafe-fixes` by ruff (Pydantic v2 compatibility risk), used `# noqa: UP046` on `DataResponse` class definition. All other ruff violations: 0.
- Exception handler typing: FastAPI's `add_exception_handler` expects `Callable[..., Any]`. Used `Exception` as the base type in all handler signatures and narrowed with `isinstance` checks inside to satisfy mypy --strict without `# type: ignore`.

### Completion Notes List

- ✅ `backend/app/schemas/common.py` — `DataResponse[T]` (generic envelope), `ErrorDetail`, `ErrorResponse`. `# noqa: UP046` on Generic class to prevent unsafe ruff auto-fix.
- ✅ `backend/app/schemas/__init__.py` — exports all three envelope types.
- ✅ `backend/app/api/v1/routes/health.py` — `GET /health` with `DataResponse[HealthStatus]` return. Reads version from `settings.VERSION`.
- ✅ `backend/app/core/config.py` — added `VERSION: str = "0.1.0"`.
- ✅ `backend/app/core/exceptions.py` — three exception handlers (HTTP, validation, 500). All accept `Exception` base type; narrow with isinstance for mypy compliance.
- ✅ `backend/app/main.py` — registered all three exception handlers; uses `settings.VERSION` for FastAPI app version.
- ✅ `backend/app/api/v1/router.py` — mounts health router + 12 domain stub routers.
- ✅ `backend/app/api/v1/routes/` — created directory with `__init__.py` and 12 stub route files (auth, bills, kot, payments, print_jobs, menu, staff, expenses, analytics, gst, tenants, super_admin).
- ✅ `backend/app/events/bus.py` — placeholder `publish()` stub with TODO for Valkey pub/sub.
- ✅ `backend/tests/conftest.py` — replaced TODO comment with `os.environ.setdefault()` calls for test env vars.
- ✅ `backend/tests/integration/routes/test_health.py` — 4 integration tests for health endpoint (200, body, content-type, envelope schema).
- ✅ `backend/tests/unit/schemas/test_common.py` — 6 unit tests for envelope schemas.
- ✅ mypy --strict: 0 errors across 38 source files.
- ✅ ruff check app: All checks passed.
- ✅ pytest: 25/25 tests pass (15 from Story 1.2, 10 new).

### File List

**Created:**
- `backend/app/schemas/common.py`
- `backend/app/api/v1/routes/__init__.py`
- `backend/app/api/v1/routes/health.py`
- `backend/app/api/v1/routes/auth.py`
- `backend/app/api/v1/routes/bills.py`
- `backend/app/api/v1/routes/kot.py`
- `backend/app/api/v1/routes/payments.py`
- `backend/app/api/v1/routes/print_jobs.py`
- `backend/app/api/v1/routes/menu.py`
- `backend/app/api/v1/routes/staff.py`
- `backend/app/api/v1/routes/expenses.py`
- `backend/app/api/v1/routes/analytics.py`
- `backend/app/api/v1/routes/gst.py`
- `backend/app/api/v1/routes/tenants.py`
- `backend/app/api/v1/routes/super_admin.py`
- `backend/app/core/exceptions.py`
- `backend/app/events/__init__.py`
- `backend/app/events/bus.py`
- `backend/tests/integration/__init__.py`
- `backend/tests/integration/routes/__init__.py`
- `backend/tests/integration/routes/test_health.py`
- `backend/tests/unit/__init__.py`
- `backend/tests/unit/schemas/__init__.py`
- `backend/tests/unit/schemas/test_common.py`

**Modified:**
- `backend/app/schemas/__init__.py`
- `backend/app/core/config.py`
- `backend/app/api/v1/router.py`
- `backend/app/main.py`
- `backend/tests/conftest.py`
