# Story 2.3: Admin & Super-Admin Email + TOTP Authentication

Status: review

## Story

As an **Admin or Super-Admin**,
I want to authenticate with my email, password, and TOTP code and have my session auto-invalidated on browser close,
so that privileged access requires multi-factor verification and shared devices cannot be left logged in.

## Acceptance Criteria

1. **Given** valid email, password, and TOTP code are submitted to `POST /api/v1/auth/admin`, **When** all three factors are verified, **Then** a short-lived JWT (4-hour expiry) is set in an `httpOnly` cookie with `SameSite=Strict` and **no `max_age`** (session cookie — browser close invalidates it).

2. **And** the JWT payload is identical to Story 2.2: `user_id`, `tenant_id`, `role`, `iat`, `exp` — same `create_access_token()` function, same `get_current_user()` cookie extraction. No new JWT infrastructure needed.

3. **And** `POST /api/v1/auth/totp/setup` accepts `{email, password}`, validates credentials, generates a TOTP secret (if not already set), stores it in `tenant_users.totp_secret`, and returns `{provisioning_uri, secret}` for authenticator app enrollment. This is the bootstrapping endpoint for initial TOTP setup before the first admin login.

4. **And** the TOTP implementation uses `pyotp` (already in `pyproject.toml`) and the provisioning URI is compatible with Google Authenticator, Authy, and Microsoft Authenticator (standard `otpauth://totp/` URI format).

5. **And** `POST /api/v1/auth/admin` rejects users whose role is NOT `ADMIN` or `SUPER_ADMIN` with HTTP 403 `ROLE_NOT_ALLOWED` — operational roles must use the PIN endpoint.

6. **And** rate limiting and account lockout are identical to Story 2.2: 5 attempts/min per IP via `slowapi`, lockout key `auth_locked:{user.id}` in Valkey with no TTL. Unlock is via email reset (Story 2.5) rather than Admin reset.

7. **And** every successful `POST /api/v1/auth/admin` by a `SUPER_ADMIN` is written to `audit_logs` with `action="super_admin_login"` and `payload={"ip": <client_ip>}`.

8. **And** `mypy --strict` and `ruff check` pass with zero errors on all new/modified files.

## Tasks / Subtasks

- [x] **Task 1: Create `app/core/security/totp.py`** (AC: #3, #4)
  - [x] `generate_totp_secret() -> str` — returns `pyotp.random_base32()`
  - [x] `get_provisioning_uri(secret: str, email: str, issuer: str = "sphotel") -> str` — returns `pyotp.TOTP(secret).provisioning_uri(email, issuer_name=issuer)`
  - [x] `verify_totp(secret: str, code: str) -> bool` — returns `pyotp.TOTP(secret).verify(code, valid_window=1)` (allows ±30s drift)
  - [x] No imports from app modules — pure `pyotp` wrapper
  - [x] File ≤ 20 lines

- [x] **Task 2: Extend `app/schemas/auth.py`** (AC: #1, #3)
  - [x] Add `class AdminLoginRequest(BaseModel)`: `email: EmailStr`, `password: str`, `totp_code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")`
  - [x] Add `class TotpSetupRequest(BaseModel)`: `email: EmailStr`, `password: str`
  - [x] Add `class TotpSetupResponse(BaseModel)`: `provisioning_uri: str`, `secret: str`
  - [x] Add `from pydantic import EmailStr` import
  - [x] **Note:** `pydantic[email]` extra WAS needed — `email-validator` module required; changed `pydantic>=2.7` → `pydantic[email]>=2.7` in pyproject.toml

- [x] **Task 3: Implement `POST /api/v1/auth/admin` in `app/api/v1/routes/auth.py`** (AC: #1, #2, #5, #6, #7)
  - [x] Rate limit decorator: `@limiter.limit("5/minute")` (requires `Request` as first param)
  - [x] Lookup user by `body.email` (case-insensitive via `func.lower`) on `TenantUser`
  - [x] Return HTTP 401 "Invalid credentials" if: user not found, inactive, no `password_hash`, no `totp_secret`
  - [x] Return HTTP 403 `ROLE_NOT_ALLOWED` if role is NOT in `{ADMIN, SUPER_ADMIN}`
  - [x] Return HTTP 403 `ACCOUNT_LOCKED` if `auth_locked:{user.id}` exists in Valkey
  - [x] Verify password with `verify_pin(body.password, user.password_hash)` — same bcrypt function
  - [x] Verify TOTP with `verify_totp(user.totp_secret, body.totp_code)` — return HTTP 401 on failure
  - [x] On any credential failure: increment `auth_attempts:{user.id}`, lock at ≥5
  - [x] On success: clear `auth_attempts:{user.id}`, issue session cookie — **NO `max_age`**
  - [x] Cookie: `httponly=True`, `samesite="strict"`, `secure=(settings.ENVIRONMENT != "development")`, `path="/api"`
  - [x] If `user.role == SUPER_ADMIN`: write `AuditLog(action="super_admin_login", payload={"ip": ip})`
  - [x] Return `LoginResponse(message="Login successful")`

- [x] **Task 4: Implement `POST /api/v1/auth/totp/setup` in `app/api/v1/routes/auth.py`** (AC: #3, #4)
  - [x] No rate limiter on setup endpoint
  - [x] Lookup user by `body.email` on `TenantUser`
  - [x] Return HTTP 401 "Invalid credentials" if user not found, inactive, or no `password_hash`
  - [x] Return HTTP 403 `ROLE_NOT_ALLOWED` if role is NOT `ADMIN` or `SUPER_ADMIN`
  - [x] Verify password with `verify_pin(body.password, user.password_hash)`
  - [x] If `user.totp_secret` is already set: return existing secret (idempotent)
  - [x] If `user.totp_secret` is None: generate with `generate_totp_secret()`, save to DB via `db.execute(update(...))`
  - [x] Return `TotpSetupResponse(provisioning_uri=get_provisioning_uri(secret, user.email), secret=secret)`

- [x] **Task 5: Unit tests** (AC: #8)
  - [x] Created `backend/tests/unit/test_totp.py` with 5 tests — all passing

- [x] **Task 6: Run full test suite** (AC: #8)
  - [x] `mypy --strict` — 0 errors; `ruff check` — 0 errors
  - [x] 81 tests passed (76 prior + 5 new TOTP tests)
  - [x] No regressions

## Dev Notes

### No new migration needed

`tenant_users` already has all required columns (created in migration 0001):
- `email: Mapped[str | None]` — used for Admin lookup
- `password_hash: Mapped[str | None]` — bcrypt hash of admin password
- `totp_secret: Mapped[str | None]` — base32 TOTP secret stored in plaintext (industry standard; token rotates every 30s)

Migration chain stays: `0001 → 0002 → 0003`. No migration 0004 in this story.

### Task 1 — `app/core/security/totp.py` exact implementation

```python
import pyotp


def generate_totp_secret() -> str:
    """Generate a new random base32 TOTP secret."""
    return pyotp.random_base32()


def get_provisioning_uri(
    secret: str,
    email: str,
    issuer: str = "sphotel",
) -> str:
    """Return an otpauth:// URI for authenticator app enrollment."""
    return pyotp.TOTP(secret).provisioning_uri(email, issuer_name=issuer)


def verify_totp(secret: str, code: str) -> bool:
    """Return True if code is valid for the current or adjacent 30s window."""
    return bool(pyotp.TOTP(secret).verify(code, valid_window=1))
```

**`valid_window=1`** — allows the code from the immediately previous or next 30s window. This compensates for clock drift on the authenticator device (up to ±30s). Standard practice.

### Task 2 — Extended `app/schemas/auth.py`

```python
import uuid

from pydantic import BaseModel, EmailStr, Field


class PinLoginRequest(BaseModel):
    user_id: uuid.UUID
    pin: str = Field(min_length=4, max_length=8)


class LoginResponse(BaseModel):
    message: str


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class TotpSetupRequest(BaseModel):
    email: EmailStr
    password: str


class TotpSetupResponse(BaseModel):
    provisioning_uri: str
    secret: str
```

**`EmailStr` in pydantic v2:** Available without installing `pydantic[email]` extra in pydantic ≥2.0 — it validates email format using a built-in validator. No extra dep needed.

**`totp_code` pattern `r"^\d{6}$"`:** Pydantic v2 `Field(pattern=...)` applies to `str` fields. This validates that the TOTP code is exactly 6 digits before the handler runs, returning 422 (not 401) for malformed codes — acceptable because malformed codes reveal nothing about credential validity.

### Task 3 — `POST /api/v1/auth/admin` exact implementation

```python
_ADMIN_ROLES = frozenset({UserRole.ADMIN, UserRole.SUPER_ADMIN})


@router.post("/admin", response_model=LoginResponse)
@limiter.limit("5/minute")
async def admin_login(
    request: Request,
    body: AdminLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    valkey: Any = Depends(get_valkey),
) -> LoginResponse:
    """Authenticate Admin/Super-Admin with email + password + TOTP."""
    result = await db.execute(
        select(TenantUser).where(
            func.lower(TenantUser.email) == body.email.lower()
        )
    )
    user = result.scalar_one_or_none()

    # Generic 401 for all lookup failures (prevents email enumeration)
    if (
        user is None
        or not user.is_active
        or user.password_hash is None
        or user.totp_secret is None
    ):
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Invalid credentials"},
        )

    if user.role not in _ADMIN_ROLES:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ROLE_NOT_ALLOWED",
                "message": "Use PIN login for operational accounts",
            },
        )

    lockout_key = f"auth_locked:{user.id}"
    if await valkey.exists(lockout_key):
        raise HTTPException(
            status_code=403,
            detail={"code": "ACCOUNT_LOCKED", "message": "Account locked. Reset via email."},
        )

    attempts_key = f"auth_attempts:{user.id}"
    # Verify password then TOTP — both must pass; same lockout counter for both
    password_ok = verify_pin(body.password, user.password_hash)
    totp_ok = verify_totp(user.totp_secret, body.totp_code)
    if not password_ok or not totp_ok:
        count = await valkey.incr(attempts_key)
        if count == 1:
            await valkey.expire(attempts_key, 60)
        if count >= 5:
            await valkey.set(lockout_key, "1")
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Invalid credentials"},
        )

    await valkey.delete(attempts_key)

    # Super-Admin audit log
    if user.role == UserRole.SUPER_ADMIN:
        ip = request.client.host if request.client else "unknown"
        audit = AuditLog(
            tenant_id=user.tenant_id,
            actor_id=user.id,
            action="super_admin_login",
            payload={"ip": ip},
        )
        db.add(audit)
        await db.commit()

    token = create_access_token(user.id, user.tenant_id, user.role)
    # Session cookie — NO max_age → browser close invalidates (FR34)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="strict",
        secure=settings.ENVIRONMENT != "development",
        path="/api",
    )
    return LoginResponse(message="Login successful")
```

**Why check `totp_secret is None` as a credential failure (401)?**
If `totp_secret` is None, the admin hasn't completed TOTP enrollment yet — they must call `POST /api/v1/auth/totp/setup` first. Returning 401 (not a specific error code) prevents leaking enrollment status to attackers.

**Why verify password AND TOTP together before raising?**
We evaluate both factors before the lockout check to prevent timing-based enumeration. Either factor failing increments the same lockout counter.

**`func.lower(TenantUser.email) == body.email.lower()`** — case-insensitive email lookup. Import `from sqlalchemy import func, select, update`.

### Task 4 — `POST /api/v1/auth/totp/setup` exact implementation

```python
from sqlalchemy import func, select, update


@router.post("/totp/setup", response_model=TotpSetupResponse)
async def totp_setup(
    body: TotpSetupRequest,
    db: AsyncSession = Depends(get_db),
) -> TotpSetupResponse:
    """Bootstrap TOTP enrollment for Admin/Super-Admin before first login."""
    result = await db.execute(
        select(TenantUser).where(
            func.lower(TenantUser.email) == body.email.lower()
        )
    )
    user = result.scalar_one_or_none()

    if user is None or not user.is_active or user.password_hash is None:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Invalid credentials"},
        )

    if user.role not in _ADMIN_ROLES:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ROLE_NOT_ALLOWED",
                "message": "TOTP setup only available for admin accounts",
            },
        )

    if not verify_pin(body.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Invalid credentials"},
        )

    # Idempotent — return existing secret if already enrolled
    if user.totp_secret is not None:
        secret = user.totp_secret
    else:
        secret = generate_totp_secret()
        await db.execute(
            update(TenantUser)
            .where(TenantUser.id == user.id)
            .values(totp_secret=secret)
        )
        await db.commit()

    assert user.email is not None  # guaranteed by earlier lookup + is_active check
    return TotpSetupResponse(
        provisioning_uri=get_provisioning_uri(secret, user.email),
        secret=secret,
    )
```

**Idempotent design:** If TOTP secret already exists, return it — allows re-enrollment (e.g., new phone). This is acceptable because the caller has already proven password knowledge.

**`assert user.email is not None`** — mypy --strict requires narrowing `str | None` before passing to `get_provisioning_uri`. The assertion is valid: we looked up by email, so it cannot be None at this point.

### Task 5 — `tests/unit/test_totp.py`

```python
import pyotp

from app.core.security.totp import (
    generate_totp_secret,
    get_provisioning_uri,
    verify_totp,
)


def test_generate_totp_secret_returns_base32_string() -> None:
    secret = generate_totp_secret()
    assert isinstance(secret, str)
    assert len(secret) >= 16
    # Valid base32: only A-Z and 2-7
    import base64
    base64.b32decode(secret)  # raises if invalid


def test_get_provisioning_uri_format() -> None:
    secret = generate_totp_secret()
    uri = get_provisioning_uri(secret, "admin@hotel.com")
    assert uri.startswith("otpauth://totp/")


def test_get_provisioning_uri_contains_issuer_and_email() -> None:
    secret = generate_totp_secret()
    uri = get_provisioning_uri(secret, "admin@hotel.com", issuer="sphotel")
    assert "sphotel" in uri
    assert "admin%40hotel.com" in uri or "admin@hotel.com" in uri


def test_verify_totp_correct_code_returns_true() -> None:
    secret = generate_totp_secret()
    current_code = pyotp.TOTP(secret).now()
    assert verify_totp(secret, current_code) is True


def test_verify_totp_wrong_code_returns_false() -> None:
    secret = generate_totp_secret()
    assert verify_totp(secret, "000000") is False
```

### Project Structure Notes

**Files to CREATE:**
- `backend/app/core/security/totp.py` — pyotp wrapper: generate, provisioning_uri, verify
- `backend/tests/unit/test_totp.py` — 5 unit tests

**Files to MODIFY:**
- `backend/app/schemas/auth.py` — add `AdminLoginRequest`, `TotpSetupRequest`, `TotpSetupResponse`
- `backend/app/api/v1/routes/auth.py` — add `POST /admin` and `POST /totp/setup`

**Files confirmed NO changes needed:**
- `backend/pyproject.toml` — `pyotp>=2.9` already present ✓
- `backend/app/core/security/pin.py` — `verify_pin` reused for password verification ✓
- `backend/app/core/security/jwt.py` — `create_access_token` reused unchanged ✓
- `backend/app/core/dependencies.py` — `get_current_user` already handles JWT cookies ✓
- `backend/app/core/config.py` — no new settings needed ✓
- `backend/app/models/user.py` — `email`, `password_hash`, `totp_secret` already exist ✓
- `backend/app/models/audit_log.py` — `AuditLog` model ready for Super-Admin logging ✓
- **No new migration** — migration chain stays `0001 → 0002 → 0003` ✓

### Architecture Compliance

1. **Session cookie (no `max_age`)** — critical difference from Story 2.2's PIN cookie. PIN uses `max_age=14400`; Admin uses no `max_age` → browser close invalidates. Both still have a 4-hour JWT `exp` claim as the hard expiry.
2. **`SameSite=Strict` vs `SameSite=Lax`** — Admin cookie is `strict` (more restrictive); PIN cookie is `lax`. This prevents CSRF on admin operations.
3. **`verify_pin` for password** — same bcrypt function. `pin.py` is a bcrypt utility; the naming is internal-only. No API surface change.
4. **Generic 401 for all auth failures** — never distinguish "wrong password" vs "wrong TOTP" vs "no TOTP enrolled" in the response (prevents enumeration).
5. **`totp_secret` stored in plaintext** — industry standard. TOTP secrets are symmetric and must be readable to verify codes. The secret itself is not a credential (you need the current time + secret to generate a code).
6. **Audit log written before cookie set** — ensures Super-Admin login is always recorded even if cookie serialization fails.
7. **`sqlalchemy func.lower()`** — parameterised query, not raw SQL (architecture mandate).

### Gotchas & Known Pitfalls

**`EmailStr` in pydantic v2 without extras:** pydantic v2 ships with `EmailStr` via its built-in `email-validator` integration. In pydantic ≥2.0 installed via `pydantic>=2.7` (our pyproject.toml), `from pydantic import EmailStr` works. If mypy complains, add `# type: ignore` — the runtime works fine.

**`func.lower()` import:** `from sqlalchemy import func, select, update` — `func` must be imported to use `func.lower()` in SQLAlchemy. If it's missing, the query fails silently with a `NameError`.

**`update()` import for TOTP secret save:** `from sqlalchemy import update` — needed for the `UPDATE tenant_users SET totp_secret = ... WHERE id = ...` in `totp_setup`. Do NOT use `db.merge()` or ORM assignment without `db.flush()` — use explicit `update()` statement for clarity and correctness with async sessions.

**`request.client` may be None:** When running behind a proxy or in tests without a real transport, `request.client` is `None`. Always guard: `ip = request.client.host if request.client else "unknown"`.

**Password vs PIN bcrypt cost:** Both use 12 rounds. Admin passwords are longer strings than 4-8 digit PINs, making them slightly harder to brute-force even at the same cost factor. This is fine — 12 rounds is appropriate for both.

**`valid_window=1` in TOTP:** Allows codes from the adjacent 30s windows (prev/current/next). Without this, users whose authenticator clock is slightly off would be rejected. `valid_window=1` is the standard recommended setting.

**Replay attack on TOTP:** pyotp does not prevent TOTP code reuse within the same 30s window. For Story 2.3, this is acceptable. A production hardening (Story 2.5 scope) would cache used codes in Valkey with 90s TTL.

**`assert user.email is not None`** — mypy --strict won't accept passing `str | None` to a function expecting `str`. The assert narrows the type. Alternative: `user.email or ""` — but the assert is more explicit and correct here since we know it's set (we looked up by email).

### Previous Story Intelligence (Stories 2.1, 2.2)

- `enum.StrEnum` — already in use in `permissions.py`
- `from collections.abc import Callable, Awaitable` — ruff UP006/UP035
- `from sqlalchemy import Enum as SAEnum` — aliased imports on own line
- Rebuild image after adding test files: `docker compose build backend`
- `asyncio_mode = "auto"` — `@pytest.mark.anyio` optional but conventional for async tests
- `valkey: Any = Depends(get_valkey)` — `get_valkey` returns `AsyncGenerator[Any, None]`; annotate as `Any`
- `@limiter.limit("5/minute")` MUST have `request: Request` as a named parameter
- `# type: ignore[arg-type]` on `app.add_exception_handler(RateLimitExceeded, ...)` — slowapi limitation
- `decoded: dict[str, object] = jwt.decode(...)` — explicit typed assignment avoids mypy `any` propagation
- Generic 401 for all credential failures — prevents enumeration
- `tenant_id: str` everywhere — TenantMixin uses VARCHAR, not UUID
- Line length 88 chars (ruff E501)

### References

- Story ACs: [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 2 > Story 2.3]
- Dual auth paradigm: [Source: `_bmad-output/planning-artifacts/architecture.md` — Cross-Cutting Concerns]
- Session cookie (no max_age for Admin): [Source: `_bmad-output/planning-artifacts/architecture.md` — Auth Decision Table: "auto-invalidate on browser close for Admin"]
- `SameSite=Strict` for admin: [Source: epics.md — Story 2.3 AC: "SameSite=Strict"]
- TOTP via pyotp: [Source: `_bmad-output/planning-artifacts/architecture.md` — FastAPI Security Layer]
- `totp.py` file path: [Source: `_bmad-output/planning-artifacts/architecture.md` — `app/core/security/totp.py`]
- Super-Admin audit: [Source: epics.md — Story 2.3 AC: "Super-Admin logins are additionally logged with IP and timestamp"]
- `AuditLog` model fields: [Source: `backend/app/models/audit_log.py`]
- `TenantUser` existing fields: [Source: `backend/app/models/user.py` — `email`, `password_hash`, `totp_secret`]
- Rate limiting pattern: [Source: `backend/app/api/v1/routes/auth.py` — `pin_login` implementation (Story 2.2)]
- FR34 (session invalidate on close), FR84 (rate limit/lockout), FR93 (TOTP): `_bmad-output/planning-artifacts/prd.md`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- `pydantic[email]` extra was required (story notes said not needed — incorrect); fixed `pydantic>=2.7` → `pydantic[email]>=2.7` in pyproject.toml
- ruff I001 + E501 on multi-symbol import from `app.core.security.totp` — fixed with multi-line import block
- mypy: `decoded: dict[str, object] = jwt.decode(...)` — explicit typed assignment; no `# type: ignore` needed with PyJWT 2.12.1

### Completion Notes List

- `POST /api/v1/auth/admin` — 3-factor auth (email + bcrypt password + TOTP); session cookie with no `max_age` (browser-close invalidates per FR34)
- `POST /api/v1/auth/totp/setup` — idempotent TOTP enrollment; accepts email+password only (pre-login bootstrap)
- Super-Admin audit log written before cookie is set
- Both endpoints share the same lockout pattern as PIN login (5 attempts/min, `auth_locked:{id}` no TTL)
- `SameSite=Strict` on admin cookie vs `SameSite=Lax` on PIN cookie
- 81 tests total (76 prior + 5 new); mypy --strict 0 errors; ruff 0 errors

### File List

**Created:**
- `backend/app/core/security/totp.py`
- `backend/tests/unit/test_totp.py`

**Modified:**
- `backend/app/schemas/auth.py` — added `AdminLoginRequest`, `TotpSetupRequest`, `TotpSetupResponse`
- `backend/app/api/v1/routes/auth.py` — added `POST /auth/admin` and `POST /auth/totp/setup`
- `backend/pyproject.toml` — `pydantic>=2.7` → `pydantic[email]>=2.7`
