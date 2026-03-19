# Story 1.7: Base Security Hardening & Observability Setup

Status: review

## Story

As a **platform operator**,
I want security headers, CORS policy, Sentry error tracking, and Uptime Kuma monitoring active from day one,
so that the app is secure by default and any production error is captured immediately.

## Acceptance Criteria

1. **Given** the production app is running, **When** any HTTP response is returned from the backend, **Then** the following headers are present: `Strict-Transport-Security: max-age=31536000; includeSubDomains`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Content-Security-Policy` (restrictive default), `Referrer-Policy: strict-origin-when-cross-origin`.

2. **And** CORS allows only the configured application origin — no wildcard `*` origins permitted. The `CORS_ORIGINS` setting is read from the `CORS_ORIGINS` environment variable (already implemented in Story 1.3/1.4; verify no regression).

3. **And** Sentry SDK is initialized in the backend (Python) using `SENTRY_DSN` from environment variables — unhandled exceptions are captured with `send_default_pii=False`. If `SENTRY_DSN` is empty, Sentry is silently skipped (dev/test environments).

4. **And** Sentry SDK (`@sentry/react`) is initialized in the frontend using `VITE_SENTRY_DSN` from Vite env — if the var is empty, Sentry is silently skipped.

5. **And** Uptime Kuma is running at port 3001 via `infra/docker-compose.monitoring.yml` and configured (via its UI) to monitor `/api/v1/health` every 60 seconds with a Telegram alert on downtime.

6. **And** `infra/backup/backup.sh` is fully implemented: pg_dump → gpg-encrypt → upload to Cloudflare R2 via AWS CLI. Required env vars: `DATABASE_URL`, `R2_BUCKET_NAME`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ENDPOINT_URL`, `GPG_PASSPHRASE`. Script exits non-zero on any failure (`set -e`).

7. **And** all secrets (DB URL, Valkey URL, Sentry DSN, R2 credentials, GPG passphrase) are read exclusively from environment variables — zero hardcoded values in source.

8. **And** `make test-backend` runs `mypy --strict` and `ruff check` as part of the test suite — either failure fails the CI build. (Verify existing Makefile command is sufficient; no changes expected.)

## Tasks / Subtasks

- [x] **Task 1: Create `SecurityHeadersMiddleware` in backend** (AC: #1)
  - [x] Create `backend/app/core/middleware.py`
  - [x] Define `class SecurityHeadersMiddleware(BaseHTTPMiddleware)` using `starlette.middleware.base.BaseHTTPMiddleware`
  - [x] Implement `async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:`
  - [x] Set headers on the response (see Dev Notes for exact values)
  - [x] Import: `from collections.abc import Awaitable, Callable` (required for mypy --strict; do NOT use `typing.Callable`)
  - [x] Keep file ≤ 100 lines

- [x] **Task 2: Initialize Sentry in backend + add SecurityHeadersMiddleware to `main.py`** (AC: #3, #1)
  - [x] Update `backend/app/main.py`
  - [x] Add Sentry init block (guarded by `if settings.SENTRY_DSN:`) before `app = FastAPI(...)` instantiation
  - [x] Use `FastApiIntegration()` and `SqlalchemyIntegration()` from `sentry_sdk.integrations`
  - [x] Add `app.add_middleware(SecurityHeadersMiddleware)` after CORS middleware
  - [x] `sentry-sdk[fastapi]>=2.0` is **already in `pyproject.toml`** — do NOT add it again
  - [x] `SENTRY_DSN: str = ""` is **already in `backend/app/core/config.py`** — do NOT add it again

- [x] **Task 3: Add security headers to nginx serving the frontend** (AC: #1)
  - [x] Update `infra/nginx/nginx.conf`
  - [x] Add a `server`-level block with security response headers (see Dev Notes for header values)
  - [x] Add headers to both the `/assets/` location (no-change to Cache-Control) and the `/` location
  - [x] CSP for the nginx/frontend HTML response must permit `'unsafe-inline'` styles (Tailwind inline) and `wss:` + `https:` in `connect-src` for Sentry and API calls

- [x] **Task 4: Add `@sentry/react` and initialize in frontend** (AC: #4)
  - [x] Add `"@sentry/react": "^8.0"` to `"dependencies"` in `frontend/package.json`
  - [x] Run pnpm install via Docker container with volume mount to update lockfile
  - [x] Update `frontend/src/vite-env.d.ts` to declare `VITE_SENTRY_DSN: string` in `ImportMetaEnv`
  - [x] Update `frontend/src/main.tsx` to conditionally init Sentry (see Dev Notes for exact code)
  - [x] `VITE_SENTRY_DSN=` is **already in `.env`** — no `.env` changes needed
  - [x] Fix `tsconfig.node.json` — add `"skipLibCheck": true` (pre-existing vite-plugin-pwa compatibility issue exposed by lockfile refresh)

- [x] **Task 5: Implement `infra/backup/backup.sh`** (AC: #6)
  - [x] Replace stub in `infra/backup/backup.sh` with full pg_dump → GPG AES256 → R2 upload implementation
  - [x] Update `infra/backup/Dockerfile` to add `gnupg` to apk packages
  - [x] Script uses `set -e` — exits non-zero on any failure
  - [x] All 6 required env vars validated with `: "${VAR:?message}"` at script start
  - [x] Add `GPG_PASSPHRASE=dev-placeholder-CHANGE-IN-PRODUCTION` to `.env`

- [x] **Task 6: Verify Uptime Kuma service definition** (AC: #5)
  - [x] Confirmed `infra/docker-compose.monitoring.yml` has `louislam/uptime-kuma:1` on port 3001 (already present)
  - [x] Created `infra/docs/uptime-kuma-setup.md` operator guide documenting: start command, monitor setup, Telegram notification config

- [x] **Task 7: Write backend unit tests for SecurityHeadersMiddleware** (AC: #1)
  - [x] Create `backend/tests/unit/test_security_middleware.py`
  - [x] Test: `X-Frame-Options: DENY` present
  - [x] Test: `X-Content-Type-Options: nosniff` present
  - [x] Test: `Strict-Transport-Security` with `max-age=31536000; includeSubDomains` present
  - [x] Test: `Content-Security-Policy` header non-empty
  - [x] Test: `Referrer-Policy: strict-origin-when-cross-origin` present
  - [x] Test: no wildcard in `settings.CORS_ORIGINS`
  - [x] All 6 tests pass

- [x] **Task 8: Verify `make test-backend` passes** (AC: #8)
  - [x] `mypy --strict` — 44 source files, 0 errors
  - [x] `ruff check` — all checks passed
  - [x] `pytest` — 48/48 passed (6 new security middleware tests + all pre-existing)
  - [x] Makefile confirmed correct — no changes needed

## Dev Notes

### Task 1 — `backend/app/core/middleware.py` full implementation

```python
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

_CSP = (
    "default-src 'none'; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self';"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach security headers to every API response."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = _CSP
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "0"  # Deprecated; CSP handles this
        return response
```

**Why `from collections.abc import Callable` not `typing.Callable`?**
- `mypy --strict` with Python ≥ 3.12 flags `typing.Callable` as deprecated (`UP006` Ruff rule). Use `collections.abc.Callable`.

**Why `X-XSS-Protection: 0`?**
- Modern browsers don't use the XSS auditor; it can introduce XSS in older MSIE. Explicitly disable it. CSP is the correct defense.

**Why a restrictive CSP on the API (not the frontend HTML)?**
- The backend API rarely returns HTML. This CSP is intentionally strict (`default-src 'none'`) because API JSON responses don't need to load any resources. The frontend HTML served by nginx gets a broader CSP (see Task 3).

### Task 2 — `backend/app/main.py` updated imports and init

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.middleware import SecurityHeadersMiddleware

# ... existing imports ...

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        integrations=[FastApiIntegration(), SqlalchemyIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )

app = FastAPI(
    title="sphotel",
    version=settings.VERSION,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

app.add_middleware(SecurityHeadersMiddleware)  # outermost — runs last on response
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ... rest of app setup unchanged ...
```

**Middleware order in Starlette/FastAPI:**
`add_middleware` builds a stack — the LAST added middleware runs FIRST on request, LAST on response. `SecurityHeadersMiddleware` should be added first so it wraps everything and sets headers on ALL responses including CORS preflight and error pages.

**mypy `--strict` on `sentry_sdk.init`:**
`sentry_sdk` stubs are bundled with the package. `sentry_sdk.init()` accepts `dsn: str | None`. The `if settings.SENTRY_DSN:` guard satisfies the non-empty string check.

### Task 3 — `infra/nginx/nginx.conf` with security headers

Add a `server`-level block of security headers (they apply to all locations unless overridden):

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    # Security headers — apply to all responses from nginx
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header X-XSS-Protection "0" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self' https: wss: ws:; font-src 'self' data:; frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;

    gzip on;
    ...

    location /assets/ {
        add_header Cache-Control "public, max-age=31536000, immutable";
        # Re-declare security headers — nginx location blocks reset add_header inheritance
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "DENY" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        try_files $uri =404;
    }

    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache";
    }
}
```

**IMPORTANT nginx inheritance quirk:** `add_header` directives in a `location` block completely override `server`-level `add_header` directives for that location. The `/assets/` location re-declares the critical security headers. The `/` location intentionally inherits from the server block.

**`'unsafe-inline'` in style-src:** Tailwind CSS in v4 (this project uses `tailwindcss@^4.0`) injects styles via `<style>` tags in some configurations. If the build system ever moves fully to class-based (no inline), this can be tightened. Keep `'unsafe-inline'` for styles as the safe default.

**`wss: ws:` in connect-src:** Required for WebSocket connections in future epics. `wss:` for production (TLS WebSocket), `ws:` for local dev.

**`https:` in connect-src:** Required for Sentry SDK which sends data to `https://sentry.io`.

### Task 4 — `frontend/src/vite-env.d.ts` and `main.tsx`

**`frontend/src/vite-env.d.ts`** — add `ImportMetaEnv` interface:
```typescript
/// <reference types="vite/client" />
/// <reference types="vite-plugin-pwa/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_WS_URL: string
  readonly VITE_SENTRY_DSN: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

**`frontend/src/main.tsx`** — add Sentry init before ReactDOM.createRoot:
```typescript
import './index.css'
import React from 'react'
import ReactDOM from 'react-dom/client'
import * as Sentry from '@sentry/react'
import { App } from './app/App'
import { Providers } from './app/providers'

if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.MODE,
    integrations: [Sentry.browserTracingIntegration()],
    tracesSampleRate: 0.1,
    sendDefaultPii: false,
  })
}

const rootElement = document.getElementById('root')
if (!rootElement) throw new Error('Root element #root not found in index.html')

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <Providers>
      <App />
    </Providers>
  </React.StrictMode>
)
```

**`@sentry/react` v8 notes:**
- Package: `@sentry/react@^8.0` — compatible with React 18
- `browserTracingIntegration()` is the v8 API (replaces `BrowserTracing` class from v7)
- `sendDefaultPii: false` — do not capture user IP or email in error events
- The `if (import.meta.env.VITE_SENTRY_DSN)` guard prevents initialization when DSN is empty string (dev/test)

**pnpm lockfile update method used:**
```bash
docker run --rm -v "$(pwd)/frontend:/app" -w /app -e CI=true node:20-alpine sh -c \
  "corepack enable && corepack prepare pnpm@9 --activate && pnpm install --no-frozen-lockfile"
```
The `--frozen-lockfile` flag in the Dockerfile Deps stage requires a matching lockfile. Use `--no-frozen-lockfile` only when updating the lockfile itself.

**`tsconfig.node.json` `skipLibCheck: true` fix:**
- `vite-plugin-pwa@0.21.x` has service-worker type declarations (`ExtendableEvent`, `Worker`, etc.) that require `lib: ["webworker"]` to compile cleanly.
- The node tsconfig (for vite.config.ts) didn't have `skipLibCheck`, causing errors when `pnpm install` bumped `@types/node` to `20.19.37`.
- Adding `"skipLibCheck": true` to `tsconfig.node.json` is the standard fix and does not weaken the application's type safety.

### Task 5 — `infra/backup/backup.sh` full implementation

```sh
#!/bin/sh
set -e

# Validate required environment variables
: "${DATABASE_URL:?DATABASE_URL is required}"
: "${R2_BUCKET_NAME:?R2_BUCKET_NAME is required}"
: "${R2_ACCESS_KEY_ID:?R2_ACCESS_KEY_ID is required}"
: "${R2_SECRET_ACCESS_KEY:?R2_SECRET_ACCESS_KEY is required}"
: "${R2_ENDPOINT_URL:?R2_ENDPOINT_URL is required}"
: "${GPG_PASSPHRASE:?GPG_PASSPHRASE is required}"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="/tmp/sphotel_${TIMESTAMP}.sql"
ENCRYPTED_FILE="${BACKUP_FILE}.gpg"

echo "[backup] Starting pg_dump at ${TIMESTAMP}"
pg_dump "${DATABASE_URL}" > "${BACKUP_FILE}"
echo "[backup] pg_dump complete ($(wc -c < "${BACKUP_FILE}") bytes)"

echo "[backup] Encrypting with GPG (AES256)"
gpg --batch --yes \
    --passphrase "${GPG_PASSPHRASE}" \
    --symmetric \
    --cipher-algo AES256 \
    --output "${ENCRYPTED_FILE}" \
    "${BACKUP_FILE}"

# Remove plaintext dump immediately after encryption
rm -f "${BACKUP_FILE}"

echo "[backup] Uploading to R2: s3://${R2_BUCKET_NAME}/backups/$(basename "${ENCRYPTED_FILE}")"
AWS_ACCESS_KEY_ID="${R2_ACCESS_KEY_ID}" \
AWS_SECRET_ACCESS_KEY="${R2_SECRET_ACCESS_KEY}" \
aws s3 cp "${ENCRYPTED_FILE}" \
    "s3://${R2_BUCKET_NAME}/backups/$(basename "${ENCRYPTED_FILE}")" \
    --endpoint-url "${R2_ENDPOINT_URL}"

rm -f "${ENCRYPTED_FILE}"
echo "[backup] Done: $(basename "${ENCRYPTED_FILE}")"
```

**`infra/backup/Dockerfile`** — add `gnupg` to apk packages:
```dockerfile
FROM alpine:3.19
RUN apk add --no-cache postgresql16-client aws-cli gnupg
COPY backup.sh /backup.sh
RUN chmod +x /backup.sh
CMD ["/backup.sh"]
```

**Notes on the backup implementation:**
- `set -e` — exit immediately if any command fails; pg_dump error = script failure
- `pg_dump "${DATABASE_URL}"` — full schema + data dump; DATABASE_URL format: `postgresql://user:pass@host:port/dbname` (no `+asyncpg` driver prefix — pg_dump uses libpq directly)
- GPG `--symmetric` uses a passphrase (not public key) — simpler for restore: `gpg --decrypt file.sql.gpg`
- AWS CLI with `--endpoint-url` — Cloudflare R2 is S3-compatible; endpoint is `https://ACCOUNT_ID.r2.cloudflarestorage.com`
- Remove plaintext backup immediately after encryption (security: no unencrypted data on disk)
- Backup naming: `sphotel_20260317_143000.sql.gpg` — timestamp-based, lexicographically sortable
- The Ofelia cron scheduler (future Epic 9 / separate service) will call this script nightly

**`.env` addition needed:**
```
GPG_PASSPHRASE=dev-placeholder-CHANGE-IN-PRODUCTION
```

### Task 7 — Test pattern for SecurityHeadersMiddleware

```python
# backend/tests/unit/test_security_middleware.py
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_security_headers_present() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")

    assert response.headers.get("x-frame-options") == "DENY"
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert "max-age=31536000" in response.headers.get("strict-transport-security", "")
    assert response.headers.get("content-security-policy") is not None
    assert response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"


@pytest.mark.anyio
async def test_no_wildcard_cors() -> None:
    """CORS allow_origins must not contain '*'."""
    from app.core.config import settings
    assert "*" not in settings.CORS_ORIGINS
```

**Test runner:** `docker compose run --rm --no-deps backend pytest tests/unit/test_security_middleware.py`

### Project Structure Notes

**Files CREATED:**
- `backend/app/core/middleware.py` — SecurityHeadersMiddleware
- `backend/tests/unit/test_security_middleware.py` — 6 unit tests
- `infra/docs/uptime-kuma-setup.md` — operator setup guide

**Files MODIFIED:**
- `backend/app/main.py` — Sentry init + SecurityHeadersMiddleware added
- `frontend/src/main.tsx` — Sentry init added
- `frontend/src/vite-env.d.ts` — ImportMetaEnv interface added
- `frontend/package.json` — `@sentry/react: ^8.0` added
- `frontend/pnpm-lock.yaml` — lockfile updated with @sentry/react 8.55.0
- `frontend/tsconfig.node.json` — `"skipLibCheck": true` added (pre-existing compatibility issue)
- `infra/nginx/nginx.conf` — security headers added
- `infra/backup/backup.sh` — stub replaced with full implementation
- `infra/backup/Dockerfile` — `gnupg` package added
- `.env` — `GPG_PASSPHRASE=dev-placeholder-CHANGE-IN-PRODUCTION` added

**Files confirmed NO changes needed:**
- `backend/app/core/config.py` — `SENTRY_DSN: str = ""` already present
- `backend/pyproject.toml` — `sentry-sdk[fastapi]>=2.0` already present
- `Makefile` — `mypy --strict` and `ruff check` already in `test-backend` target
- `infra/docker-compose.monitoring.yml` — Uptime Kuma service already defined

### Architecture Compliance Rules (Mandatory for All Files)

From `_bmad-output/planning-artifacts/architecture.md`:

1. **Money as integer paise** — Not applicable to this story (no financial data)
2. **`DataResponse` envelope** — Not applicable (no new API endpoints)
3. **camelCase JSON** — Not applicable (no new schemas)
4. **`tenant_id` first param** — Not applicable (no new service/repo functions)
5. **TanStack Query for server data** — Not applicable (no new frontend data fetching)
6. **100-line file limit** — `middleware.py` is 33 lines ✅
7. **No raw SQL** — Not applicable
8. **Full type safety** — `mypy --strict` passes with 0 errors ✅
9. **CORS_ORIGINS never `*`** — Verified: `test_no_wildcard_cors` test passes ✅
10. **All secrets from env** — Enforced: all new secrets (`GPG_PASSPHRASE`) are env vars only ✅

### Previous Story Intelligence (from Story 1.6)

**mypy --strict gotchas learned:**
- `redis-py 7.3.0` `Redis` class is NOT generic — cannot use `Redis[str]`; use `Any`
- `json.loads()` returns `Any` causing `no-any-return` — use `cast()` with imported type
- `from collections.abc import Callable, Awaitable` — prefer over `typing.Callable` for Python 3.12+

**Docker-based testing (DO NOT run pip/npm locally):**
```bash
# Run backend tests
docker compose run --rm --no-deps backend pytest tests/unit/test_security_middleware.py -v

# Run full backend suite
docker compose run --rm --no-deps backend make test-backend

# Install frontend packages (lockfile update)
docker run --rm -v "$(pwd)/frontend:/app" -w /app -e CI=true node:20-alpine sh -c \
  "corepack enable && corepack prepare pnpm@9 --activate && pnpm install --no-frozen-lockfile"
```

**Pattern from Story 1.3 for integration tests:**
```python
async with AsyncClient(
    transport=ASGITransport(app=app), base_url="http://test"
) as client:
    response = await client.get("/api/v1/health")
```

### References

- Security headers spec: [Source: `_bmad-output/planning-artifacts/architecture.md` — Security section: "Security headers middleware (CSP, HSTS, X-Frame-Options)"]
- Sentry choice: [Source: `_bmad-output/planning-artifacts/architecture.md` — Deployment table: "Error tracking: Sentry free tier — MVP day one"]
- Uptime Kuma choice: [Source: `_bmad-output/planning-artifacts/architecture.md` — Deployment table: "Uptime monitoring: Uptime Kuma (self-hosted) + Telegram alerts"]
- Backup design: [Source: `_bmad-output/planning-artifacts/architecture.md` — "pg_dump nightly via Ofelia cron → gpg encrypted → Cloudflare R2 (free tier, 10GB) → Telegram confirmation"]
- Backup/monitoring file paths: [Source: `_bmad-output/planning-artifacts/architecture.md` — File Tree: `infra/docker-compose.monitoring.yml`, `infra/backup/backup.sh`]
- Story ACs: [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 1 > Story 1.7]
- `make test-backend` definition: [Source: `Makefile:6-7`]
- Existing config: [Source: `backend/app/core/config.py`] — `SENTRY_DSN`, `CORS_ORIGINS` already defined
- `sentry-sdk` already in deps: [Source: `backend/pyproject.toml:19`]
- CORS already configured (no wildcard): [Source: `backend/app/main.py:21-27`]
- Uptime Kuma service stub: [Source: `infra/docker-compose.monitoring.yml`]
- nginx serving frontend: [Source: `infra/nginx/nginx.conf`, `frontend/Dockerfile:24-27`]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

1. **mypy `type: ignore` unused errors (pre-existing):** Backend Docker image was stale — had old Story 1.6 code with `type: ignore` comments that are no longer needed. Fixed by rebuilding the image (`docker compose build backend`). All 44 files pass mypy --strict cleanly.

2. **`pnpm install --frozen-lockfile` failure:** Adding `@sentry/react` to `package.json` made the lockfile outdated. Used `docker run --rm -v "$(pwd)/frontend:/app" -w /app -e CI=true node:20-alpine sh -c "corepack enable && corepack prepare pnpm@9 --activate && pnpm install --no-frozen-lockfile"` to update the lockfile. `@sentry/react 8.55.0` resolved.

3. **`tsconfig.node.json` missing `skipLibCheck`:** After lockfile refresh, `vite-plugin-pwa` / `workbox` type errors surfaced because `tsconfig.node.json` (which compiles `vite.config.ts`) lacked `skipLibCheck: true`. Added it. This is a pre-existing upstream compatibility issue unrelated to our Sentry changes.

### Completion Notes List

- ✅ `SecurityHeadersMiddleware` created at `backend/app/core/middleware.py` (33 lines, fully typed for mypy --strict)
- ✅ Sentry init added to `backend/app/main.py` guarded by `if settings.SENTRY_DSN:` — no-op in dev/test
- ✅ Security headers added to `infra/nginx/nginx.conf` at server level with `/assets/` location re-declaration workaround for nginx inheritance quirk
- ✅ `@sentry/react 8.55.0` installed; lockfile updated; `frontend/src/main.tsx` init with `browserTracingIntegration()`
- ✅ `infra/backup/backup.sh` fully implemented: pg_dump → GPG AES256 symmetric encrypt → R2 upload via AWS CLI; `set -e` ensures failure propagation
- ✅ `infra/backup/Dockerfile` updated with `gnupg` package
- ✅ `infra/docs/uptime-kuma-setup.md` created documenting one-time UI setup steps
- ✅ Backend: 48/48 tests pass including 6 new security header tests; mypy --strict clean; ruff clean
- ✅ Frontend: 17/17 tests pass; tsc --noEmit clean; eslint clean; Docker build succeeds

### File List

- `backend/app/core/middleware.py` — NEW
- `backend/app/main.py` — MODIFIED
- `backend/tests/unit/test_security_middleware.py` — NEW
- `frontend/package.json` — MODIFIED
- `frontend/pnpm-lock.yaml` — MODIFIED (lockfile update)
- `frontend/src/main.tsx` — MODIFIED
- `frontend/src/vite-env.d.ts` — MODIFIED
- `frontend/tsconfig.node.json` — MODIFIED
- `infra/nginx/nginx.conf` — MODIFIED
- `infra/backup/backup.sh` — MODIFIED
- `infra/backup/Dockerfile` — MODIFIED
- `infra/docs/uptime-kuma-setup.md` — NEW
- `.env` — MODIFIED
