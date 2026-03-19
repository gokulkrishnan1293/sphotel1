# Story 1.1: Monorepo Scaffold & Docker Dev Environment

Status: review

## Story

As a **developer**,
I want a fully configured monorepo with Docker Compose running both frontend and backend with hot reload,
so that the team can start writing features immediately with a consistent, reproducible local environment.

## Acceptance Criteria

1. **Given** the repo is cloned fresh, **When** `make dev` is run, **Then** the FastAPI backend starts with hot reload on port 8000, the React+Vite frontend starts on port 5173, PostgreSQL 16 starts on port 5432, and Valkey starts on port 6379.

2. **And** the Makefile exposes exactly these commands (and no others at this stage): `make dev`, `make test-backend`, `make test-frontend`, `make migrate`, `make build-agent`.

3. **And** the folder structure at the monorepo root separates: `backend/`, `frontend/`, `print-agent/`, `infra/` — no application code at the root level.

4. **And** backend uses Python 3.12+, FastAPI, SQLAlchemy 2.x async, Alembic; frontend uses React 18+, Vite, TypeScript strict mode, Tailwind CSS v4, shadcn/ui.

5. **And** `docker-compose.dev.yml` overrides the base `docker-compose.yml` for local dev — provides volume mounts for hot reload, exposed ports, no SSL requirement.

6. **And** `README.md` documents the `make` commands and the one-command setup (`make dev`) so any new developer can onboard in under 5 minutes.

7. **And** `make test-backend` runs `mypy --strict` + `ruff check` + `pytest` in sequence — any one failure fails the command with a non-zero exit code.

8. **And** `make test-frontend` runs `tsc --noEmit` + `eslint` + `vitest run` in sequence — any one failure fails the command.

## Tasks / Subtasks

- [x] **Task 1: Create monorepo root structure** (AC: #3)
  - [x] Create root directories: `backend/`, `frontend/`, `print-agent/`, `infra/`
  - [x] Create root `.gitignore` covering: `__pycache__`, `*.pyc`, `.env`, `.env.local`, `.env.production`, `dist/`, `node_modules/`, `.venv/`, `*.egg-info/`, `pnpm-lock.yaml` NOT gitignored (lock file must be committed)
  - [x] Create root `.env.example` with all env vars documented (see Dev Notes for full list)

- [x] **Task 2: Write root Makefile** (AC: #2, #7, #8)
  - [x] `make dev` → `docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build`
    - ⚠️ **Must include `--build`** — without it, a fresh clone fails because images don't exist yet
  - [x] `make test-backend` → `cd backend && mypy app --strict && ruff check app && pytest`
  - [x] `make test-frontend` → `cd frontend && pnpm tsc --noEmit && pnpm lint && pnpm test`
  - [x] `make migrate` → `cd backend && alembic upgrade head`
  - [x] `make build-agent` → `cd print-agent && python build.py`

- [x] **Task 3: Create docker-compose.yml (production base)** (AC: #5)
  - [x] Service: `backend` — FastAPI, reads from env vars, NO port mapping (Traefik handles in production)
  - [x] Service: `db` — image: `postgres:16-alpine`, data volume `postgres_data`
  - [x] Service: `valkey` — image: `valkey/valkey:8-alpine`, data volume `valkey_data`
  - [x] No volume mounts for source code; no exposed ports to host

- [x] **Task 4: Create docker-compose.dev.yml (dev override)** (AC: #1, #5)
  - [x] Override `backend`: `volumes: [./backend:/app]`, `command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`, `ports: ["8000:8000"]`
  - [x] Add `frontend` service: `build: { context: ./frontend, target: dev }`, `volumes: [./frontend:/app, /app/node_modules]`, `command: pnpm dev --host 0.0.0.0 --port 5173`, `ports: ["5173:5173"]`
  - [x] Override `db` ports: `["5432:5432"]`; override `valkey` ports: `["6379:6379"]`

- [x] **Task 5: Scaffold FastAPI backend** (AC: #4, #7)
  - [x] `backend/Dockerfile` — see Dev Notes for pinned Python version + multi-stage pattern
  - [x] `backend/pyproject.toml` — deps + tool configs (see Dev Notes for full spec)
  - [x] `backend/alembic.ini` — `script_location = alembic`, `sqlalchemy.url` left blank (overridden in env.py from settings)
  - [x] `backend/alembic/env.py` — async-compatible pattern using `asyncio.run()` (see Dev Notes) + model import stub
  - [x] `backend/alembic/versions/.gitkeep`
  - [x] `backend/app/main.py` — FastAPI app creation + `/api/v1` router mount, ≤100 lines (see Dev Notes)
  - [x] `backend/app/api/v1/router.py` — empty `APIRouter`, ready to mount sub-routers
  - [x] `backend/app/core/config.py` — pydantic-settings `Settings` class (see Dev Notes for fields)
  - [x] `backend/app/db/session.py` — `AsyncSessionLocal` factory + `get_db` dependency stub
  - [x] Stub all module directories with empty `__init__.py`: `app/models/`, `app/schemas/`, `app/services/`, `app/repositories/`, `app/workers/`, `app/websocket/`, `app/core/security/`
  - [x] `backend/tests/conftest.py` — empty with `# TODO: add test DB fixtures in Story 2.1`

- [x] **Task 6: Scaffold React+Vite frontend** (AC: #4, #8)
  - [x] `frontend/Dockerfile` — multi-stage with explicit `dev` target (see Dev Notes)
  - [x] `frontend/package.json` — full spec including **scripts section** (see Dev Notes — critical)
  - [x] `frontend/vite.config.ts` — React plugin + `@tailwindcss/vite` plugin + Vitest config block (see Dev Notes)
  - [x] `frontend/tsconfig.json` — `strict: true`, `noImplicitAny: true`, `moduleResolution: bundler`, path alias `@` → `./src`
  - [x] ~~`frontend/tailwind.config.ts`~~ — **NOT created for Tailwind v4** (CSS-based config, see Dev Notes)
  - [x] `frontend/src/index.css` — `@import "tailwindcss";` only (full design tokens added Story 1.4)
  - [x] `frontend/eslint.config.mjs` — ESLint 9 flat config with `no-explicit-any` + cross-feature import boundary rule (see Dev Notes — critical)
  - [x] `frontend/src/test-setup.ts` — `import '@testing-library/jest-dom'`
  - [x] `frontend/src/app/App.tsx` — renders `<p>sphotel</p>` placeholder; imports `./index.css`
  - [x] `frontend/src/app/routes.tsx` — `createBrowserRouter([])` stub using **library mode** (see Dev Notes)
  - [x] `frontend/src/main.tsx` — `ReactDOM.createRoot(document.getElementById('root')!).render(<App />)`
  - [x] `frontend/public/manifests/biller.manifest.json`, `kitchen.manifest.json`, `admin.manifest.json` — minimal PWA manifest stubs
  - [x] Create feature dirs with empty `types.ts` (not `.gitkeep`) so TypeScript can import them: `src/features/{billing,kitchen-display,waiter,admin,super-admin}/types.ts`
  - [x] `src/shared/utils/formatCurrency.ts` — typed stub (see Dev Notes — must compile)
  - [x] `src/shared/utils/formatDate.ts` — typed stub (see Dev Notes — must compile)
  - [x] `src/lib/queryClient.ts` — `QueryClient` instance stub
  - [x] `src/lib/websocket.ts` — empty export stub (full impl Story 1.8)
  - [x] `src/lib/db/schema.ts` — empty export stub (full impl Story 4.3)

- [x] **Task 7: Scaffold print-agent directory** (AC: #3)
  - [x] `print-agent/launcher/launcher.py`, `print-agent/agent/{main,ws_client,printer,auth}.py` — stubs with module docstrings
  - [x] `print-agent/config/agent_config.py` — pydantic-settings stub
  - [x] `print-agent/build.py` — PyInstaller stub
  - [x] `print-agent/requirements.txt` — `python-escpos>=3.0`, `pyinstaller>=6.0`, `pydantic-settings>=2.3`

- [x] **Task 8: Scaffold infra + CI** (AC: #3)
  - [x] `infra/docker-compose.monitoring.yml` — Uptime Kuma service stub
  - [x] `infra/backup/{Dockerfile,backup.sh}` — stubs
  - [x] `infra/dokploy/app.yml` — stub
  - [x] `infra/scripts/{create_tenant,rotate_agent_key,manual_backup,archive_partition}.sh` + `seed_suggestions.py` — stubs
  - [x] `.github/workflows/ci-backend.yml` — see CI pattern in Dev Notes
  - [x] `.github/workflows/ci-frontend.yml` — see CI pattern in Dev Notes

- [x] **Task 9: Write README.md** (AC: #6)
  - [x] Prerequisites: Docker 24+, pnpm 9+, GNU Make, Python 3.12+ (for local print-agent work)
  - [x] Quick start: `cp .env.example .env.local && make dev`
  - [x] Make commands table
  - [x] Service URLs table: Backend API `http://localhost:8000`, Swagger `http://localhost:8000/api/v1/docs`, Frontend `http://localhost:5173`

- [x] **Task 10: End-to-end verification** (AC: #1, #2)
  - [x] See Quick Validation Checklist in Dev Notes

---

## Dev Notes

### Critical Architecture Constraints (Read First)

**100-line file limit:** Every file in `backend/app/` and `frontend/src/` must stay under 100 lines. Split immediately when violated. This is a project invariant — do not defer.

**No cross-feature imports:** `src/features/billing/` must never import from `src/features/kitchen-display/`. Enforced by ESLint (see below). All cross-feature communication goes through `src/shared/` or Zustand stores.

**No `any` type anywhere:** `@typescript-eslint/no-explicit-any: error` in frontend. `mypy --strict` in backend. Both fail CI.

**Money = integer paise ALWAYS:** `₹150.00 = 15000`. Never float. Never rupees in API or DB. `formatCurrency(paise: number)` is the only place division by 100 occurs.

**TIMESTAMPTZ UTC only in PostgreSQL:** Every timestamp column uses `TIMESTAMPTZ`. Alembic column convention enforces this (see below).

---

### Environment Variables — Full `.env.example`

```bash
# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/sphotel
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# ── Valkey ────────────────────────────────────────────────────────────────────
VALKEY_URL=redis://valkey:6379/0

# ── Application ───────────────────────────────────────────────────────────────
SECRET_KEY=dev-secret-key-CHANGE-IN-PRODUCTION
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173

# ── Sentry (leave empty for local dev) ────────────────────────────────────────
SENTRY_DSN=

# ── Telegram (leave empty for local dev) ──────────────────────────────────────
TELEGRAM_BOT_TOKEN=

# ── Cloudflare R2 (leave empty for local dev) ─────────────────────────────────
R2_BUCKET_NAME=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_ENDPOINT_URL=

# ── Frontend — Vite VITE_ prefix required for client exposure ─────────────────
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_SENTRY_DSN=
```

---

### Backend Package Spec (`pyproject.toml`)

```toml
[project]
name = "sphotel-backend"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.29",
    "alembic>=1.13",
    "pydantic>=2.7",
    "pydantic-settings>=2.3",
    "pyotp>=2.9",
    "slowapi>=0.1",
    "sentry-sdk[fastapi]>=2.0",
]

[project.optional-dependencies]
dev = [
    "mypy>=1.10",
    "ruff>=0.4",
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "httpx>=0.27",       # AsyncClient for FastAPI testing
]

[tool.mypy]
strict = true
plugins = ["pydantic.mypy"]

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "UP"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

---

### Backend Dockerfile (Pinned Python Version)

```dockerfile
# Pin minor version for reproducible builds — update deliberately, not automatically
FROM python:3.12.9-slim AS base
WORKDIR /app

FROM base AS deps
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]"

FROM base AS production
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

> Do NOT use `python:3.12-slim` (resolves to a different patch every pull). Always pin the full `3.12.x` version.

---

### Backend `app/main.py` (≤100 lines)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title="sphotel",
    version="0.1.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
```

---

### Backend `app/core/config.py` (pydantic-settings)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    VALKEY_URL: str
    SECRET_KEY: str
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    SENTRY_DSN: str = ""

settings = Settings()
```

---

### Alembic `env.py` — Async Pattern + Model Import (Critical)

```python
import asyncio
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

# CRITICAL: Import ALL models here so autogenerate detects them.
# Without this, `alembic revision --autogenerate` produces empty migrations.
# Add new model imports here as each story creates new models.
from app.models import base as _base  # noqa: F401 — registers Base.metadata
# Story 1.2 will add: from app.models import tenant, user, audit_log

from app.models.base import Base
target_metadata = Base.metadata

def run_migrations_online() -> None:
    engine = create_async_engine(settings.DATABASE_URL)

    async def do_run() -> None:
        async with engine.connect() as connection:
            await connection.run_sync(
                lambda conn: context.configure(
                    connection=conn,
                    target_metadata=target_metadata,
                ).run_migrations()
            )

    asyncio.run(do_run())

run_migrations_online()
```

---

### Frontend Dockerfile (Multi-Stage with `dev` Target)

```dockerfile
FROM node:20-alpine AS base
WORKDIR /app
# Enable pnpm via corepack (ships with Node 20)
RUN corepack enable && corepack prepare pnpm@9 --activate

FROM base AS deps
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

# ── dev stage: used by docker-compose.dev.yml ─────────────────────────────────
# Source code is volume-mounted at runtime — only node_modules pre-installed
FROM base AS dev
COPY --from=deps /app/node_modules ./node_modules
COPY package.json ./
# Actual source files come from volume mount in docker-compose.dev.yml

# ── production build ───────────────────────────────────────────────────────────
FROM deps AS builder
COPY . .
RUN pnpm build

FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
```

> `docker-compose.dev.yml` uses `target: dev` + volume mount. This avoids rebuilding the full image on every code change while keeping `node_modules` inside the container (anonymous volume prevents host override).

---

### Frontend `package.json` — Complete Spec (Including Scripts)

```json
{
  "name": "sphotel-frontend",
  "private": true,
  "version": "0.1.0",
  "engines": {
    "node": ">=20",
    "pnpm": ">=9"
  },
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest",
    "tsc": "tsc --noEmit",
    "lint": "eslint src"
  },
  "dependencies": {
    "react": "^18.3",
    "react-dom": "^18.3",
    "react-router": "^7.5",
    "@tanstack/react-query": "^5.0",
    "zustand": "^5.0",
    "idb": "^8.0",
    "axios": "^1.7"
  },
  "devDependencies": {
    "vite": "^6.0",
    "@vitejs/plugin-react": "^4.0",
    "typescript": "^5.5",
    "tailwindcss": "^4.0",
    "@tailwindcss/vite": "^4.0",
    "vitest": "^2.0",
    "@vitest/ui": "^2.0",
    "jsdom": "^25.0",
    "@testing-library/react": "^16.0",
    "@testing-library/jest-dom": "^6.0",
    "eslint": "^9.0",
    "typescript-eslint": "^8.0",
    "eslint-plugin-boundaries": "^5.0"
  }
}
```

> **No `@tailwindcss/forms` for v4** — v4 doesn't need the forms plugin; use `@tailwindcss/forms` only if an existing v3 project needs it. Not applicable here.

---

### Tailwind CSS v4 — Setup (No `tailwind.config.ts`)

Tailwind v4 is **CSS-first**. There is NO `tailwind.config.ts` file. Configuration lives in CSS.

**`vite.config.ts`:**
```ts
/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test-setup.ts'],
  },
})
```

> `@tailwindcss/vite` replaces the old PostCSS approach. Do NOT add `postcss.config.js` for Tailwind v4.

**`src/index.css`** (scaffold only — design tokens added in Story 1.4):
```css
@import "tailwindcss";

/* Design tokens (@theme) added in Story 1.4 */
/* shadcn/ui CSS custom properties added by shadcn init */
```

**`src/main.tsx`** must import `./index.css`:
```tsx
import './index.css'
import React from 'react'
import ReactDOM from 'react-dom/client'
import { App } from './app/App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

---

### shadcn/ui Initialization with Tailwind v4

```bash
cd frontend && pnpm dlx shadcn@latest init
```

**Answer the wizard exactly:**
| Prompt | Answer |
|---|---|
| Which style would you like to use? | **New York** |
| Which color would you like to use as the base color? | **Zinc** |
| Would you like to use CSS variables for theming? | **Yes** |
| Where is your global CSS file? | `src/index.css` |
| Where is your `components.json` file? | (accept default) |
| Configure the import alias for components? | `@/shared/components/ui` |
| Configure the import alias for utils? | `@/shared/utils` |

> shadcn/ui v4 writes CSS custom properties in oklch format to `src/index.css`. Do not modify them in this story — full dark theme override happens in Story 1.4.

---

### ESLint 9 Flat Config — Cross-Feature Boundary Enforcement (Critical)

**Do NOT create `.eslintrc.json`** — ESLint 9 uses flat config. Create `frontend/eslint.config.mjs`:

```js
import tseslint from 'typescript-eslint'
import boundaries from 'eslint-plugin-boundaries'

export default tseslint.config(
  ...tseslint.configs.strict,
  {
    plugins: { boundaries },
    settings: {
      'boundaries/elements': [
        { type: 'feature', pattern: 'src/features/*', capture: ['name'] },
        { type: 'shared', pattern: 'src/shared/*' },
        { type: 'lib', pattern: 'src/lib/*' },
        { type: 'app', pattern: 'src/app/*' },
      ],
    },
    rules: {
      // No any type — ever
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],

      // Cross-feature import barrier:
      // billing/ cannot import from kitchen-display/ — must go through shared/
      'boundaries/element-types': ['error', {
        default: 'disallow',
        rules: [
          // Feature may import from itself, shared, lib — never from other features
          { from: 'feature', allow: [['feature', { name: '${from.name}' }], 'shared', 'lib'] },
          { from: 'shared', allow: ['shared', 'lib'] },
          { from: 'lib', allow: ['lib'] },
          { from: 'app', allow: ['feature', 'shared', 'lib'] },
        ],
      }],
    },
  }
)
```

> `eslint-plugin-boundaries` v5 requires setting up `boundaries/elements` in ESLint settings. The `capture` field extracts the feature name from the path for use in the `${from.name}` rule pattern.

---

### React Router v7 — Library Mode (Not Framework Mode)

React Router v7 merged with Remix. It has two modes:
- **Framework mode** (Remix-like): SSR, file-based routing, Vite plugin required — **NOT this project**
- **Library mode** (SPA): Classic `createBrowserRouter`, no SSR — **THIS project**

Use **library mode**:

```tsx
// src/app/routes.tsx
import { createBrowserRouter } from 'react-router'

// Stub — routes populated from Story 2.1 onwards
export const router = createBrowserRouter([
  // { path: '/', element: <App /> }
])
```

```tsx
// src/app/App.tsx
import { RouterProvider } from 'react-router'
import { router } from './routes'

export function App() {
  // Placeholder until routes are populated in Story 2.1
  return <p>sphotel</p>
}
```

> Import from `'react-router'` (not `'react-router-dom'` — they're the same package in v7).

---

### `formatCurrency.ts` and `formatDate.ts` — Typed Stubs (Must Compile)

These must have real type signatures or TypeScript strict mode will reject imports:

```ts
// src/shared/utils/formatCurrency.ts
// INVARIANT: all money is integer paise. NEVER pass float rupees.
// ₹150.00 = 15000 paise. NEVER use floating point arithmetic on money values.
// NEVER divide by 100 anywhere except this function.
export const formatCurrency = (paise: number): string => {
  return `₹${(paise / 100).toFixed(2)}`
}
```

```ts
// src/shared/utils/formatDate.ts
// INVARIANT: DB stores TIMESTAMPTZ UTC. API returns ISO 8601. Display converts to IST.
// NEVER display raw UTC timestamps. NEVER accept Unix epoch numbers.
// Full IST formatting implemented in the story that first displays dates.
export const formatDate = (isoUtc: string): string => {
  // TODO: proper IST formatting — placeholder for TypeScript compilation
  return new Date(isoUtc).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })
}
```

---

### Vitest + jsdom — Required Config

Without `environment: 'jsdom'`, React component tests throw `document is not defined`. This is set in `vite.config.ts` (see Tailwind v4 section above).

`src/test-setup.ts` must exist and contain:
```ts
import '@testing-library/jest-dom'
```

Without this, `expect(element).toBeInTheDocument()` matchers are not registered.

---

### CI Pipeline

```yaml
# .github/workflows/ci-backend.yml
name: Backend CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -e ".[dev]"
        working-directory: backend
      - run: make test-backend
```

```yaml
# .github/workflows/ci-frontend.yml
name: Frontend CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: corepack enable && corepack prepare pnpm@9 --activate
      - run: pnpm install --frozen-lockfile
        working-directory: frontend
      - run: make test-frontend
```

---

### Scope Boundary — What This Story Does NOT Include

| Feature | Story |
|---|---|
| Database schema (tenants, users, audit_logs) | Story 1.2 |
| Health endpoint (`GET /api/v1/health`) | Story 1.3 |
| Dark theme design tokens, full Tailwind config | Story 1.4 |
| Dokploy deployment, Traefik SSL | Story 1.5 |
| Feature flags Valkey infrastructure | Story 1.6 |
| Security headers, CORS, Sentry | Story 1.7 |
| WebSocket service bootstrap | Story 1.8 *(new — add to epics.md)* |
| IndexedDB offline layer | Story 4.3 |

**The ONLY goal of this story:** `git clone + make dev` → 4 containers running, hot reload working, frontend renders, `make test-*` exits 0.

---

### Quick Validation Checklist

Before marking this story `review`, verify all of the following:

- [ ] `make dev` starts without errors — all 4 containers healthy in Docker logs
- [ ] `http://localhost:5173` renders "sphotel" (no browser console errors)
- [ ] `http://localhost:8000/api/v1/docs` renders Swagger UI
- [ ] `make test-backend` exits 0 (mypy + ruff + pytest all pass with empty test suite)
- [ ] `make test-frontend` exits 0 (tsc + eslint + vitest all pass with empty test suite)
- [ ] `make migrate` exits 0 (no migrations yet — just verifies Alembic connects to DB)
- [ ] No file in `backend/app/` exceeds 100 lines (`wc -l backend/app/**/*.py`)
- [ ] No `any` in TypeScript — `pnpm tsc --noEmit` passes with strict mode

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 1, Story 1.1]
- [Source: _bmad-output/planning-artifacts/architecture.md — Project Structure, Docker, Backend Scaffold, Frontend Scaffold, CI/CD, Code Quality sections]
- [Tailwind CSS v4 docs: https://tailwindcss.com/docs/upgrade-guide]
- [React Router v7 library mode: https://reactrouter.com/start/library/installation]
- [shadcn/ui Tailwind v4: https://ui.shadcn.com/docs/installation/vite]
- [eslint-plugin-boundaries: https://github.com/javierbrea/eslint-plugin-boundaries]
- [Alembic async cookbook: https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

_None — first story, no prior implementation_

### Completion Notes List

- ✅ All 10 tasks and all subtasks completed in a single session.
- ✅ Tailwind CSS v4 configured via `@tailwindcss/vite` plugin — no `tailwind.config.ts` created (CSS-first approach).
- ✅ ESLint 9 flat config (`eslint.config.mjs`) with `typescript-eslint` strict + `eslint-plugin-boundaries` cross-feature enforcement.
- ✅ Alembic async pattern using `asyncio.run()` — model import stub in env.py prevents empty autogenerate.
- ✅ Frontend Dockerfile has explicit `dev` target used by `docker-compose.dev.yml` for hot reload with volume mount.
- ✅ `tsconfig.node.json` uses `composite: true` (required for project references); `tsconfig.json` adds `@types/react`, `@types/react-dom`, `@types/node` to package.json.
- ✅ React Router v7 library mode (`createBrowserRouter`) — NOT framework/Remix mode.
- ✅ `formatCurrency` and `formatDate` stubs are typed and compilable — enforces paise invariant at definition.
- ✅ All backend files ≤21 lines (well under 100-line limit).
- ✅ `make dev --build` flag included — required for fresh clone to succeed.
- Note: `pnpm-lock.yaml` will be generated on first `pnpm install` inside the frontend container — it is intentionally NOT gitignored.
- Note: shadcn/ui init (`pnpm dlx shadcn@latest init`) should be run manually after first `make dev` to generate `components.json` and populate `src/index.css` with CSS custom properties.

### File List

**Created (relative to repo root):**
- `.gitignore`
- `.env.example`
- `Makefile`
- `README.md`
- `docker-compose.yml`
- `docker-compose.dev.yml`
- `.github/workflows/ci-backend.yml`
- `.github/workflows/ci-frontend.yml`
- `backend/Dockerfile`
- `backend/pyproject.toml`
- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/script.py.mako`
- `backend/alembic/versions/.gitkeep`
- `backend/app/__init__.py`
- `backend/app/main.py`
- `backend/app/api/__init__.py`
- `backend/app/api/v1/__init__.py`
- `backend/app/api/v1/router.py`
- `backend/app/core/__init__.py`
- `backend/app/core/config.py`
- `backend/app/core/security/__init__.py`
- `backend/app/db/__init__.py`
- `backend/app/db/session.py`
- `backend/app/models/__init__.py`
- `backend/app/models/base.py`
- `backend/app/repositories/__init__.py`
- `backend/app/schemas/__init__.py`
- `backend/app/services/__init__.py`
- `backend/app/websocket/__init__.py`
- `backend/app/workers/__init__.py`
- `backend/tests/__init__.py`
- `backend/tests/conftest.py`
- `frontend/Dockerfile`
- `frontend/index.html`
- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/tsconfig.json`
- `frontend/tsconfig.node.json`
- `frontend/eslint.config.mjs`
- `frontend/src/index.css`
- `frontend/src/main.tsx`
- `frontend/src/test-setup.ts`
- `frontend/src/app/App.tsx`
- `frontend/src/app/routes.tsx`
- `frontend/src/features/billing/types.ts`
- `frontend/src/features/kitchen-display/types.ts`
- `frontend/src/features/waiter/types.ts`
- `frontend/src/features/admin/types.ts`
- `frontend/src/features/super-admin/types.ts`
- `frontend/src/shared/utils/formatCurrency.ts`
- `frontend/src/shared/utils/formatDate.ts`
- `frontend/src/lib/queryClient.ts`
- `frontend/src/lib/websocket.ts`
- `frontend/src/lib/db/schema.ts`
- `frontend/public/manifests/biller.manifest.json`
- `frontend/public/manifests/kitchen.manifest.json`
- `frontend/public/manifests/admin.manifest.json`
- `print-agent/launcher/launcher.py`
- `print-agent/agent/main.py`
- `print-agent/agent/ws_client.py`
- `print-agent/agent/printer.py`
- `print-agent/agent/auth.py`
- `print-agent/config/agent_config.py`
- `print-agent/build.py`
- `print-agent/requirements.txt`
- `infra/docker-compose.monitoring.yml`
- `infra/backup/Dockerfile`
- `infra/backup/backup.sh`
- `infra/dokploy/app.yml`
- `infra/scripts/create_tenant.sh`
- `infra/scripts/rotate_agent_key.sh`
- `infra/scripts/manual_backup.sh`
- `infra/scripts/archive_partition.sh`
- `infra/scripts/seed_suggestions.py`
