# Story 2.2: PIN Authentication for Operational Roles

Status: review

## Story

As a **Biller, Waiter, Kitchen Staff, or Manager**,
I want to authenticate with my PIN and receive a short-lived session token,
so that I can access my role's features quickly without a full login flow, and every action I take is tagged to my identity.

## Acceptance Criteria

1. **Given** a valid PIN is submitted to `POST /api/v1/auth/pin`, **When** the PIN matches a `tenant_users` record, **Then** a short-lived JWT (4-hour expiry) is set in an `httpOnly` cookie — never in the response body or localStorage.

2. **And** the JWT payload contains: `user_id` (str UUID), `tenant_id` (str), `role` (str), `iat`, `exp`.

3. **And** `POST /api/v1/auth/pin` is rate-limited to 5 attempts per minute per IP via `slowapi`; after 5 failures the endpoint returns HTTP 429.

4. **And** after 5 consecutive failed PIN attempts for a specific user, that account is locked in Valkey (no TTL — requires Admin reset) and subsequent attempts return HTTP 403 with `{"code": "ACCOUNT_LOCKED"}`.

5. **And** the PIN auth endpoint rejects `ADMIN` and `SUPER_ADMIN` role users with HTTP 403 — those roles must use Story 2.3's email+TOTP flow.

6. **And** `get_current_user` in `app/core/dependencies.py` is replaced with real JWT cookie extraction: extracts `access_token` cookie, validates JWT, returns `CurrentUser` — raises HTTP 401 if cookie is missing or token is invalid/expired.

7. **And** all sessions auto-expire after 4 hours (JWT `exp` claim enforced on every request by `get_current_user`).

8. **And** `mypy --strict` and `ruff check` pass with zero errors on all new/modified files.

## Tasks / Subtasks

- [x] **Task 1: Add new dependencies to `pyproject.toml`** (AC: #1, #3)
  - [x] Add `bcrypt>=4.1` — PIN hashing (direct, no passlib wrapper)
  - [x] Add `PyJWT>=2.8` — JWT creation and validation
  - [x] Rebuild backend Docker image: `docker compose build backend`
  - [x] Verify imports work: `bcrypt 5.0.0`, `PyJWT 2.12.1` confirmed

- [x] **Task 2: Extend `app/core/config.py`** (AC: #2, #7)
  - [x] Add `JWT_ALGORITHM: str = "HS256"` to `Settings`
  - [x] Add `JWT_EXPIRY_HOURS: int = 4` to `Settings`
  - [x] `SECRET_KEY` already exists — used as JWT signing secret ✓

- [x] **Task 3: Create `app/core/security/pin.py`** (AC: #1, #4)
  - [x] `hash_pin(pin: str) -> str` — bcrypt hash with 12 rounds, returns str for DB storage
  - [x] `verify_pin(pin: str, pin_hash: str) -> bool` — returns `bcrypt.checkpw(pin.encode(), pin_hash.encode())`
  - [x] File ≤ 20 lines; no imports from app modules (pure crypto utility)

- [x] **Task 4: Create `app/core/security/jwt.py`** (AC: #2, #7)
  - [x] `create_access_token(user_id: uuid.UUID, tenant_id: str, role: UserRole) -> str`
  - [x] `decode_access_token(token: str) -> dict[str, object]`
  - [x] Import `jwt` (PyJWT package) — NOT `from jose import jwt`
  - [x] mypy fix: assigned `jwt.decode` result to typed variable to satisfy strict mode

- [x] **Task 5: Create `app/core/security/rate_limiter.py`** (AC: #3)
  - [x] `limiter = Limiter(key_func=get_remote_address)` from `slowapi`

- [x] **Task 6: Update `app/main.py` — wire slowapi** (AC: #3)
  - [x] `app.state.limiter = limiter`
  - [x] `app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)` with `# type: ignore[arg-type]`

- [x] **Task 7: Create `app/schemas/auth.py`** (AC: #1)
  - [x] `class PinLoginRequest(BaseModel)`: `user_id: uuid.UUID`, `pin: str = Field(min_length=4, max_length=8)`
  - [x] `class LoginResponse(BaseModel)`: `message: str`
  - [x] No `TokenResponse` — JWT in cookie only

- [x] **Task 8: Implement `POST /api/v1/auth/pin` in `app/api/v1/routes/auth.py`** (AC: #1–#5)
  - [x] Rate limit decorator: `@limiter.limit("5/minute")`
  - [x] Lookup user by `body.user_id` via SQLAlchemy async query
  - [x] HTTP 401 for not found / inactive / no pin_hash (generic, prevents enumeration)
  - [x] HTTP 403 `ACCOUNT_LOCKED` if Valkey key `auth_locked:{user.id}` exists
  - [x] HTTP 403 `ROLE_NOT_ALLOWED` if ADMIN or SUPER_ADMIN role
  - [x] Lockout logic: `auth_attempts:{user.id}` incr (60s TTL) → lock at ≥5
  - [x] Cookie: `httponly=True`, `samesite="lax"`, `path="/api"`, `max_age=14400`

- [x] **Task 9: Replace `get_current_user` stub in `app/core/dependencies.py`** (AC: #6, #7)
  - [x] Extracts `access_token` cookie, validates JWT, returns `CurrentUser`
  - [x] HTTP 401 on missing cookie or invalid/expired JWT
  - [x] All 6 existing `require_role` tests still pass (dependency_overrides bypass)

- [x] **Task 10: Unit tests** (AC: #8)
  - [x] `backend/tests/unit/test_pin.py` — 4 tests (hash format, correct/wrong PIN, unique salts)
  - [x] `backend/tests/unit/test_jwt.py` — 4 tests (create, round-trip decode, expired, tampered)

- [x] **Task 11: Run full test suite** (AC: #8)
  - [x] mypy --strict: 50 files, 0 errors
  - [x] ruff: all checks passed
  - [x] pytest: **76/76 passed** (68 prior + 8 new, zero regressions)

## Dev Notes

### Dependency additions — why these libraries

**`bcrypt>=4.1`** (direct, not via `passlib`):
- `passlib` is largely unmaintained (last release 2022); its `bcrypt` wrapper has known deprecation warnings with bcrypt ≥4
- Python 3.12+ project → use `bcrypt` directly: clean API, actively maintained, same security
- DO NOT add `passlib` — use `bcrypt` module directly

**`PyJWT>=2.8`** (not `python-jose`):
- `python-jose` is unmaintained (last release 2023) and has known CVEs in older versions
- `PyJWT` is the maintained standard — FastAPI docs have moved toward recommending it
- Import as `import jwt` (the package name is `PyJWT` but it imports as `jwt`)

### Task 3 — `app/core/security/pin.py` exact implementation

```python
import bcrypt

_ROUNDS = 12  # cost factor — ~100ms on modern hardware; tune if needed


def hash_pin(pin: str) -> str:
    """Hash a plaintext PIN with bcrypt. Returns str for storage in DB."""
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt(rounds=_ROUNDS)).decode()


def verify_pin(pin: str, pin_hash: str) -> bool:
    """Return True if pin matches the stored bcrypt hash."""
    return bool(bcrypt.checkpw(pin.encode(), pin_hash.encode()))
```

### Task 4 — `app/core/security/jwt.py` exact implementation

```python
import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import settings
from app.core.security.permissions import UserRole


def create_access_token(
    user_id: uuid.UUID,
    tenant_id: str,
    role: UserRole,
) -> str:
    """Create a signed JWT for the given user identity."""
    now = datetime.now(UTC)
    payload: dict[str, object] = {
        "user_id": str(user_id),
        "tenant_id": tenant_id,
        "role": str(role),
        "iat": now,
        "exp": now + timedelta(hours=settings.JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, object]:
    """Decode and validate a JWT. Raises jwt.InvalidTokenError on failure."""
    result = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    return result  # type: ignore[return-value]  # jwt.decode returns dict[str, Any]
```

**mypy note:** `jwt.decode` returns `dict[str, Any]` which mypy --strict will flag. Use `# type: ignore[return-value]` on the return statement. This is acceptable — we own the token creation and the payload structure is known.

### Task 5 — `app/core/security/rate_limiter.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

### Task 6 — `app/main.py` slowapi wiring

Add these imports and lines to `main.py` after creating `app = FastAPI(...)`:

```python
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.security.rate_limiter import limiter

# After app = FastAPI(...):
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

**Order matters:** add the `RateLimitExceeded` handler AFTER the existing exception handlers — slowapi's handler returns a 429 response, not a custom envelope. This is intentional (standard HTTP rate limit response).

### Task 7 — `app/schemas/auth.py`

```python
import uuid

from pydantic import BaseModel, Field


class PinLoginRequest(BaseModel):
    user_id: uuid.UUID
    pin: str = Field(min_length=4, max_length=8)


class LoginResponse(BaseModel):
    message: str
```

**No `TokenResponse` schema** — the JWT goes in the `httpOnly` cookie, never in the response body. This is a non-negotiable security requirement (FR85, FR86).

### Task 8 — `app/api/v1/routes/auth.py` exact implementation

```python
from typing import Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security.jwt import create_access_token
from app.core.security.permissions import UserRole
from app.core.security.pin import verify_pin
from app.core.security.rate_limiter import limiter
from app.db.session import get_db
from app.db.valkey import get_valkey
from app.models.user import TenantUser
from app.schemas.auth import LoginResponse, PinLoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])

_PIN_ROLES = frozenset({
    UserRole.BILLER,
    UserRole.WAITER,
    UserRole.KITCHEN_STAFF,
    UserRole.MANAGER,
})
_COOKIE_MAX_AGE = settings.JWT_EXPIRY_HOURS * 3600


@router.post("/pin", response_model=LoginResponse)
@limiter.limit("5/minute")
async def pin_login(
    request: Request,
    body: PinLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    valkey: Any = Depends(get_valkey),
) -> LoginResponse:
    """Authenticate operational staff with PIN. Sets httpOnly JWT cookie."""
    # Fetch user
    result = await db.execute(
        select(TenantUser).where(TenantUser.id == body.user_id)
    )
    user = result.scalar_one_or_none()

    # Generic 401 for not found / inactive / no PIN set
    if user is None or not user.is_active or user.pin_hash is None:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Invalid credentials"},
        )

    # Reject Admin/Super-Admin — must use Story 2.3 email+TOTP flow
    if user.role not in _PIN_ROLES:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ROLE_NOT_ALLOWED",
                "message": "Use email login for admin accounts",
            },
        )

    # Check account lockout
    lockout_key = f"auth_locked:{user.id}"
    if await valkey.exists(lockout_key):
        raise HTTPException(
            status_code=403,
            detail={"code": "ACCOUNT_LOCKED", "message": "Account locked. Contact admin."},
        )

    # Verify PIN
    attempts_key = f"auth_attempts:{user.id}"
    if not verify_pin(body.pin, user.pin_hash):
        # Increment attempts counter (60s window)
        count = await valkey.incr(attempts_key)
        if count == 1:
            await valkey.expire(attempts_key, 60)
        if count >= 5:
            await valkey.set(lockout_key, "1")  # no TTL — admin must reset
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Invalid credentials"},
        )

    # Success — clear attempts, issue token
    await valkey.delete(attempts_key)
    token = create_access_token(user.id, user.tenant_id, user.role)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.ENVIRONMENT != "development",
        max_age=_COOKIE_MAX_AGE,
        path="/api",
    )
    return LoginResponse(message="Login successful")
```

**`valkey: Any = Depends(get_valkey)`** — `get_valkey` is typed `AsyncGenerator[Any, None]`, so the injected value is `Any`. This is consistent with the existing `valkey.py` pattern established in Story 1.6.

**`@limiter.limit` must have `request: Request` as a parameter** — slowapi inspects the function signature for `Request` to extract the client IP. If `Request` is missing, slowapi raises a `RuntimeError`.

**Generic 401 for all auth failures** — Never distinguish between "user not found" vs "wrong PIN" in the error message (timing attack / enumeration hardening).

### Task 9 — Updated `app/core/dependencies.py`

```python
import uuid
from collections.abc import Awaitable, Callable
from typing import TypedDict

import jwt
from fastapi import Depends, HTTPException, Request

from app.core.security.jwt import decode_access_token
from app.core.security.permissions import UserRole


class CurrentUser(TypedDict):
    """Authenticated user context injected by require_role() into endpoints."""

    user_id: uuid.UUID
    tenant_id: str  # VARCHAR in DB — TenantMixin uses str, not UUID
    role: UserRole


async def get_current_user(request: Request) -> CurrentUser:
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
    return CurrentUser(
        user_id=uuid.UUID(str(payload["user_id"])),
        tenant_id=str(payload["tenant_id"]),
        role=UserRole(str(payload["role"])),
    )


def require_role(
    *allowed_roles: UserRole,
) -> Callable[..., Awaitable[CurrentUser]]:
    """FastAPI dependency factory for role-based access control.

    Usage:
        @router.get("/protected")
        async def endpoint(
            user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
        ) -> ...

    Raises HTTP 401 when no valid session cookie exists.
    Raises HTTP 403 when the authenticated role is not in allowed_roles.
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

**Existing test compatibility:** All 6 tests in `test_require_role.py` use `dependency_overrides[get_current_user]`. When overridden, `get_current_user` is never called → no cookie lookup happens → tests still pass exactly as before.

**Existing 401 test (`test_require_role_returns_401_without_auth`):** No override → `get_current_user` runs → no `access_token` cookie → raises HTTP 401. Test still passes ✓

### Task 10 — Test implementations

#### `tests/unit/test_pin.py`

```python
from app.core.security.pin import hash_pin, verify_pin


def test_hash_pin_returns_bcrypt_string() -> None:
    result = hash_pin("1234")
    assert result.startswith("$2b$")


def test_verify_pin_correct_returns_true() -> None:
    pin_hash = hash_pin("5678")
    assert verify_pin("5678", pin_hash) is True


def test_verify_pin_wrong_returns_false() -> None:
    pin_hash = hash_pin("1234")
    assert verify_pin("9999", pin_hash) is False


def test_hash_pin_different_salts() -> None:
    h1 = hash_pin("1234")
    h2 = hash_pin("1234")
    assert h1 != h2  # bcrypt salts are unique per call
```

#### `tests/unit/test_jwt.py`

```python
import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import jwt
import pytest

from app.core.security.jwt import create_access_token, decode_access_token
from app.core.security.permissions import UserRole


def _make_token(role: UserRole = UserRole.BILLER) -> str:
    return create_access_token(
        user_id=uuid.uuid4(),
        tenant_id="tenant-abc",
        role=role,
    )


def test_create_access_token_returns_string() -> None:
    token = _make_token()
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_access_token_returns_correct_payload() -> None:
    uid = uuid.uuid4()
    token = create_access_token(uid, "tenant-xyz", UserRole.MANAGER)
    payload = decode_access_token(token)
    assert payload["user_id"] == str(uid)
    assert payload["tenant_id"] == "tenant-xyz"
    assert payload["role"] == "manager"
    assert "iat" in payload
    assert "exp" in payload


def test_expired_token_raises_invalid_token_error() -> None:
    uid = uuid.uuid4()
    # Create token with past expiry by patching datetime.now
    past = datetime.now(UTC) - timedelta(hours=5)
    with patch("app.core.security.jwt.datetime") as mock_dt:
        mock_dt.now.return_value = past
        token = create_access_token(uid, "t", UserRole.BILLER)
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)


def test_tampered_token_raises_invalid_token_error() -> None:
    token = _make_token()
    tampered = token[:-4] + "XXXX"
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(tampered)
```

### Project Structure Notes

**Files to CREATE:**
- `backend/app/core/security/jwt.py` — token creation + validation
- `backend/app/core/security/pin.py` — bcrypt PIN hashing + verification
- `backend/app/core/security/rate_limiter.py` — slowapi `Limiter` instance
- `backend/app/schemas/auth.py` — `PinLoginRequest`, `LoginResponse`
- `backend/tests/unit/test_pin.py` — 4 unit tests
- `backend/tests/unit/test_jwt.py` — 4 unit tests

**Files to MODIFY:**
- `backend/pyproject.toml` — add `bcrypt>=4.1`, `PyJWT>=2.8` to `[project].dependencies`
- `backend/app/core/config.py` — add `JWT_ALGORITHM: str = "HS256"`, `JWT_EXPIRY_HOURS: int = 4`
- `backend/app/core/dependencies.py` — replace `get_current_user` stub with real JWT cookie extraction
- `backend/app/api/v1/routes/auth.py` — implement `POST /api/v1/auth/pin`
- `backend/app/main.py` — wire `limiter` and `RateLimitExceeded` handler

**No new migration needed** — `tenant_users.pin_hash` (nullable VARCHAR) was created in migration 0001. Migration chain stays: `0001 → 0002 → 0003`.

**No frontend changes** — UI for staff selection + PIN entry is Story 2.2's frontend counterpart (deferred to a later frontend story in Epic 2).

**Known architectural constraints:**
- `tenant_id` in `TenantMixin` is `str` (VARCHAR), not UUID — consistent with `CurrentUser.tenant_id: str`
- `get_valkey` yields `Any` — use `Any` type annotation in route parameter
- `asyncio_mode = "auto"` in pyproject.toml — all async tests discovered automatically, `@pytest.mark.anyio` is optional but conventional
- Line length 88 chars (ruff E501)
- Import sorting: `from collections.abc import` NOT `from typing import` (ruff UP006/UP035)

### Architecture Compliance

1. **httpOnly cookie only** — JWT NEVER in response body or localStorage (FR85, FR86)
2. **slowapi rate limiting** — `slowapi` was already in `pyproject.toml` — no new dep just setup
3. **Account lockout in Valkey** — no TTL, admin resets by deleting `auth_locked:{user_id}` key
4. **Generic 401 for all credential failures** — prevents username enumeration
5. **ADMIN/SUPER_ADMIN rejection** — those roles use Story 2.3's flow; mixing is forbidden
6. **Server-side enforcement** — `get_current_user` validates JWT on every request; client UI is decorative
7. **`secure=False` in dev** — cookie works over HTTP on localhost; `secure=True` in staging/prod

### Gotchas & Known Pitfalls

**`@limiter.limit` requires `request: Request` as a named parameter** — slowapi inspects the function signature. If `Request` is not present, it raises `RuntimeError: "No request found in handler"`. Always include it even if you don't use it directly.

**`jwt` package vs `jose` package** — `import jwt` works only after installing `PyJWT`. If `python-jose` is accidentally installed, `import jwt` will import the wrong module with a different API. Verify with `python -c "import jwt; print(jwt.__version__)"` inside Docker.

**bcrypt `rounds=12`** — each additional round doubles hash time. 12 rounds ≈ 100ms which is acceptable for PIN auth. Do NOT lower to 10 or less (too fast for brute force).

**Cookie `path="/api"`** — restricts cookie to API paths only; the frontend Vite dev server at `/` never receives it. This is correct — the browser sends the cookie only when making API requests.

**`_COOKIE_MAX_AGE` vs JWT `exp`** — both are set to 4 hours but are independent: `max_age` tells the browser when to discard the cookie; `exp` in the JWT payload is validated by `decode_access_token`. Both must match. If they diverge, the cookie may outlive or underrun the JWT.

**slowapi + `@limiter.limit` + async routes** — slowapi works with async FastAPI routes. The decorator pattern `@router.post("/pin") @limiter.limit("5/minute")` requires that the `limiter` is attached to `app.state` BEFORE any request is handled. The `app.state.limiter = limiter` line in `main.py` satisfies this.

**ruff `UP006`** — use `dict[str, object]` not `Dict[str, object]` (lowercase generics, Python 3.9+). All type hints in new files must use lowercase generics.

### Previous Story Intelligence (Story 2.1)

- `enum.StrEnum` (not `str, enum.Enum`) — ruff UP042
- `from collections.abc import Callable, Awaitable` (not `typing`) — ruff UP006/UP035
- `from sqlalchemy import Enum as SAEnum` must be on its own import line — ruff I001
- Rebuild backend image with `docker compose build backend` after changing `pyproject.toml`
- Tests use `@pytest.mark.anyio` for async tests (anyio compat)
- Isolated mini `FastAPI()` for route-specific tests — avoids production app mutation
- `create_type=False` on SAEnum is critical — not relevant for this story but worth remembering
- `tenant_id: str` everywhere — TenantMixin uses VARCHAR, not UUID

### References

- Story ACs: [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 2 > Story 2.2]
- PIN auth flow: [Source: `_bmad-output/planning-artifacts/architecture.md` — Authentication & Security section]
- Security module structure: [Source: `_bmad-output/planning-artifacts/architecture.md` — `app/core/security/`]
- Rate limiting: [Source: `_bmad-output/planning-artifacts/architecture.md` — FastAPI Security Layer: "slowapi — 5 attempts/min"]
- Token storage (httpOnly cookies): [Source: `_bmad-output/planning-artifacts/architecture.md` — Auth Decision Table]
- `get_valkey` pattern: [Source: `backend/app/db/valkey.py`]
- Existing `get_db` pattern: [Source: `backend/app/db/session.py`]
- `TenantUser` model with `pin_hash` field: [Source: `backend/app/models/user.py`]
- `CurrentUser` TypedDict: [Source: `backend/app/core/dependencies.py`]
- `DataResponse`/`ErrorResponse` envelope: [Source: `backend/app/schemas/common.py`]
- FR84 (rate limiting), FR85 (httpOnly), FR86 (encrypted at rest), FR37 (4h expiry): `_bmad-output/planning-artifacts/prd.md`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- mypy: `# type: ignore[return-value]` and `# type: ignore[no-any-return]` both rejected as unused — PyJWT 2.12.1 types `jwt.decode` as `dict[str, Any]` which mypy accepts for `dict[str, object]` directly. Fix: assign to typed variable `decoded: dict[str, object] = jwt.decode(...)`
- mypy: `_rate_limit_exceeded_handler` type signature (`Callable[[Request, RateLimitExceeded], Response]`) doesn't match FastAPI's `add_exception_handler` expected type — used `# type: ignore[arg-type]` on that line (slowapi limitation, not fixable without upstream change)
- New test files not picked up by pytest — image was stale (built before files were written). Fix: `docker compose build backend` after writing test files

### Completion Notes List

- `bcrypt 5.0.0` + `PyJWT 2.12.1` installed and confirmed
- `jwt.decode` returns `dict[str, Any]` — assigned to `decoded: dict[str, object]` to satisfy mypy --strict without type: ignore
- All 6 existing `require_role` tests pass unchanged — `dependency_overrides[get_current_user]` bypasses the real implementation entirely
- Account lockout key `auth_locked:{user_id}` has no TTL (admin must delete manually to unlock)
- Cookie: `path="/api"` restricts to API requests only; `secure=False` in `development` environment

### File List

**Created:**
- `backend/app/core/security/pin.py`
- `backend/app/core/security/jwt.py`
- `backend/app/core/security/rate_limiter.py`
- `backend/app/schemas/auth.py`
- `backend/tests/unit/test_pin.py`
- `backend/tests/unit/test_jwt.py`

**Modified:**
- `backend/pyproject.toml` — added `bcrypt>=4.1`, `PyJWT>=2.8`
- `backend/app/core/config.py` — added `JWT_ALGORITHM`, `JWT_EXPIRY_HOURS`
- `backend/app/core/dependencies.py` — replaced `get_current_user` stub with real JWT cookie extraction
- `backend/app/api/v1/routes/auth.py` — implemented `POST /api/v1/auth/pin`
- `backend/app/main.py` — wired slowapi `limiter` + `RateLimitExceeded` handler
