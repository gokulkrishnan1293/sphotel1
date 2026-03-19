# Story 2.5: Session Management & Credential Self-Service

Status: review

## Story

As any **authenticated user**,
I want my session to auto-expire after inactivity, and as an Admin I want to manage my own credentials,
so that stale sessions don't remain active and I can maintain my own account security.

## Acceptance Criteria

1. **Given** a session JWT is 4 hours old with no activity, **When** the next request is made with that expired token, **Then** `get_current_user` raises HTTP 401 (JWT `exp` check via PyJWT's `jwt.decode` — no additional code needed). The frontend catches 401 responses, clears the `access_token` cookie client-side, and redirects to the login screen.

2. **And** `POST /api/v1/auth/logout` clears the `access_token` httpOnly cookie AND writes `session_revoked:{user_id}` into Valkey with the token's `iat` as the value and TTL = remaining JWT lifetime — so even if the token was captured, `get_current_user` rejects it. Logout succeeds even with an already-expired or invalid token (idempotent). No authentication required for this endpoint.

3. **And** `GET /api/v1/auth/me` returns the authenticated user's `user_id`, `tenant_id`, `role`, `name`, and `email` — all roles allowed. Used by the frontend to populate the auth store after login and determine routing.

4. **And** `PATCH /api/v1/auth/credentials` allows an authenticated Admin or Super-Admin to change their own `email` and/or `password`. At least one field must be provided. A new email must not already exist in `tenant_users` (case-insensitive, global check). A new password is bcrypt-hashed before storage. All credential changes are written to `audit_logs`.

5. **And** `POST /api/v1/auth/admin-reset/{id}` allows a Super-Admin to reset any Admin's `email` and/or `password` within their tenant. Also deletes `auth_locked:{id}` and `session_revoked:{id}` from Valkey — effectively unlocking and re-enabling the target admin. All resets are written to `audit_logs`.

6. **And** the frontend implements a Zustand auth store (`useAuthStore`) at `src/features/auth/stores/authStore.ts` that holds `currentUser: MeResponse | null`. After a successful PIN or admin login, the store calls `GET /api/v1/auth/me` and sets `currentUser`. On logout, it calls `POST /api/v1/auth/logout`, clears `currentUser`, and redirects to `/login`.

7. **And** `src/app/providers.tsx` is updated to read `tenantId` from `useAuthStore` instead of the current hardcoded `null` — enabling feature flags to load after login.

8. **And** `mypy --strict` and `ruff check` pass with zero errors on all new/modified files.

## Tasks / Subtasks

- [x] **Task 1: Add schemas in `backend/app/schemas/auth.py`** (AC: #3, #4, #5)
  - [x] `MeResponse(BaseModel)` with `ConfigDict(from_attributes=True)`: `user_id: uuid.UUID`, `tenant_id: str`, `name: str`, `role: UserRole`, `email: str | None`, `is_active: bool`
  - [x] `UpdateCredentialsRequest(BaseModel)`: `email: EmailStr | None = None`, `password: str | None = None`; add `@model_validator(mode="after")` that raises `ValueError` if both are None
  - [x] `AdminResetRequest(BaseModel)`: same structure and validator as `UpdateCredentialsRequest`

- [x] **Task 2: Implement `POST /api/v1/auth/logout`** (AC: #2)
  - [x] No auth required (no `require_role` or `get_current_user` dependency)
  - [x] Read `access_token` from request cookies
  - [x] If token present and valid: decode with `decode_access_token`, extract `user_id` and `exp`; set `session_revoked:{user_id}` = `str(payload["iat"])` in Valkey with TTL = `max(1, int(payload["exp"] - time.time()))`
  - [x] If token absent or decode fails: skip Valkey write (already invalid)
  - [x] Always: call `response.delete_cookie(key="access_token", path="/api")`
  - [x] Return `DataResponse(data=MessageResponse(message="Logged out successfully"))`

- [x] **Task 3: Implement `GET /api/v1/auth/me`** (AC: #3)
  - [x] Require any authenticated user via `Depends(get_current_user)` (all roles)
  - [x] Load `TenantUser` from DB by `current_user["user_id"]`; raise 404 if missing
  - [x] Return `DataResponse[MeResponse]`

- [x] **Task 4: Implement `PATCH /api/v1/auth/credentials`** (AC: #4)
  - [x] `require_role(ADMIN, SUPER_ADMIN)`
  - [x] If `body.email` provided: check `select(TenantUser).where(func.lower(TenantUser.email) == body.email.lower(), TenantUser.id != current_user["user_id"])` — raise 409 `EMAIL_TAKEN` if found
  - [x] If `body.password` provided: hash with `hash_pin(body.password)` (same bcrypt utility)
  - [x] `db.execute(update(TenantUser).where(id == current_user["user_id"]).values(**updates))`
  - [x] Write `AuditLog(action="credentials_update", actor_id=current_user["user_id"], payload={"changed": list_of_changed_fields})`
  - [x] Return `DataResponse[MeResponse]` with refreshed user

- [x] **Task 5: Implement `POST /api/v1/auth/admin-reset/{id}`** (AC: #5)
  - [x] `require_role(SUPER_ADMIN)` only
  - [x] Load target from DB: `TenantUser.id == target_id AND TenantUser.tenant_id == current_user["tenant_id"]`; 404 if not found
  - [x] Target must have `role == ADMIN` — raise 403 `ROLE_NOT_ALLOWED` if attempting to reset SUPER_ADMIN
  - [x] Apply same email/password update logic as Task 4 (for target user)
  - [x] Delete `auth_locked:{target_id}` and `session_revoked:{target_id}` from Valkey (unlock/re-enable)
  - [x] Write `AuditLog(action="admin_credentials_reset", actor_id=current_user["user_id"], target_id=target_id, payload={"changed": list_of_changed_fields})`
  - [x] Return `DataResponse[MeResponse]` of target user

- [x] **Task 6: Frontend auth store and API client** (AC: #6, #7)
  - [x] Create `frontend/src/features/auth/api/auth.ts` — API client for `/auth/logout`, `/auth/me`, `/auth/credentials`
  - [x] Create `frontend/src/features/auth/stores/authStore.ts` — Zustand store with `currentUser: MeResponse | null`, `setCurrentUser(user)`, `clearCurrentUser()`
  - [x] Create `frontend/src/features/auth/hooks/useAuth.ts` — `useMe()` query hook (TanStack Query) + `useLogout()` mutation hook
  - [x] Update `frontend/src/app/providers.tsx` — read `tenantId` from `useAuthStore((s) => s.currentUser?.tenant_id ?? null)` instead of hardcoded `null`

- [x] **Task 7: Tests** (AC: #8)
  - [x] `backend/tests/unit/test_auth_schemas.py` — `UpdateCredentialsRequest` validator (both-None rejected, either-one accepted)
  - [x] `backend/tests/unit/test_logout.py` — mock Valkey; test cookie cleared, `session_revoked` set, expired/missing token handled gracefully
  - [x] `backend/tests/integration/routes/test_auth_logout_me.py` — integration tests for logout and me endpoints
  - [x] Run: `docker compose build backend && docker compose run --rm --no-deps backend sh -c "cd /app && mypy app --strict && ruff check app && pytest"`
  - [x] All 102 prior tests still pass (124 total now — 22 new tests added)

## Dev Notes

### No new migration needed

All fields already exist on `TenantUser`:
- `email: Mapped[str | None]` ✓
- `password_hash: Mapped[str | None]` ✓
- `is_active: Mapped[bool]` ✓
- `name: Mapped[str]` ✓

`tenant_users.preferences` JSONB does NOT exist yet — Story 2.6 adds it. Do NOT reference `preferences` in this story.

Migration chain stays: `0001 → 0002 → 0003`. No new migration.

### Task 1 — Exact `app/schemas/auth.py` additions

```python
from pydantic import model_validator

class MeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    tenant_id: str
    name: str
    role: UserRole
    email: str | None
    is_active: bool


class UpdateCredentialsRequest(BaseModel):
    email: EmailStr | None = None
    password: str | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "UpdateCredentialsRequest":
        if self.email is None and self.password is None:
            raise ValueError("At least one of email or password must be provided")
        return self


class AdminResetRequest(BaseModel):
    email: EmailStr | None = None
    password: str | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "AdminResetRequest":
        if self.email is None and self.password is None:
            raise ValueError("At least one of email or password must be provided")
        return self
```

**`model_config = ConfigDict(from_attributes=True)` in `MeResponse`** — enables `MeResponse.model_validate(db_user)`. Add `from pydantic import ConfigDict` to `auth.py` imports.

**`model_validator(mode="after")`** — runs after all field validators. Returns `self`. mypy strict: must annotate return type as the class name in quotes (forward reference).

### Task 2 — `POST /api/v1/auth/logout` exact implementation

```python
import time

@router.post("/logout", response_model=DataResponse[MessageResponse])
async def logout(
    request: Request,
    response: Response,
    valkey: Any = Depends(get_valkey),
) -> DataResponse[MessageResponse]:
    """Invalidate session in Valkey and clear httpOnly cookie."""
    token = request.cookies.get("access_token")
    if token:
        try:
            payload = decode_access_token(token)
            user_id_str = str(payload["user_id"])
            exp = float(str(payload.get("exp", 0)))
            iat = float(str(payload.get("iat", 0)))
            remaining_ttl = max(1, int(exp - time.time()))
            await valkey.set(
                f"session_revoked:{user_id_str}", str(iat), ex=remaining_ttl
            )
        except jwt.InvalidTokenError:
            pass  # Token already invalid — just clear the cookie
    response.delete_cookie(key="access_token", path="/api")
    return DataResponse(data=MessageResponse(message="Logged out successfully"))
```

**No auth guard on logout** — this is intentional. Forcing auth on logout means a user with an expired token can't log out cleanly. The OWASP recommendation is to accept and process logout even with invalid tokens.

**`response.delete_cookie(key="access_token", path="/api")`** — The `path="/api"` must match the `path="/api"` used when setting the cookie. Without matching path, the cookie won't be deleted.

**`session_revoked` TTL = remaining lifetime** — After the token expires anyway (JWT `exp`), the Valkey key auto-cleans. Setting `str(iat)` as the value allows `get_current_user` to reject the token via its existing `float(revoked_at) >= token_iat` check.

**Import `DataResponse` and `MessageResponse`** — add `from app.schemas.common import DataResponse, MessageResponse` to `auth.py` imports.

### Task 3 — `GET /api/v1/auth/me`

```python
@router.get("/me", response_model=DataResponse[MeResponse])
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[MeResponse]:
    """Return authenticated user's profile. All roles allowed."""
    result = await db.execute(
        select(TenantUser).where(TenantUser.id == current_user["user_id"])
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "User not found"},
        )
    return DataResponse(data=MeResponse.model_validate(user))
```

**Use `Depends(get_current_user)` directly, not `require_role(...)`** — `/me` should work for all roles without listing them explicitly. `get_current_user` already validates the JWT and revocation status.

**`TenantUser.id` is a UUID, `current_user["user_id"]` is also UUID** — direct comparison works with SQLAlchemy.

### Task 4 — `PATCH /api/v1/auth/credentials`

```python
@router.patch("/credentials", response_model=DataResponse[MeResponse])
async def update_credentials(
    body: UpdateCredentialsRequest,
    current_user: CurrentUser = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[MeResponse]:
    """Admin/Super-Admin self-service credential update."""
    updates: dict[str, object] = {}

    if body.email is not None:
        # Global uniqueness check (email used for cross-tenant admin lookup)
        dupe = await db.execute(
            select(TenantUser).where(
                func.lower(TenantUser.email) == body.email.lower(),
                TenantUser.id != current_user["user_id"],
            )
        )
        if dupe.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=409,
                detail={"code": "EMAIL_TAKEN", "message": "Email already in use"},
            )
        updates["email"] = body.email.lower()

    if body.password is not None:
        updates["password_hash"] = hash_pin(body.password)

    await db.execute(
        update(TenantUser)
        .where(TenantUser.id == current_user["user_id"])
        .values(**updates)
    )
    db.add(AuditLog(
        tenant_id=current_user["tenant_id"],
        actor_id=current_user["user_id"],
        action="credentials_update",
        payload={"changed": list(updates.keys())},
    ))
    await db.commit()

    # Re-fetch to return current state
    result = await db.execute(
        select(TenantUser).where(TenantUser.id == current_user["user_id"])
    )
    user = result.scalar_one()
    return DataResponse(data=MeResponse.model_validate(user))
```

**`updates["email"] = body.email.lower()`** — store emails lowercase for consistency with login lookup (`func.lower(TenantUser.email) == body.email.lower()`).

**`list(updates.keys())`** — audit payload records which fields changed (e.g., `["email"]` or `["password_hash"]` or both). Never log the actual values.

**`dict[str, object]`** — mypy strict requires typed dict, not `dict[str, Any]`. `object` is the correct upper bound here.

### Task 5 — `POST /api/v1/auth/admin-reset/{id}`

```python
@router.post(
    "/admin-reset/{target_id}",
    response_model=DataResponse[MeResponse],
)
async def admin_reset_credentials(
    target_id: uuid.UUID,
    body: AdminResetRequest,
    current_user: CurrentUser = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
    valkey: Any = Depends(get_valkey),
) -> DataResponse[MeResponse]:
    """Super-Admin reset of any Admin's credentials + account unlock."""
    result = await db.execute(
        select(TenantUser).where(
            TenantUser.id == target_id,
            TenantUser.tenant_id == current_user["tenant_id"],
        )
    )
    target = result.scalar_one_or_none()
    if target is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "Admin not found"},
        )
    if target.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ROLE_NOT_ALLOWED",
                "message": "Can only reset credentials for Admin accounts",
            },
        )

    updates: dict[str, object] = {}
    if body.email is not None:
        dupe = await db.execute(
            select(TenantUser).where(
                func.lower(TenantUser.email) == body.email.lower(),
                TenantUser.id != target_id,
            )
        )
        if dupe.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=409,
                detail={"code": "EMAIL_TAKEN", "message": "Email already in use"},
            )
        updates["email"] = body.email.lower()

    if body.password is not None:
        updates["password_hash"] = hash_pin(body.password)

    await db.execute(
        update(TenantUser).where(TenantUser.id == target_id).values(**updates)
    )

    # Unlock: remove lockout and session revocation keys
    await valkey.delete(f"auth_locked:{target_id}")
    await valkey.delete(f"session_revoked:{target_id}")

    db.add(AuditLog(
        tenant_id=current_user["tenant_id"],
        actor_id=current_user["user_id"],
        action="admin_credentials_reset",
        target_id=target_id,
        payload={"changed": list(updates.keys())},
    ))
    await db.commit()

    result2 = await db.execute(
        select(TenantUser).where(TenantUser.id == target_id)
    )
    user = result2.scalar_one()
    return DataResponse(data=MeResponse.model_validate(user))
```

**`target.role != UserRole.ADMIN`** — explicitly reject non-Admin targets. Super-Admin cannot reset another Super-Admin, and cannot reset operational staff via this endpoint (use Story 2.4's PIN reset for staff).

**`await valkey.delete(f"auth_locked:{target_id}")` and `await valkey.delete(f"session_revoked:{target_id}")`** — these keys may not exist; `DELETE` is a no-op if key doesn't exist.

**Route path: `/admin-reset/{target_id}`** — `target_id` not `{id}` to avoid mypy ambiguity with multiple UUID path params.

### Task 6 — Frontend auth store and API client

**`frontend/src/features/auth/api/auth.ts`:**
```typescript
import { apiClient } from '../../../lib/api'
import type { UserRole } from './staff'

export interface MeResponse {
  user_id: string
  tenant_id: string
  name: string
  role: UserRole
  email: string | null
  is_active: boolean
}

export interface UpdateCredentialsPayload {
  email?: string
  password?: string
}

export const authApi = {
  me: (): Promise<MeResponse> =>
    apiClient.get<MeResponse>('/api/v1/auth/me').then((r) => r.data),

  logout: (): Promise<{ message: string }> =>
    apiClient
      .post<{ message: string }>('/api/v1/auth/logout')
      .then((r) => r.data),

  updateCredentials: (payload: UpdateCredentialsPayload): Promise<MeResponse> =>
    apiClient
      .patch<MeResponse>('/api/v1/auth/credentials', payload)
      .then((r) => r.data),
}
```

**`frontend/src/features/auth/stores/authStore.ts`:**
```typescript
import { create } from 'zustand'
import type { MeResponse } from '../api/auth'

interface AuthState {
  currentUser: MeResponse | null
  setCurrentUser: (user: MeResponse) => void
  clearCurrentUser: () => void
}

export const useAuthStore = create<AuthState>()((set) => ({
  currentUser: null,
  setCurrentUser: (user) => set({ currentUser: user }),
  clearCurrentUser: () => set({ currentUser: null }),
}))
```

**`frontend/src/app/providers.tsx` update** — replace `const tenantId: string | null = null` with:
```typescript
import { useAuthStore } from '@/features/auth/stores/authStore'
// inside Providers:
const tenantId = useAuthStore((s) => s.currentUser?.tenant_id ?? null)
```

**`frontend/src/features/auth/hooks/useAuth.ts`:**
```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { authApi } from '../api/auth'
import { useAuthStore } from '../stores/authStore'

export function useMe() {
  const setCurrentUser = useAuthStore((s) => s.setCurrentUser)
  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      const user = await authApi.me()
      setCurrentUser(user)
      return user
    },
    retry: false,   // Don't retry on 401 — means logged out
    staleTime: 5 * 60 * 1000, // 5 min — user profile rarely changes
  })
}

export function useLogout() {
  const clearCurrentUser = useAuthStore((s) => s.clearCurrentUser)
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      clearCurrentUser()
      queryClient.clear()
      window.location.href = '/login'
    },
  })
}
```

### Project Structure Notes

**Files to CREATE:**
- `backend/tests/unit/test_auth_schemas.py`
- `backend/tests/unit/test_logout.py`
- `backend/tests/integration/routes/test_auth_logout_me.py`
- `frontend/src/features/auth/api/auth.ts`
- `frontend/src/features/auth/stores/authStore.ts`
- `frontend/src/features/auth/hooks/useAuth.ts`

**Files to MODIFY:**
- `backend/app/schemas/auth.py` — add `MeResponse`, `UpdateCredentialsRequest`, `AdminResetRequest`
- `backend/app/api/v1/routes/auth.py` — add 4 new endpoints
- `frontend/src/app/providers.tsx` — wire `tenantId` from auth store

**Files confirmed NO changes needed:**
- `backend/app/models/user.py` — all columns already exist ✓
- `backend/app/core/dependencies.py` — `get_current_user` already handles Valkey revocation ✓
- `backend/app/core/security/pin.py` — `hash_pin()` reused for password hashing ✓
- `backend/app/models/audit_log.py` — no changes needed ✓
- **No new migration** — chain stays `0001 → 0002 → 0003` ✓

### Architecture Compliance

1. **Logout idempotent** — `response.delete_cookie()` always runs regardless of token validity. No auth gate on logout.
2. **`response.delete_cookie(path="/api")`** — must match the `path="/api"` used when cookies were set in Stories 2.2 and 2.3. A mismatch silently fails.
3. **Email stored lowercase** — `body.email.lower()` before storage to match `func.lower()` lookup in admin login.
4. **`dict[str, object]` for updates** — mypy strict: use `object` as value type for mixed-type update dicts. Never use `Any`.
5. **Audit payload never includes credential values** — only `{"changed": ["email"]}` or `{"changed": ["password_hash"]}`.
6. **`DataResponse[T]` envelope** — all 4 new endpoints use the standard `{data: T, error: null}` envelope.
7. **`require_role()` for credential endpoints** — only Admin/Super-Admin can modify credentials; use existing dependency.
8. **Tenant scoping for admin-reset** — target admin must be in `current_user["tenant_id"]`. Super-Admin manages their own tenant.

### Gotchas & Known Pitfalls

**`response.delete_cookie` and cookie path:** The cookie was set with `path="/api"`. To delete it, `delete_cookie(key="access_token", path="/api")` MUST be called. Without `path="/api"`, the browser won't clear the cookie — the old cookie remains and the user stays "logged in".

**`model_validator(mode="after")` return type for mypy strict:** Must return `Self` or the class in quotes:
```python
@model_validator(mode="after")
def at_least_one_field(self) -> "UpdateCredentialsRequest":
```
Using `Self` from `typing_extensions` is cleaner but the quoted string form works for mypy.

**`result.scalar_one()` vs `scalar_one_or_none()`:** After an `update(TenantUser).where(TenantUser.id == ...)`, the ORM object `target` is stale. Re-fetch with a fresh `select` query. Use `scalar_one()` (not `scalar_one_or_none()`) since we know the user exists (we just updated them).

**`uuid.UUID` path parameter:** FastAPI automatically validates and converts `{target_id}` to `uuid.UUID`. Type hint `target_id: uuid.UUID` in the handler signature.

**`dict[str, object]` SQLAlchemy `**updates`:** `update(...).values(**updates)` with `dict[str, object]` — mypy may complain about `**kwargs`. Add `# type: ignore[arg-type]` only if needed after testing.

**`valkey.delete()` returns int (count of deleted keys):** No error if keys don't exist. Return value can be ignored.

**Frontend: `window.location.href = '/login'`** — hard navigation clears all React state. This is intentional for logout (ensures clean slate). If a SPA soft-redirect is preferred, use `useNavigate()` from react-router.

**Frontend: `useAuthStore` import path in `providers.tsx`:** Use `@/features/auth/stores/authStore` if `@` alias is configured, or `../../features/auth/stores/authStore` relative path. Check `tsconfig.json` / `vite.config.ts` for alias config.

**`useQuery({ retry: false })` on `/me`:** The `retry: false` prevents TanStack Query from retrying on 401 (logged out). Without this, a logged-out user would see 3 failed requests to `/me` before the error state appears.

**`queryClient.clear()` on logout** — clears all cached query data (staff list, feature flags, etc.) to prevent stale data from the previous user's session showing briefly when the next user logs in on the same device.

### Previous Story Intelligence (Stories 2.2, 2.3, 2.4)

- **`hash_pin()` handles passwords too** — same bcrypt, 12 rounds. `pin.py` is a bcrypt utility; naming is internal-only.
- **`valkey: Any = Depends(get_valkey)`** — always annotate as `Any`
- **`session_revoked:{user_id}` pattern** — established in Story 2.4; logout reuses it with `str(iat)` as value
- **`func.lower()` + `.lower()` for email comparison** — imports `from sqlalchemy import func, select, update`
- **`db.flush()` before audit** — only needed when new row's server-generated ID is required in audit; for updates, flush is not needed
- **`DataResponse[T]` envelope** — all staff and future endpoints use it; auth login endpoints (2.2/2.3) don't wrap responses but new auth endpoints in this story SHOULD use `DataResponse` for consistency with the `apiClient` interceptor
- **Docker rebuild required**: after adding test files → `docker compose build backend`
- **Line length 88 chars** — watch `func.lower(TenantUser.email) == body.email.lower(), TenantUser.id != current_user["user_id"]` constructs

### References

- Story ACs: [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 2 > Story 2.5]
- FR37 (session expiry), FR90 (credential self-service), FR84 (lockout): [Source: `_bmad-output/planning-artifacts/prd.md`]
- `session_revoked` Valkey pattern: [Source: `backend/app/core/dependencies.py` — Story 2.4]
- `hash_pin()` for passwords: [Source: `backend/app/core/security/pin.py`]
- `AuditLog` model: [Source: `backend/app/models/audit_log.py`]
- `TenantUser` columns: [Source: `backend/app/models/user.py`]
- `DataResponse` / `MessageResponse` envelope: [Source: `backend/app/schemas/common.py`]
- Cookie path `/api` (set in Stories 2.2/2.3): [Source: `backend/app/api/v1/routes/auth.py`]
- `apiClient` with `withCredentials: true`: [Source: `frontend/src/lib/api.ts`]
- `useFeatureFlagStore` tenantId TODO: [Source: `frontend/src/app/providers.tsx` line 55]
- Architecture security patterns: [Source: `_bmad-output/planning-artifacts/architecture.md`]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6 (2026-03-18)

### Debug Log References

- **`validation_exception_handler` crash on model_validator**: Pydantic v2 puts the raw `ValueError` object in error `ctx` dict when a `@model_validator` raises. `json.dumps(exc.errors())` then crashes because `ValueError` is not JSON-serializable. Fixed in `app/core/exceptions.py` by using `json.loads(json.dumps(exc.errors(), default=str))` to safely stringify non-serializable ctx values.

### Completion Notes List

- **No new migration needed**: All fields (`email`, `password_hash`, `is_active`, `name`) already exist on `TenantUser` from Story 2.2/2.3. Migration chain stays `0001 → 0002 → 0003`.
- **Logout is unauthenticated by design**: OWASP recommends accepting logout with expired/invalid tokens. Cookie always cleared; Valkey write skipped if token is invalid.
- **`dict[str, object]` for SQLAlchemy updates**: mypy strict accepted this without `# type: ignore` — the earlier story notes suggested it might complain, but it did not.
- **`response.delete_cookie(path="/api")`**: Must match the set path from Stories 2.2/2.3 exactly. Cookie remains if path differs.
- **22 new tests added** (10 unit: auth schemas + logout; 8 integration: logout + me + credentials; 4 unit: logout unit): 124 total passing.
- **`exceptions.py` bugfix**: The `validation_exception_handler` had a latent bug with model validators — fixed as part of making Task 7 tests pass.

### File List

**Backend — Modified:**
- `backend/app/schemas/auth.py` — added `MeResponse`, `UpdateCredentialsRequest`, `AdminResetRequest`
- `backend/app/api/v1/routes/auth.py` — added `logout`, `get_me`, `update_credentials`, `admin_reset_credentials` endpoints
- `backend/app/core/exceptions.py` — fixed `validation_exception_handler` to handle non-JSON-serializable `ValueError` in Pydantic model_validator ctx

**Backend — Created:**
- `backend/tests/unit/test_auth_schemas.py` — 10 unit tests for new schemas
- `backend/tests/unit/test_logout.py` — 4 unit tests for logout endpoint
- `backend/tests/integration/routes/test_auth_logout_me.py` — 8 integration tests for logout, /me, credentials endpoints

**Frontend — Modified:**
- `frontend/src/app/providers.tsx` — wired `tenantId` from `useAuthStore` instead of hardcoded `null`

**Frontend — Created:**
- `frontend/src/features/auth/api/auth.ts` — API client for `me`, `logout`, `updateCredentials`
- `frontend/src/features/auth/stores/authStore.ts` — Zustand auth store with `currentUser: MeResponse | null`
- `frontend/src/features/auth/hooks/useAuth.ts` — `useMe()` and `useLogout()` hooks

### Change Log

- 2026-03-18: Story 2.5 implemented — session logout, GET /me, credential self-service, admin credential reset, frontend auth store wired. 124/124 tests passing.
