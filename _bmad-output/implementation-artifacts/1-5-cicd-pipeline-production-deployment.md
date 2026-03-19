# Story 1.5: CI/CD Pipeline & Production Deployment

Status: review

## Story

As a **developer**,
I want GitHub Actions deploying to Dokploy on Hetzner automatically on every push to `main`, with SSL via Traefik,
so that every merged story is live in production within minutes and the team never manually deploys.

## Acceptance Criteria

1. **Given** a commit is pushed to `main`, **When** the GitHub Actions workflow runs, **Then** backend Docker image is built, tests run (`make test-backend`), and on success the Dokploy webhook triggers a redeploy.

2. **And** frontend is built (`make test-frontend` + `vite build`) and deployed.

3. **And** Traefik automatically provisions and renews a Let's Encrypt TLS certificate for the configured domain.

4. **And** `https://` is the only accessible protocol — HTTP redirects to HTTPS (301).

5. **And** WSS is the only WebSocket protocol — plain WS connections are rejected at the Traefik level (FR88, NFR16).

6. **And** `docker-compose.prod.yml` is separate from dev compose and contains no volume mounts or hot reload config.

7. **And** the CI workflow completes in under 5 minutes for a standard build.

## Tasks / Subtasks

- [x] **Task 1: Create `docker-compose.prod.yml`** (AC: #3, #4, #5, #6)
  - [x] Add `traefik` service: `traefik:v3.1` image, ports `80:80` and `443:443`, ACME Let's Encrypt via TLS challenge, cert storage volume
  - [x] Configure HTTP→HTTPS redirect on port-80 entrypoint (`redirections.entrypoint.to=websecure`, `scheme=https`)
  - [x] Configure `websecure` entrypoint (port 443) with TLS enabled
  - [x] Add `frontend` service: build `context: .`, `dockerfile: frontend/Dockerfile`, `target: production`; Traefik labels for catch-all host routing
  - [x] Add `backend` service override: Traefik labels routing `PathPrefix('/api')` and `PathPrefix('/ws')` to backend:8000
  - [x] No exposed ports on db/valkey/backend/frontend (Traefik routes externally via 80/443 only)
  - [x] No volume mounts to source code, no `--reload` flags, no dev artifacts
  - [x] Mount `traefik_certs` named volume at `/letsencrypt` in Traefik service
  - [x] Mount `/var/run/docker.sock:/var/run/docker.sock:ro` in Traefik service (Docker provider)
  - [x] `providers.docker.exposedbydefault=false` — only services with `traefik.enable=true` label are routed

- [x] **Task 2: Update `docker-compose.yml` — add frontend service** (AC: #2, #6)
  - [x] Add `frontend` service: `build: {context: ., dockerfile: frontend/Dockerfile, target: production}`, `restart: unless-stopped`, `depends_on: [backend]`
  - [x] **Important:** Change frontend build context from `./frontend` to `.` (monorepo root) so Dockerfile can `COPY infra/nginx/nginx.conf` — update `frontend/Dockerfile` `COPY` path accordingly
  - [x] Keep backend build context as `./backend` — no changes needed
  - [x] No Traefik in base compose — Traefik added only in `docker-compose.prod.yml` overlay

- [x] **Task 3: Create `infra/nginx/nginx.conf`** (AC: #2, #4)
  - [x] `listen 80;` — nginx serves HTTP inside container; Traefik handles TLS externally
  - [x] `root /usr/share/nginx/html;` + `index index.html;`
  - [x] SPA routing: `location / { try_files $uri $uri/ /index.html; add_header Cache-Control "no-cache"; }`
  - [x] Immutable asset cache: `location /assets/ { add_header Cache-Control "public, max-age=31536000, immutable"; }`
  - [x] Gzip: `gzip on; gzip_types text/html text/css application/javascript application/json image/svg+xml;`
  - [x] File MUST be ≤100 lines

- [x] **Task 4: Update `frontend/Dockerfile` production stage** (AC: #2)
  - [x] In the `production` stage (nginx:alpine), add: `COPY infra/nginx/nginx.conf /etc/nginx/conf.d/default.conf`
  - [x] **Critical:** The `COPY infra/nginx/nginx.conf` only works if build context is monorepo root (`.`) — ensure docker-compose.yml and docker-compose.prod.yml both use `context: .` for frontend
  - [x] Expose port 80 (documentation, already implicit in nginx:alpine)
  - [x] No changes to `dev`, `deps`, or `builder` stages

- [x] **Task 5: Create `.github/workflows/deploy.yml`** (AC: #1, #2, #7)
  - [x] Trigger: `push` to `main` branch only (NOT pull_request)
  - [x] Job `test-backend`: actions/checkout@v4, setup-python@v5 (python 3.12), pip cache (`~/.cache/pip` keyed on `backend/pyproject.toml`), `pip install -e ".[dev]"`, `make test-backend`
  - [x] Job `test-frontend`: actions/checkout@v4, setup-node@v4 (node 20), pnpm cache (`~/.local/share/pnpm/store` keyed on `frontend/pnpm-lock.yaml`), `corepack enable && corepack prepare pnpm@9 --activate`, `pnpm install --frozen-lockfile`, `make test-frontend`
  - [x] Job `build-images`: actions/checkout@v4, run `docker build --target production ./backend` and `docker build -f frontend/Dockerfile --target production .` — verifies images build cleanly; runs in parallel with test jobs
  - [x] Job `deploy`: `needs: [test-backend, test-frontend, build-images]`; single step: `curl -fsS -X POST "${{ secrets.DOKPLOY_WEBHOOK_URL }}"` — `-f` fails on HTTP error, `-s` suppresses progress
  - [x] All three upstream jobs run in parallel (no `needs` between them) → total wall-clock ≈ max(~2min backend, ~2min frontend, ~3min build) + ~10s deploy ≈ 3-4 min
  - [x] Add pip and pnpm caches with `actions/cache@v4` — required to stay under 5-minute budget

- [x] **Task 6: Complete `infra/dokploy/app.yml`** (AC: #1, #2, #3)
  - [x] Set `appName: sphotel`
  - [x] Set `composeFile: docker-compose.yml`
  - [x] Set `composeOverrideFile: docker-compose.prod.yml` (Dokploy merges both)
  - [x] Document webhook setup instruction as a comment
  - [x] Document required env vars section: `DOMAIN`, `ACME_EMAIL`, `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `VALKEY_URL`, `SECRET_KEY`, `CORS_ORIGINS`, `VITE_API_URL`, `VITE_WS_URL`, `SENTRY_DSN`, `TELEGRAM_BOT_TOKEN`, `R2_*` — all injected via Dokploy dashboard, not committed to repo

- [x] **Task 7: Update `.env.example` and `README.md`** (AC: #1)
  - [x] Add section to `.env.example` (as comment block): `# ── Production / Dokploy ──`, `DOMAIN=yourdomain.com`, `ACME_EMAIL=admin@yourdomain.com`
  - [x] Add section to `.env.example`: `# ── GitHub Secrets (set in repo settings, NOT .env) ──`, `# DOKPLOY_WEBHOOK_URL=https://your-dokploy-instance/webhook/...`
  - [x] Update root `README.md` — add "Production Deployment" section documenting: Dokploy setup, GitHub secrets required, Hetzner VPS requirements, first-deploy checklist

## Dev Notes

### Current State (from Stories 1.1–1.4)

**Already exists — do NOT recreate:**
- `docker-compose.yml` — backend (target: production), db (postgres:16-alpine), valkey (valkey/valkey:8-alpine); **no frontend service yet**; **no Traefik**
- `docker-compose.dev.yml` — hot reload overrides: backend `--reload`, frontend `pnpm dev`, ports 8000/5173/5432/6379 exposed
- `backend/Dockerfile` — multi-stage: `base (python:3.12.9-slim)` → `deps` → `production`; CMD: `uvicorn app.main:app --host 0.0.0.0 --port 8000`; build context `./backend`
- `frontend/Dockerfile` — multi-stage: `base (node:20-alpine)` → `deps` → `dev` → `builder` (pnpm build) → `production (nginx:alpine)`; currently no nginx.conf copied → default nginx config (broken SPA routing)
- `.github/workflows/ci-backend.yml` — runs on ALL pushes/PRs; `pip install -e ".[dev]"` + `make test-backend`; **no deployment step**
- `.github/workflows/ci-frontend.yml` — runs on ALL pushes/PRs; pnpm@9 + `make test-frontend`; **no deployment step**
- `infra/dokploy/app.yml` — stub (2 lines, "full implementation in Story 1.5")
- `infra/backup/backup.sh` — stub ("implement in Story 1.7" — do NOT touch)
- `.env.example` — fully documented vars: DB, Valkey, SECRET_KEY, CORS_ORIGINS, Sentry, Telegram, R2, VITE_API_URL, VITE_WS_URL
- `Makefile` — `make test-backend` → `mypy --strict + ruff + pytest`; `make test-frontend` → `pnpm tsc --noEmit + pnpm lint + pnpm test`

**NOT yet existing — create in this story:**
- `docker-compose.prod.yml`
- `.github/workflows/deploy.yml`
- `infra/nginx/nginx.conf`

### Critical: Traefik v3 Docker Labels (Exact Pattern)

Traefik v3 changed label syntax vs v2. Use this exact pattern:

```yaml
# docker-compose.prod.yml
services:
  traefik:
    image: traefik:v3.1
    command:
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
      - "--entrypoints.web.http.redirections.entrypoint.scheme=https"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=${ACME_EMAIL}"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - traefik_certs:/letsencrypt
      - /var/run/docker.sock:/var/run/docker.sock:ro
    restart: unless-stopped

  backend:
    labels:
      - "traefik.enable=true"
      # REST API routes
      - "traefik.http.routers.backend.rule=Host(`${DOMAIN}`) && PathPrefix(`/api`)"
      - "traefik.http.routers.backend.entrypoints=websecure"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
      - "traefik.http.services.backend.loadbalancer.server.port=8000"
      # WebSocket routes (same backend container, separate Traefik router)
      - "traefik.http.routers.backend-ws.rule=Host(`${DOMAIN}`) && PathPrefix(`/ws`)"
      - "traefik.http.routers.backend-ws.entrypoints=websecure"
      - "traefik.http.routers.backend-ws.tls.certresolver=letsencrypt"
      - "traefik.http.routers.backend-ws.service=backend"

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
      target: production
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`${DOMAIN}`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
      - "traefik.http.services.frontend.loadbalancer.server.port=80"
    restart: unless-stopped

volumes:
  traefik_certs:
```

**WSS enforcement (FR88, NFR16):** The `redirections.entrypoint.scheme=https` on port 80 means ALL traffic — including `ws://` WebSocket upgrade requests — is redirected to HTTPS/WSS via HTTP 301. WebSocket clients receiving a 301 cannot follow it (WS protocol doesn't support redirects), so the connection fails. Port 443 enforces TLS, so only `wss://` works. This satisfies "plain WS connections are rejected at the Traefik level."

### Critical: Frontend Docker Build Context Change

The current `frontend/Dockerfile` production stage has:
```dockerfile
FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
# Missing: nginx.conf copy — causes broken SPA routing (404 on page refresh)
```

After this story, the production stage needs:
```dockerfile
FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY infra/nginx/nginx.conf /etc/nginx/conf.d/default.conf
```

`infra/nginx/nginx.conf` is in the monorepo root's `infra/` directory — **not inside `frontend/`**. The `COPY` will only work if the Docker build context is the **monorepo root** (`.`), not `./frontend`. Update `docker-compose.yml` frontend service accordingly:

```yaml
# In docker-compose.yml (and docker-compose.prod.yml):
frontend:
  build:
    context: .                      # monorepo root, NOT ./frontend
    dockerfile: frontend/Dockerfile  # explicit path from root
    target: production
```

The `dev` stage in `docker-compose.dev.yml` should also be updated to use `context: .` for consistency, but the volume mount `./frontend:/app` still works correctly.

### Critical: GitHub Actions Cache Keys (for <5 min budget)

Without caching, pip install + pytest takes ~3min, pnpm install + tests takes ~3min. With caching, each drops to ~1min.

```yaml
# Backend cache
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('backend/pyproject.toml') }}
    restore-keys: ${{ runner.os }}-pip-

# Frontend cache
- uses: actions/cache@v4
  with:
    path: ~/.local/share/pnpm/store
    key: ${{ runner.os }}-pnpm-${{ hashFiles('frontend/pnpm-lock.yaml') }}
    restore-keys: ${{ runner.os }}-pnpm-
```

### Critical: Dokploy Webhook Trigger

Dokploy generates a webhook URL from its dashboard (Settings → Webhooks or per-app). When called, Dokploy:
1. Pulls latest code from the connected GitHub repo
2. Runs the merged docker-compose command
3. Performs zero-downtime redeploy

Store webhook URL as GitHub repository secret `DOKPLOY_WEBHOOK_URL`. In `deploy.yml`:

```yaml
- name: Trigger Dokploy redeploy
  run: curl -fsS -X POST "${{ secrets.DOKPLOY_WEBHOOK_URL }}"
```

`-f` = fail on HTTP 4xx/5xx (fail the CI step if Dokploy rejects), `-s` = silent (no progress bar), `-S` = show errors even when silent.

### Critical: Existing CI Workflows Must Be Preserved

**Do NOT modify** `.github/workflows/ci-backend.yml` and `.github/workflows/ci-frontend.yml`. They continue running on ALL pushes and PRs for fast feedback. The new `deploy.yml` adds deployment **only on `main` push**.

If you merge the workflows, PRs lose CI feedback. Keep them separate.

### Critical: nginx SPA Routing (React Router v7)

Without `try_files`, React Router client-side routes (e.g., `/billing`, `/admin/staff`) return nginx 404 on page refresh — the server has no file at that path. The nginx.conf MUST have:

```nginx
location / {
    try_files $uri $uri/ /index.html;
    add_header Cache-Control "no-cache";
}
```

Vite produces content-hashed filenames in `/assets/` (e.g., `assets/index-Bz3xD7kQ.js`) — these should be cached immutably:

```nginx
location /assets/ {
    add_header Cache-Control "public, max-age=31536000, immutable";
}
```

`index.html` itself must NOT be cached (it references the hashed asset filenames). The `no-cache` header on `location /` achieves this.

### Architecture Compliance Notes

- **No plain WS (FR88, NFR16):** Traefik port-80 redirect covers this — explicit in AC #5 and verified by Traefik config
- **All env vars from environment (architecture rule #11):** `DOMAIN`, `ACME_EMAIL`, `DOKPLOY_WEBHOOK_URL` — never hardcoded; injected via Dokploy dashboard and GitHub secrets
- **No dev artifacts in production compose (AC #6):** `docker-compose.prod.yml` must not include `--reload`, source volume mounts, or exposed DB/Valkey ports
- **100-line file limit (architecture rule):** `infra/nginx/nginx.conf` and `deploy.yml` must stay ≤100 lines each
- **No cross-feature imports:** This story is pure infrastructure — no frontend feature code

### Previous Story Intelligence (Story 1.4)

From Story 1.4 debug log (relevant to this story):
- `frontend/Dockerfile` production stage currently has **no nginx.conf** — default nginx config does NOT support SPA routing; this is a known gap deferred to Story 1.5
- `vitest.config.ts` is separate from `vite.config.ts` — `make test-frontend` runs vitest config; `pnpm build` uses vite.config.ts (no conflict for this story)
- Frontend build produces `frontend/dist/` — nginx serves from `/usr/share/nginx/html` after `COPY --from=builder /app/dist`
- All 8 tests pass; `make test-frontend` exits 0 — CI workflow can rely on this

### Project Structure Notes

**Files created by this story:**
- `docker-compose.prod.yml` (root)
- `.github/workflows/deploy.yml`
- `infra/nginx/nginx.conf`

**Files modified by this story:**
- `docker-compose.yml` — add frontend service, update frontend context to monorepo root
- `frontend/Dockerfile` — copy nginx.conf in production stage
- `infra/dokploy/app.yml` — full implementation (was stub)
- `.env.example` — add DOMAIN, ACME_EMAIL, GitHub secrets comment section
- `README.md` — add Production Deployment section

**Files NOT touched by this story:**
- `docker-compose.dev.yml` — dev overrides unchanged (optional: update frontend context to `.` for consistency)
- `backend/Dockerfile` — no changes needed
- `.github/workflows/ci-backend.yml` — preserved as-is
- `.github/workflows/ci-frontend.yml` — preserved as-is
- `infra/backup/backup.sh` — stub, implemented in Story 1.7

**No backend application code changes.** This story is pure infrastructure.

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 1, Story 1.5]
- [Source: _bmad-output/planning-artifacts/architecture.md — Infrastructure & Deployment section]
- [Source: _bmad-output/planning-artifacts/architecture.md — All AI Agents MUST rules (11 rules)]
- [Source: _bmad-output/implementation-artifacts/1-4-frontend-module-scaffold-pwa-config-design-system-bootstrap.md — Frontend Dockerfile state, debug log: nginx.conf gap]
- [Source: _bmad-output/implementation-artifacts/1-1-monorepo-scaffold-docker-dev-environment.md — docker-compose.yml scaffold state]
- [Source: docker-compose.yml — current production compose (no frontend, no Traefik)]
- [Source: frontend/Dockerfile — current multi-stage build (production: nginx:alpine, no nginx.conf)]
- [Source: .github/workflows/ci-backend.yml — current CI state]
- [Source: .github/workflows/ci-frontend.yml — current CI state]
- [Source: infra/dokploy/app.yml — stub to be completed]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- **Frontend Dockerfile build context change:** Original `frontend/Dockerfile` used `COPY package.json` and `COPY . .` assuming `context: ./frontend`. Changing context to monorepo root (`.`) required updating to `COPY frontend/package.json` and `COPY frontend/ .` in the deps/builder stages. Also required creating `.dockerignore` to exclude `frontend/node_modules` (prevents COPY of ~100k node_modules files into builder layer).
- **docker-compose.dev.yml update required:** The story spec said "optional" to update dev compose context, but it is actually required since the Dockerfile now expects monorepo root context. Updated `context: ./frontend` → `context: .` with explicit `dockerfile: frontend/Dockerfile`. Volume mount `./frontend:/app` still works correctly.

### Completion Notes List

- ✅ `docker-compose.prod.yml` — Traefik v3.1 with Let's Encrypt TLS challenge; HTTP→HTTPS redirect (port 80 → websecure); frontend/backend services with correct Traefik labels; WSS-only enforced via TLS entrypoint (FR88); no source volume mounts; `traefik_certs` volume persists certs across restarts
- ✅ `docker-compose.yml` — frontend service added; monorepo root context for Docker build
- ✅ `infra/nginx/nginx.conf` — SPA `try_files` fallback; Vite asset immutable cache (1yr); `index.html` no-cache; gzip enabled; 21 lines (well under 100)
- ✅ `frontend/Dockerfile` — all stages updated for monorepo root context; production stage copies nginx.conf; deps/builder stages use `frontend/` prefix paths
- ✅ `.dockerignore` — created at monorepo root; excludes `frontend/node_modules`, Python caches, `.git`, `.env`, `_bmad*` dirs; critical for Docker build performance
- ✅ `docker-compose.dev.yml` — updated frontend build context to `.` (monorepo root) for consistency with Dockerfile
- ✅ `.github/workflows/deploy.yml` — triggers on `main` push only; 3 parallel jobs (test-backend, test-frontend, build-images); deploy job waits for all three; pip/pnpm caches for <5min budget; Dokploy webhook trigger
- ✅ `infra/dokploy/app.yml` — full implementation with appName, composeFile, composeOverrideFile, documented env vars list and setup steps
- ✅ `.env.example` — added DOMAIN, ACME_EMAIL, DOKPLOY_WEBHOOK_URL comment
- ✅ `README.md` — Production Deployment section with Dokploy setup steps, CI/CD explanation, GitHub secrets table
- ✅ Merged compose config validated: `docker compose config` passes with no errors
- ✅ Frontend tests: 8/8 pass (no regressions)
- ✅ All files ≤100 lines: nginx.conf (21), deploy.yml (55), docker-compose.prod.yml (58), Dockerfile (26)

### File List

**Created:**
- `docker-compose.prod.yml`
- `.dockerignore`
- `infra/nginx/nginx.conf`
- `.github/workflows/deploy.yml`

**Modified:**
- `docker-compose.yml` — added frontend service
- `docker-compose.dev.yml` — updated frontend build context to monorepo root
- `frontend/Dockerfile` — monorepo root context paths; nginx.conf copy in production stage
- `infra/dokploy/app.yml` — full implementation (was stub)
- `.env.example` — added DOMAIN, ACME_EMAIL, GitHub secrets comment
- `README.md` — added Production Deployment section
