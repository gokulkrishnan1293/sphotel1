---
stepsCompleted: ['step-01-init', 'step-02-context', 'step-03-starter', 'step-04-decisions', 'step-05-patterns', 'step-06-structure', 'step-07-validation', 'step-08-complete']
lastStep: 8
status: 'complete'
completedAt: '2026-03-13'
inputDocuments: ['_bmad-output/planning-artifacts/prd.md']
workflowType: 'architecture'
project_name: 'sphotel'
user_name: 'Gokul'
date: '2026-03-12'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
95 FRs across 13 categories. The billing engine (FR1–FR13, FR61–FR63, FR69, FR79) is the performance-critical core — command palette with < 100ms response, multi-tab bill management, F-key switching, and the unified Bill = KOT state machine. Kitchen management (FR14–FR18) requires real-time delta-only updates. Payment and cash management (FR19–FR23, FR76, FR77, FR82) require fintech-grade immutability with no post-close modifications without audit trail. Offline resilience (FR54–FR56, FR66) demands a full IndexedDB-backed sync architecture with server-side sequential number assignment on reconciliation.

**Non-Functional Requirements:**
- Performance: < 10ms active bill queries (hot layer), < 3s menu/KOT sync, < 100ms command palette, < 1.5s FCP, < 500ms offline activation
- Security: TLS/WSS everywhere, TOTP for Admin+, PIN for operational roles, server-side role enforcement, tenant isolation at DB query level, encrypted at rest, immutable audit logs
- Reliability: Zero data loss, IndexedDB offline mode, 30-second crash snapshots, print queue survives agent restart, 99.5% monthly uptime target
- Scalability: Stateless app layer, dedicated real-time service, hot/archive split, suggestion engine in isolated datastore, 100+ tenant architecture

**Scale & Complexity:**

- Primary domain: Full-stack real-time PWA with offline-first architecture
- Complexity level: High / Enterprise-class
- Estimated major architectural components: 12
  (Billing Engine, Real-time Service, Print Tunnel Service, Sync/Reconciliation Engine,
  Suggestion Engine, Auth Service, Notification Service, Analytics Service,
  Admin Panel API, Tenant Management, Hot DB, Archive DB)

### Technical Constraints & Dependencies

- Bill numbers: Server-assigned sequential integers; client uses provisional IDs offline
- No customer-facing display: Out of scope for all phases
- No PCI-DSS: Payment method and amount logged only; no payment processing
- GST: Calculated at report time on totals, not per-bill at creation
- Print agent: Outbound WSS from agent to cloud; cloud never initiates connection
- Suggestion engine: Read-only separate datastore; must not impact billing DB performance
- Tenant isolation: Enforced at DB query level from day one — no exceptions
- Archive retention: Minimum 7 years for GST compliance (configurable)
- Concurrent users per tenant: Designed for up to 20 initially, 100+ tenants target

### Cross-Cutting Concerns Identified

1. **Multi-tenancy** — `tenant_id` scoping on every DB entity, every API endpoint, every WebSocket channel, every report. Architectural decision on isolation strategy (row-level vs schema-per-tenant) shapes all subsequent DB design.

2. **Real-time WebSocket infrastructure** — Single WSS connection per client multiplexing multiple event types. Requires a dedicated stateful real-time service (not embedded in API server) to enable horizontal scaling.

3. **Audit immutability** — All financial records are append-only. Voids create new records; they never modify existing ones. Archive layer is write-once. This is a structural constraint on ORM choice, migration strategy, and DB schema.

4. **Offline-first sync reconciliation** — Client bills have provisional local IDs; server assigns canonical sequential numbers on sync. Conflict resolution favors server state. This is the most complex correctness problem in the system.

5. **Role-based auth with dual paradigm** — PIN-based for operational roles (Biller, Waiter, Kitchen, Manager); credential + TOTP for Admin/Super-Admin. Server-side enforcement mandatory; client checks are UI only.

6. **Hot/archive data split** — Two physical data stores. Query routing must be transparent to the application layer. Migration of data from hot to archive is a scheduled background process.

7. **Async Telegram delivery** — Event bus feeds Telegram alerts. Retries on failure; no alert dropped silently. Financial alerts (void, cash, discrepancy) must be at-least-once delivered.

8. **Suggestion engine isolation** — Separate service, separate datastore. Consumes billing events asynchronously (via event queue, not direct DB reads). Never blocks billing operations.

## Technology Stack & Starter Template

### Primary Technology Domain

Full-stack real-time PWA — React SPA frontend, Python backend, PostgreSQL primary database.

### Selected Stack

| Layer | Choice |
|---|---|
| **Frontend** | React + Vite (SPA, no SSR — internal tool, no SEO) |
| **Backend** | FastAPI (Python) — ML/AI ready, async-native |
| **ORM** | SQLAlchemy (async) + Alembic (migrations) |
| **Primary Database** | PostgreSQL 16 (RLS + range partitioning) |
| **Cache / Suggestion Store** | Valkey (open-source Redis fork, BSD license) |
| **Deployment** | Dokploy (self-hosted PaaS) on Hetzner VPS |
| **Containerisation** | Docker + Docker Compose |
| **Reverse Proxy / SSL** | Traefik (via Dokploy, automatic Let's Encrypt) |

### Rationale

- **FastAPI** chosen for native Python ML ecosystem alignment — Phase 3 AI features require no stack change
- **Valkey** over Redis — BSD license, fully open source, drop-in API compatible
- **Vite** over Next.js — pure SPA, no SSR needed, lighter and faster for keyboard-first internal tooling
- **SQLAlchemy** over SQLModel — complex PostgreSQL features (RLS, partitioning, per-tenant sequences) require full ORM control
- **Hetzner + Dokploy** — fully open-source self-hosted stack, zero licensing cost, ~€13/month for sphotel as tenant #1
- **All components open-source** — no vendor licensing costs at any scale

### Security Layer

**FastAPI:**
- httpOnly cookies for JWT tokens (not localStorage — XSS-proof)
- CORS restricted to known origins (no wildcard)
- Rate limiting via `slowapi` — 5 attempts/min on auth endpoints; account lockout after 5 failures (stored in Valkey)
- TOTP via `pyotp` for Admin/Super-Admin (mandatory 2FA)
- Pydantic input validation on all endpoints (built-in with FastAPI)
- SQLAlchemy ORM — parameterised queries only, no raw SQL
- PostgreSQL RLS — tenant isolation enforced at DB layer
- Per-message tenant validation on every WebSocket message
- Security headers middleware (CSP, HSTS, X-Frame-Options)

**React:**
- Auth tokens in httpOnly cookies — invisible to JavaScript entirely
- Route guards for UX only — all enforcement server-side
- CSP headers block injected scripts at browser level
- No sensitive data in localStorage or sessionStorage
- Operational data (bills, queues, menu) in IndexedDB with financial fields encrypted via Web Crypto API
- Encryption key derived from session token, held in memory only — lost on logout

**Offline + Security reconciliation:**
- httpOnly cookie persists across browser crashes and offline periods
- On crash recovery: user re-authenticates → encryption key re-derived → IndexedDB decrypted → active bills restored
- Server validates tenant_id on every synced record on reconnect

### Print Agent Stack

| Component | Choice |
|---|---|
| **Language** | Python (packaged via PyInstaller → .exe) |
| **Windows Service** | NSSM (Non-Sucking Service Manager) wraps launcher.exe |
| **Printer protocol** | ESC/POS via python-escpos (USB, Network, Bluetooth/Serial) |
| **Cloud connection** | Outbound WSS to Hetzner server (agent initiates, cloud never dials in) |
| **Local offline fallback** | ws://127.0.0.1:8765 (loopback only — same machine as billing counter) |
| **Rendering** | Cloud renders ESC/POS bytes from tenant template; agent receives and forwards blindly |
| **Auto-update** | launcher.exe checks version endpoint on startup + daily at 3am; downloads, verifies SHA256, replaces agent.exe — no human intervention |

**Two-process update design:**
- `launcher.exe` — registered Windows Service, rarely changes, handles update logic
- `agent.exe` — actual print agent, gets updated silently while launcher swaps it

**Authentication flow:**
1. Admin generates one-time registration token (24hr expiry) in web app
2. Token pasted into agent config on restaurant PC
3. Agent exchanges token for permanent Agent API Key (stored encrypted locally)
4. All future WSS connections use permanent key — one-time token is dead after first use
5. Admin can revoke permanent key from dashboard at any time

**Printer connectivity:**
- USB: `Usb(vendor_id, product_id)`
- Network/WiFi: `Network("192.168.x.x", port=9100)`
- Bluetooth: `Serial("COM5")` (Bluetooth Serial Profile maps to COM port on Windows)
- Windows queue: `Win32Raw("printer_name")` (fallback for non-ESC/POS printers)
- Configured once at installation — cloud never needs to know transport type

**Offline print fallback (Scenario A only):**
- Agent binds local WebSocket server to 127.0.0.1:8765 only (not 0.0.0.0 — not network-accessible)
- PWA tries cloud first → falls back to localhost:8765 if cloud unreachable
- Chrome Private Network Access handled via `Access-Control-Allow-Private-Network: true` header on local server
- Other devices (phone/tablet) offline → jobs queue in IndexedDB, flush on reconnect

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Multi-tenancy: PostgreSQL Row-Level Security (RLS), tenant_id on every entity
- Bill state machine: Single document model (Draft → KOT Sent → Billed → Void)
- Offline sync: IndexedDB with server-assigned sequential bill numbers on reconnect
- Auth: httpOnly JWT cookies, PIN for operational roles, TOTP for Admin/Super-Admin

**Important Decisions (Shape Architecture):**
- Hot/archive split: PostgreSQL range partitioning by closed_at date (monthly)
- Event bus: Valkey pub/sub (real-time) + Postgres-backed queue (at-least-once)
- Print agent: Dual-mode (cloud WSS primary, localhost:8765 fallback, same machine only)
- Suggestion engine: Valkey sorted sets, async worker, zero billing DB coupling

**Deferred to Phase 2:**
- Grafana + Loki + Prometheus (upgrade when multi-tenant traffic justifies it)
- Multi-printer routing (counter vs kitchen printer)
- Waiter reward visibility on own login

### Data Architecture

| Decision | Choice | Rationale |
|---|---|---|
| Multi-tenancy | Row-level isolation + PostgreSQL RLS | Scales to 100+ tenants; schema-per-tenant is an operational nightmare at scale |
| ORM | SQLAlchemy (async) + Alembic | Full PostgreSQL feature access (RLS, partitioning, sequences) |
| Hot/archive split | PostgreSQL range partitioning by month | Transparent to app layer; pg_partman manages partition creation; old partitions movable to cheaper storage |
| Bill number integrity | Per-tenant Postgres SEQUENCE; server-assigned on close/sync | Immutable, sequential, gap-detectable; offline bills use provisional UUID until sync |
| Suggestion store | Valkey sorted sets | ZINCRBY for frequency, sorted sets for co-occurrence; sub-millisecond reads; doubles as session cache and rate-limit store |
| Migrations | Alembic | Standard Python migration tool; integrates with SQLAlchemy |

**Core Bill Schema:**
- `bills`: id (UUID), tenant_id, bill_number (server-assigned on close, NULL offline), status (ENUM: draft | kot_sent | partially_kot_sent | billed | void), table_ref, waiter_id, opened_at, closed_at
- `bill_items`: id, bill_id, tenant_id, menu_item_id, quantity, unit_price (snapshotted at order time), kot_status (ENUM: pending | sent | ready | voided), void_requested_at, void_approved_by, void_approved_at
- `bill_events`: append-only audit ledger — id, bill_id, tenant_id, actor_id, event_type (ENUM), payload (JSONB), created_at

### Authentication & Security

| Decision | Choice |
|---|---|
| Token storage | httpOnly cookies (not localStorage — XSS-proof) |
| Operational auth | PIN-based → short-lived JWT |
| Admin auth | Email + Password + TOTP (pyotp) → JWT |
| Session expiry | 4 hours; auto-invalidate on browser close for Admin |
| Rate limiting | slowapi — 5 attempts/min on auth; account lockout after 5 failures (stored in Valkey) |
| Tenant isolation | PostgreSQL RLS + tenant_id validated on every WebSocket message |
| IndexedDB security | Financial fields encrypted via Web Crypto API; key derived from session token, held in memory only — lost on logout |
| Local print server | Binds to 127.0.0.1 only; Access-Control-Allow-Private-Network header for Chrome PNA |

### API & Communication Patterns

| Decision | Choice |
|---|---|
| API style | REST (FastAPI native, auto OpenAPI docs) |
| Versioning | /api/v1/ prefix from day one |
| WebSocket protocol | JSON envelope: `{ "type": "event.name", "tenant_id": "...", "payload": {...}, "ts": "..." }` |
| Internal event bus | Valkey pub/sub for real-time events; Postgres-backed queue for at-least-once delivery (Telegram alerts, backup confirmations) |
| Error handling | FastAPI exception handlers; structured JSON error responses with typed error codes |

### Frontend Architecture

| Decision | Choice | Rationale |
|---|---|---|
| Framework | React + Vite | SPA, no SSR needed; fastest for keyboard-first internal tooling |
| UI state | Zustand | Lightweight; ideal for multi-tab bill management, command palette, active bill sidebar |
| Server state | TanStack Query (React Query) | API data fetching, caching, background refresh |
| Component library | shadcn/ui + Tailwind CSS | Copy-paste components, fully customisable, zero runtime overhead |
| Routing | React Router v7 | Role-based route protection, distinct URL paths per role (/biller, /admin, /kitchen) |
| Offline storage | IndexedDB via idb library + Service Worker | Bills, KOT queue, print queue, menu snapshot |
| PWA | Vite PWA plugin (Workbox) | Service worker generation, manifest, install prompt |

### Infrastructure & Deployment

| Decision | Choice |
|---|---|
| Hosting | Hetzner VPS (CX31, ~€13/month) |
| PaaS | Dokploy (self-hosted, open source) |
| Reverse proxy / SSL | Traefik via Dokploy (automatic Let's Encrypt) |
| Containerisation | Docker + Docker Compose |
| CI/CD | GitHub Actions → Dokploy webhook auto-deploy on push to main |
| Error tracking | Sentry free tier — MVP day one |
| Uptime monitoring | Uptime Kuma (self-hosted) + Telegram alerts |
| Metrics / logs | Deferred to Phase 2 (Grafana + Loki + Prometheus) |
| Backup | pg_dump nightly via Ofelia cron → gpg encrypted → Cloudflare R2 (free tier, 10GB) → Telegram confirmation on success/failure |
| Backup retention | 7 years minimum (GST compliance, FR94) |

## Implementation Patterns & Consistency Rules

**12 conflict areas identified and resolved.**

### Naming Patterns

**Database (PostgreSQL + SQLAlchemy):**

| Element | Convention | Example |
|---|---|---|
| Tables | `snake_case` plural | `bills`, `bill_items`, `menu_items`, `tenant_users` |
| Columns | `snake_case` | `tenant_id`, `created_at`, `kot_status` |
| Foreign keys | `{singular_table}_id` | `bill_id`, `tenant_id`, `waiter_id` |
| Indexes | `idx_{table}_{column(s)}` | `idx_bills_tenant_id`, `idx_bill_items_bill_id` |
| Enums (PG type) | `snake_case` | `bill_status`, `kot_status` |
| Enum values | `snake_case` | `draft`, `kot_sent`, `partially_kot_sent` |
| Sequences | `tenant_{id}_bill_seq` | `tenant_abc123_bill_seq` |

**API Endpoints (FastAPI):**

| Element | Convention | Example |
|---|---|---|
| Resources | `/api/v1/{resource}` plural snake_case | `/api/v1/bills`, `/api/v1/menu_items` |
| Path params | `{id}` | `/api/v1/bills/{id}` |
| Query params | `camelCase` | `?tenantId=...&kotStatus=sent` |
| Headers | `X-{PascalCase}` | `X-Tenant-Id` |

**Python code (backend):**

| Element | Convention | Example |
|---|---|---|
| Functions | `snake_case` | `get_bill_by_id()` |
| Classes | `PascalCase` | `BillService`, `BillSchema` |
| Constants | `SCREAMING_SNAKE_CASE` | `MAX_OPEN_BILLS = 10` |
| Files | `snake_case.py` | `bill_service.py`, `auth_router.py` |
| Pydantic models | `PascalCase` + `Response`/`Request` suffix | `BillResponse`, `CreateBillRequest` |

**TypeScript/React code (frontend):**

| Element | Convention | Example |
|---|---|---|
| Components | `PascalCase` file + export | `BillTab.tsx`, `CommandPalette.tsx` |
| Hooks | `use` prefix + `camelCase` | `useBillStore.ts`, `useMenuItems.ts` |
| Utilities | `camelCase` | `formatCurrency.ts`, `formatDate.ts` |
| Stores (Zustand) | `use{Feature}Store` | `useBillingStore`, `useKitchenStore` |
| Types/interfaces | `PascalCase` | `Bill`, `BillItem`, `KotStatus` |
| Constants | `SCREAMING_SNAKE_CASE` | `MAX_BILL_TABS = 10` |
| Feature folders | `kebab-case` | `billing/`, `kitchen-display/`, `admin/` |

### Format Patterns

**Money — CRITICAL (fintech rule):**
```
Storage (DB):  integer paise only
               total_amount = 15000  →  ₹150.00
               unit_price   = 4500   →  ₹45.00

Display layer: paise / 100 → formatCurrency(paise: number): string
               formatCurrency(15000) → "₹150.00"

NEVER: store 150.00 as float in DB
NEVER: use JS floating point arithmetic on money values
NEVER: pass rupees between services — always paise
```

**Dates:**
```
Storage:  PostgreSQL TIMESTAMPTZ (UTC always)
API JSON: ISO 8601 string  →  "2026-03-13T08:00:00Z"
Display:  frontend formats to local time (IST)
NEVER:    Unix timestamps in API responses
```

**API Response Envelope:**
```json
// Success
{ "data": { "id": "...", "billNumber": 42, "status": "draft" }, "error": null }

// Error
{ "data": null, "error": { "code": "BILL_NOT_FOUND", "message": "...", "details": {} } }

// List
{ "data": { "items": [...], "total": 84, "page": 1 }, "error": null }
```

**JSON field naming:**
```
API JSON output:  camelCase  (billNumber, tenantId, kotStatus, createdAt)
Pydantic config:  model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
Frontend types:   camelCase matching API output exactly
DB columns:       snake_case (SQLAlchemy handles mapping)
```

**WebSocket message envelope:**
```json
{ "type": "bill.item_added", "tenantId": "uuid", "payload": { ... }, "ts": "2026-03-13T08:00:00Z" }
```

Event type format: `{resource}.{action}` — dot notation, snake_case segments.

**Canonical event types:**
```
bill.created            bill.item_added         bill.kot_fired
bill.payment_collected  bill.closed             bill.void_requested
bill.void_approved      menu.availability_changed
print.job_queued        print.job_completed     print.agent_offline
kitchen.item_ready      kitchen.table_ready     session.expired
```

### Structure Patterns

**Backend (FastAPI):**
```
app/
  api/v1/routes/          # One file per resource, max 100 lines
    bills.py
    menu_items.py
    auth.py
  models/                 # SQLAlchemy ORM models — one file per model
  schemas/                # Pydantic schemas — one file per resource
  services/               # Business logic — split by operation
    bill_create_service.py
    bill_kot_service.py
    bill_void_service.py
    bill_sync_service.py
  repositories/           # DB queries only — one file per model
  db/
    session.py
    base.py
  core/
    config.py
    security.py
    dependencies.py
  websocket/
    manager.py
    handlers/
  workers/
    suggestion_worker.py
    backup_worker.py
    telegram_worker.py
```

**Frontend (React + Vite):**
```
src/
  features/               # Feature-based — agents never cross boundaries
    billing/
      components/         # BillTab.tsx, CommandPalette.tsx, BillSidebar.tsx
      hooks/
      stores/
      types.ts
    kitchen-display/
    admin/
    waiter/
  shared/
    components/
    hooks/                # useWebSocket.ts, useOfflineSync.ts
    utils/                # formatCurrency.ts, formatDate.ts
    types/
  lib/
    api.ts                # Axios client + envelope unwrapper
    queryClient.ts
    websocket.ts
    db.ts                 # IndexedDB (idb) setup
  app/
    routes.tsx
    App.tsx
```

### Process Patterns

**Error handling:**
```python
# Backend — always typed error codes
raise HTTPException(status_code=404, detail={"code": "BILL_NOT_FOUND", "message": "..."})
```
```typescript
// Frontend — toast for user-facing, Error Boundary for crash
onError: (error) => toast.error(error.response.data.error.message)
// NEVER: alert() or console.error() for user-facing errors
// ALWAYS: React Error Boundary wraps each feature root
```

**Loading states:**
```typescript
// ALWAYS use TanStack Query states
const { data, isLoading, isFetching } = useQuery(...)
// isLoading → skeleton screen
// isFetching → subtle background indicator only
// NEVER: local useState<boolean> for server data loading
```

**Zustand vs TanStack Query boundary:**
```
Zustand:        UI state only — active tab, palette open/closed, bill lock, offline flag
TanStack Query: all server data — bills, menu items, staff list
NEVER:          duplicate server data in Zustand
```

**Tenant isolation (mandatory):**
```python
# EVERY repository function receives tenant_id as first param
async def get_bill(tenant_id: str, bill_id: UUID) -> BillResponse: ...
# NEVER: query without explicit tenant_id parameter
```

### All AI Agents MUST

1. Store all money as **integer paise** — never float, never rupees in DB
2. Return all API responses in **wrapped envelope** `{data, error}`
3. Use **camelCase** for all JSON API fields (Pydantic `alias_generator=to_camel`)
4. Pass **`tenant_id` as first parameter** to every repository function
5. Use **TanStack Query** for all server data — never `useState` for API data
6. Name WebSocket events as **`resource.action`** dot notation
7. Place all feature code inside **`src/features/{feature-name}/`** — no cross-feature imports
8. Use **ISO 8601 UTC strings** for all dates in API responses
9. Never write **raw SQL** — SQLAlchemy ORM only
10. Never store **auth tokens** in `localStorage` or `sessionStorage`
11. **No file exceeds 100 lines** — split immediately, one responsibility per file

```
WRONG: bill_service.py (380 lines)  |  BillingScreen.tsx (290 lines)
RIGHT: bill_create_service.py (~60) + bill_kot_service.py (~70) + bill_void_service.py (~55)
       BillTab.tsx (~70) + CommandPalette.tsx (~90) + BillSidebar.tsx (~65)
```

12. **No `any` type** — full type safety mandatory in both languages

```typescript
// TypeScript: tsconfig strict: true, noImplicitAny: true
// ESLint: @typescript-eslint/no-explicit-any → error
// FORBIDDEN: const bill: any  |  function fn(x: any)
// REQUIRED:  const bill: Bill |  function fn(x: BillItem): void
```
```python
# Python: mypy --strict in CI, type errors fail the build
# FORBIDDEN: def get_bill(id) -> dict  |  data: Any
# REQUIRED:  async def get_bill(tenant_id: str, bill_id: UUID) -> BillResponse
# No Dict[str, Any] — define a Pydantic model instead
```

## Project Structure & Boundaries

### Complete Project Directory Structure

```
sphotel-billing/                          # Monorepo root
├── .gitignore                            # covers __pycache__, dist, .env files
├── .env.example                          # all env vars across all services documented
├── Makefile                              # canonical dev commands for all agents
│     make dev          → docker compose up (dev override)
│     make test-backend → cd backend && pytest
│     make test-frontend→ cd frontend && pnpm test
│     make migrate      → cd backend && alembic upgrade head
│     make build-agent  → cd print-agent && python build.py
├── docker-compose.yml                    # production stack
├── docker-compose.dev.yml                # local dev override (hot reload, exposed ports)
├── .github/
│   └── workflows/
│       ├── ci-backend.yml               # mypy --strict + pytest on PR
│       └── ci-frontend.yml              # tsc + vitest on PR
│
├── backend/                             # FastAPI application
│   ├── Dockerfile
│   ├── pyproject.toml                   # deps + tool configs
│   │     [tool.mypy] strict = true, plugins = ["pydantic.mypy"]
│   │     [tool.ruff] line-length = 88, select = ["E","F","I","UP"]
│   │     [tool.pytest.ini_options] asyncio_mode = "auto"
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/                    # DB migration files
│   ├── app/
│   │   ├── main.py                      # FastAPI app + middleware stack (≤100 lines)
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py            # mounts all sub-routers
│   │   │       └── routes/              # one file per resource, ≤100 lines each
│   │   │           ├── auth.py          # FR32–FR37, FR74, FR84–FR87, FR90, FR93
│   │   │           ├── bills.py         # FR1–FR13, FR61–FR63, FR69, FR79
│   │   │           ├── kot.py           # FR14–FR18
│   │   │           ├── payments.py      # FR19–FR23, FR76, FR77, FR82
│   │   │           ├── print_jobs.py    # FR24–FR27, FR65, FR78
│   │   │           ├── menu.py          # FR28–FR31, FR75
│   │   │           ├── staff.py         # FR38–FR41, FR71
│   │   │           ├── expenses.py      # FR42–FR44
│   │   │           ├── analytics.py     # FR49–FR50, FR73, FR80, FR81
│   │   │           ├── gst.py           # FR51–FR53
│   │   │           ├── tenants.py       # FR57–FR60, FR92, FR94
│   │   │           └── super_admin.py   # FR57, FR58
│   │   ├── models/                      # SQLAlchemy ORM models — one per entity
│   │   │   ├── base.py                  # DeclarativeBase + tenant_id mixin
│   │   │   ├── bill.py                  # bills + bill_items + bill_events tables
│   │   │   ├── menu_item.py
│   │   │   ├── tenant.py
│   │   │   ├── user.py
│   │   │   ├── staff.py
│   │   │   ├── expense.py
│   │   │   ├── print_agent.py
│   │   │   └── audit_log.py             # append-only, no updates/deletes
│   │   ├── schemas/                     # Pydantic schemas — one per resource
│   │   │   ├── bill.py                  # CreateBillRequest, BillResponse, BillItemResponse
│   │   │   ├── auth.py                  # LoginRequest, TokenResponse, PinLoginRequest
│   │   │   ├── menu.py
│   │   │   ├── payment.py
│   │   │   ├── staff.py
│   │   │   ├── expense.py
│   │   │   ├── analytics.py
│   │   │   ├── gst.py
│   │   │   └── tenant.py
│   │   ├── services/                    # Business logic — split by operation, ≤100 lines
│   │   │   ├── sync/                    # FR54–FR56 — offline reconciliation (pre-split)
│   │   │   │   ├── bill_sync_orchestrator.py   # coordinates full sync flow
│   │   │   │   ├── bill_number_assigner.py     # per-tenant sequence assignment
│   │   │   │   ├── conflict_resolver.py        # server-state-wins logic
│   │   │   │   └── sync_queue_flusher.py       # flushes IndexedDB queue in order
│   │   │   ├── bill_create_service.py   # FR1–FR6
│   │   │   ├── bill_kot_service.py      # FR7–FR10, FR14–FR18
│   │   │   ├── bill_void_service.py     # FR9–FR10, FR35
│   │   │   ├── payment_service.py       # FR19–FR23
│   │   │   ├── print_service.py         # FR24–FR26 — queue + dispatch
│   │   │   ├── print_render_service.py  # FR78 — ESC/POS rendering (cloud-side)
│   │   │   ├── menu_service.py          # FR28–FR31
│   │   │   ├── auth_service.py          # FR32–FR37, FR84–FR87
│   │   │   ├── staff_service.py         # FR38–FR41
│   │   │   ├── payroll_service.py       # FR40–FR41
│   │   │   ├── expense_service.py       # FR42–FR44
│   │   │   ├── gst_service.py           # FR51–FR53
│   │   │   ├── analytics_service.py     # FR49–FR50, FR80
│   │   │   └── backup_service.py        # FR47, FR94
│   │   ├── repositories/                # DB queries only — one per model
│   │   │   ├── bill_repository.py
│   │   │   ├── menu_repository.py
│   │   │   ├── user_repository.py
│   │   │   ├── staff_repository.py
│   │   │   ├── expense_repository.py
│   │   │   ├── audit_repository.py
│   │   │   └── tenant_repository.py
│   │   ├── websocket/
│   │   │   ├── manager.py               # connection pool, tenant channel management
│   │   │   └── handlers/                # one handler per event domain
│   │   │       ├── bill_handler.py
│   │   │       ├── menu_handler.py
│   │   │       ├── kitchen_handler.py
│   │   │       └── print_handler.py
│   │   ├── workers/
│   │   │   ├── telegram/                # at-least-once delivery — pre-split
│   │   │   │   ├── telegram_dispatcher.py      # Postgres queue consumer
│   │   │   │   ├── eod_report_formatter.py     # FR45
│   │   │   │   ├── alert_formatter.py          # FR46 — voids, cash, printer
│   │   │   │   └── backup_formatter.py         # FR47
│   │   │   ├── suggestion_worker.py     # FR69, FR79, FR95 — Valkey sorted sets
│   │   │   ├── archive_worker.py        # FR94 — hot→archive partition migration
│   │   │   └── backup_worker.py         # nightly pg_dump + gpg + R2 upload
│   │   ├── core/
│   │   │   ├── config.py                # pydantic-settings + env vars
│   │   │   ├── security/                # pre-split — four distinct responsibilities
│   │   │   │   ├── jwt.py               # token creation + validation
│   │   │   │   ├── pin.py               # PIN hashing + verification
│   │   │   │   ├── totp.py              # TOTP setup + verify (wraps pyotp)
│   │   │   │   └── rate_limiter.py      # slowapi config + lockout logic
│   │   │   ├── dependencies.py          # FastAPI Depends() — auth, tenant, db session
│   │   │   ├── middleware.py            # CORS, HTTPS redirect, security headers
│   │   │   └── audit.py                 # FR83, FR86 — append-only audit log writer
│   │   └── db/
│   │       ├── session.py               # AsyncSession factory + RLS context setter
│   │       └── valkey.py                # Valkey client + pub/sub setup
│   └── tests/
│       ├── conftest.py                  # fixtures — test DB, auth tokens, tenant
│       ├── unit/
│       │   ├── services/
│       │   │   ├── test_bill_create_service.py
│       │   │   ├── test_bill_kot_service.py
│       │   │   ├── test_bill_number_assigner.py
│       │   │   └── test_conflict_resolver.py
│       │   └── core/
│       │       ├── test_jwt.py
│       │       └── test_pin.py
│       ├── integration/
│       │   ├── routes/
│       │   │   ├── test_bills_route.py   # real DB + auth
│       │   │   └── test_payments_route.py
│       │   └── workers/
│       │       └── test_telegram_worker.py  # mocked Telegram API, real DB queue
│       └── e2e/
│           ├── test_billing_flow.py      # create → KOT → pay → print (happy path)
│           └── test_offline_sync.py      # disconnect → bill → reconnect → verify
│
├── frontend/                            # React + Vite PWA
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts                   # Vite PWA plugin (Workbox)
│   ├── tsconfig.json                    # strict: true, noImplicitAny: true
│   ├── tailwind.config.ts
│   ├── .eslintrc.json                   # @typescript-eslint/no-explicit-any: error
│   ├── .env.example
│   ├── .env.local                       # gitignored
│   ├── .env.production                  # gitignored — Dokploy injects
│   ├── public/
│   │   ├── manifests/                   # role-specific PWA install (FR: installable per role)
│   │   │   ├── biller.manifest.json
│   │   │   ├── kitchen.manifest.json
│   │   │   └── admin.manifest.json
│   │   └── icons/
│   └── src/
│       ├── app/
│       │   ├── App.tsx
│       │   ├── routes.tsx               # React Router v7 — role-based route protection
│       │   └── providers.tsx            # QueryClient, WS, theme providers
│       ├── features/                    # no cross-feature imports permitted
│       │   ├── billing/                 # FR1–FR13, FR19–FR23, FR61–FR63, FR69, FR79
│       │   │   ├── components/
│       │   │   │   ├── BillTab.tsx
│       │   │   │   ├── BillTab.test.tsx           # co-located Vitest tests
│       │   │   │   ├── BillTabBar.tsx
│       │   │   │   ├── BillSidebar.tsx
│       │   │   │   ├── BillSidebar.item.tsx
│       │   │   │   ├── CommandPalette.tsx
│       │   │   │   ├── CommandPalette.test.tsx
│       │   │   │   ├── ItemSearch.tsx
│       │   │   │   ├── ShortcutOverlay.tsx
│       │   │   │   ├── PaymentModal.tsx
│       │   │   │   └── VoidRequest.tsx
│       │   │   ├── hooks/
│       │   │   │   ├── useBillSync.ts
│       │   │   │   ├── useCommandPalette.ts
│       │   │   │   └── usePrintJob.ts   # cloud WSS → localhost:8765 fallback
│       │   │   ├── stores/
│       │   │   │   └── useBillingStore.ts  # active tab, palette state, bill locks
│       │   │   └── types.ts
│       │   ├── kitchen-display/         # FR14–FR18
│       │   │   ├── components/
│       │   │   │   ├── KotCard.tsx
│       │   │   │   ├── KotCard.item.tsx
│       │   │   │   └── KotFeed.tsx
│       │   │   └── hooks/
│       │   │       └── useKotFeed.ts
│       │   ├── waiter/                  # FR11–FR12
│       │   │   ├── components/
│       │   │   │   ├── WaiterBillView.tsx
│       │   │   │   └── HandoffButton.tsx
│       │   │   └── hooks/
│       │   ├── admin/                   # FR28–FR31, FR38–FR53, FR57–FR60
│       │   │   ├── components/
│       │   │   │   ├── dashboard/
│       │   │   │   │   ├── LiveDashboard.tsx
│       │   │   │   │   └── AnalyticsView.tsx
│       │   │   │   ├── menu/
│       │   │   │   │   ├── MenuTable.tsx
│       │   │   │   │   └── CsvImport.tsx
│       │   │   │   ├── staff/
│       │   │   │   │   ├── PayrollView.tsx
│       │   │   │   │   └── AttendanceEntry.tsx
│       │   │   │   ├── expenses/
│       │   │   │   │   └── ExpenseForm.tsx
│       │   │   │   └── settings/
│       │   │   │       ├── TelegramConfig.tsx
│       │   │   │       ├── PrintAgentPanel.tsx
│       │   │   │       └── GstConfig.tsx
│       │   │   └── hooks/
│       │   └── super-admin/             # FR57–FR60
│       │       └── components/
│       │           └── TenantProvisioner.tsx
│       ├── shared/
│       │   ├── components/
│       │   │   ├── ui/                  # shadcn/ui components
│       │   │   ├── OfflineBanner.tsx    # FR66
│       │   │   ├── ErrorBoundary.tsx
│       │   │   └── LoadingSkeleton.tsx
│       │   ├── hooks/
│       │   │   ├── useWebSocket.ts
│       │   │   ├── useOfflineSync.ts
│       │   │   └── useAudioFeedback.ts  # FR67
│       │   ├── utils/
│       │   │   ├── formatCurrency.ts    # paise → "₹150.00"
│       │   │   ├── formatDate.ts        # ISO UTC → IST display
│       │   │   └── apiClient.ts         # Axios + envelope unwrapper
│       │   └── types/
│       │       ├── bill.ts
│       │       ├── menu.ts
│       │       ├── auth.ts
│       │       └── websocket.ts
│       └── lib/
│           ├── queryClient.ts
│           ├── websocket.ts             # WS singleton + reconnect + event emitter
│           └── db/                     # IndexedDB — pre-split
│               ├── schema.ts            # idb setup + schema definition
│               ├── bills.db.ts          # offline bill CRUD
│               ├── queue.db.ts          # KOT queue + print queue helpers
│               └── crypto.db.ts         # Web Crypto encrypt/decrypt
│
├── print-agent/                        # Python Windows service
│   ├── launcher/
│   │   └── launcher.py                 # Windows Service, update checker, starts agent
│   ├── agent/
│   │   ├── main.py                     # entry point
│   │   ├── ws_client.py                # outbound WSS + reconnect
│   │   ├── local_server.py             # ws://127.0.0.1:8765 + PNA header
│   │   ├── print_queue.py              # local queue — handles printer offline
│   │   ├── printer.py                  # python-escpos dispatch (USB/Network/Serial)
│   │   ├── auth.py                     # token exchange + credential storage
│   │   └── updater.py                  # version check + download + sha256 verify
│   ├── config/
│   │   └── agent_config.py             # pydantic-settings — api_key, printer_type
│   ├── tests/
│   │   ├── test_updater.py
│   │   ├── test_local_server.py
│   │   ├── test_print_queue.py
│   │   └── test_printer.py             # mock python-escpos, verify ESC/POS bytes
│   ├── build.py                        # PyInstaller → agent.exe
│   └── requirements.txt
│
├── infra/
│   ├── docker-compose.yml
│   ├── docker-compose.monitoring.yml   # Uptime Kuma + Sentry (Phase 2: Grafana)
│   ├── backup/
│   │   ├── Dockerfile
│   │   └── backup.sh                   # pg_dump + gpg + R2 upload
│   ├── dokploy/
│   │   └── app.yml
│   └── scripts/                        # operational one-liners
│       ├── create_tenant.sh            # super-admin tenant provisioning
│       ├── rotate_agent_key.sh         # revoke + regenerate print agent credential
│       ├── manual_backup.sh            # on-demand backup trigger
│       ├── archive_partition.sh        # manual hot→archive migration
│       └── seed_suggestions.py         # backfill Valkey from historical bills on first deploy
│
└── docs/
    └── architecture.md                 # this document
```

### Architectural Boundaries & Integration Points

**Service communication map:**
```
Frontend PWA   ←→  Backend API:      HTTPS REST /api/v1/* (httpOnly cookie auth)
Frontend PWA   ←→  Backend WS:       WSS /ws (tenant validated per message)
Frontend PWA   ←→  Print Agent:      ws://127.0.0.1:8765 (same machine only, offline fallback)
Backend        ←→  Print Agent:      WSS (agent opens outbound connection — cloud never dials in)
Backend        ←→  Valkey:           pub/sub (real-time events) + sorted sets (suggestions)
Backend        ←→  Telegram API:     async HTTP via telegram_worker (at-least-once via Postgres queue)
Backend        ←→  Cloudflare R2:    S3-compatible API via backup_worker
Backend        ←→  PostgreSQL:       SQLAlchemy async + RLS (every query scoped by tenant_id)
```

**FR → location mapping:**

| FR Category | Backend Location | Frontend Location |
|---|---|---|
| Billing engine | `routes/bills.py` + `services/bill_*` | `features/billing/` |
| KOT management | `routes/kot.py` + `services/bill_kot_service.py` | `features/billing/` + `features/kitchen-display/` |
| Offline sync | `services/sync/` | `shared/hooks/useOfflineSync.ts` + `lib/db/` |
| Print | `routes/print_jobs.py` + `services/print_*` | `features/billing/hooks/usePrintJob.ts` |
| Real-time WS | `websocket/manager.py` + `websocket/handlers/` | `lib/websocket.ts` + `shared/hooks/useWebSocket.ts` |
| Auth | `core/security/` + `routes/auth.py` | `app/routes.tsx` (route guards) |
| Suggestion engine | `workers/suggestion_worker.py` → Valkey | `features/billing/components/ItemSearch.tsx` |
| Telegram alerts | `workers/telegram/` (Postgres-backed queue) | Admin config only |
| Audit | `core/audit.py` + `repositories/audit_repository.py` | Admin read-only view |
| GST compliance | `services/gst_service.py` + `routes/gst.py` | `features/admin/` |

## Architecture Validation Results

### Coherence Validation ✅

**Decision compatibility:** All technology choices confirmed compatible — FastAPI + SQLAlchemy async + asyncpg + PostgreSQL 16 + Valkey + React + Vite + TanStack Query + Zustand + shadcn/ui. No peer dependency conflicts. All MIT/BSD/Apache licensed.

**Pattern consistency:** snake_case DB → camelCase JSON (Pydantic alias_generator) → camelCase TypeScript is a clean unidirectional mapping. Wrapped API envelope consistent with TanStack Query interceptor pattern. WebSocket `resource.action` naming consistent with REST resource naming.

**Structure alignment:** Pre-split applied to all modules that would breach 100-line limit (sync/, telegram/, security/, db/). Feature-based frontend prevents cross-boundary agent pollution.

### Requirements Coverage Validation ✅

All 95 functional requirements mapped to specific files. All NFRs architecturally supported:

| NFR | Architectural support |
|---|---|
| < 10ms active queries | Hot/archive range partitioning + Valkey for suggestions |
| < 3s menu/KOT sync | WebSocket pub/sub + Valkey broadcast |
| < 100ms command palette | Client-side Valkey sorted set reads |
| Zero data loss | IndexedDB offline + 30s snapshots + Postgres ACID |
| 7-year audit retention | Archive partitions + Cloudflare R2 backup |
| Tenant isolation | PostgreSQL RLS at DB layer — enforced structurally |
| TOTP + PIN auth | `core/security/totp.py` + `core/security/pin.py` |

### Gaps Identified & Resolved

**Gap 1 — Bill locking server-side (FR64):**
Resolved: Valkey stores bill locks with TTL — `SETEX bill_lock:{bill_id} 300 {user_id}`. Add `services/bill_lock_service.py`. `bill_handler.py` checks and broadcasts lock state.

**Gap 2 — Cash session management (FR77, FR21):**
Resolved: Add `services/cash_session_service.py` — shift open (opening balance), shift close (expected vs actual cash, discrepancy detection). Endpoints added to `routes/staff.py`.

**Gap 3 — WebSocket reconnect strategy:**
Resolved: `lib/websocket.ts` implements exponential backoff — 1s → 2s → 4s → max 30s. Mandatory constraint, not left to agent interpretation.

### Phase 2 Deferrals (confirmed, architecturally supported)

| Feature | What it is | Why deferred |
|---|---|---|
| Multi-printer routing | Two named printers (counter + kitchen), cloud routes by `printer_id` | sphotel uses tablet KDS — kitchen printer not needed at launch. Config extension only, no re-architecture |
| Telegram bot commands | `/sales`, `/open`, `/void` — owners query live data from Telegram chat | Inbound webhook alongside existing outbound worker. Deferred until outbound alerts are battle-tested |
| Bill merge / split | Split one bill into two (separate payment) or merge two into one | State machine edge cases with mid-flight KOT items need stable billing foundation first |

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] 95 FRs analyzed and mapped to architectural components
- [x] Project complexity assessed — High / Enterprise-class
- [x] 8 cross-cutting concerns identified and resolved
- [x] All technical constraints documented

**✅ Technology Stack**
- [x] All layers decided — frontend, backend, DB, cache, monitoring, backup, deployment
- [x] Full open-source stack — zero licensing cost
- [x] Hetzner + Dokploy — ~€13/month operational cost for tenant #1

**✅ Architectural Decisions**
- [x] Multi-tenancy: PostgreSQL RLS
- [x] Bill = KOT: single document state machine
- [x] Offline sync: IndexedDB + server-assigned sequential bill numbers
- [x] Hot/archive: range partitioning by month (pg_partman)
- [x] Print agent: dual-mode (cloud WSS primary + localhost:8765 fallback)
- [x] Suggestion engine: Valkey sorted sets, isolated async worker
- [x] Auth: httpOnly cookies, TOTP (pyotp), PIN, rate limiting (slowapi)
- [x] Monitoring: Sentry + Uptime Kuma (MVP) → Grafana stack (Phase 2)
- [x] Backup: pg_dump + gpg + Cloudflare R2 (free tier)

**✅ Implementation Patterns**
- [x] 12 mandatory rules with examples and anti-patterns
- [x] Money: integer paise enforced throughout
- [x] Type safety: `mypy --strict` + TypeScript `strict: true` + `noImplicitAny: true`
- [x] 100-line file limit with pre-split applied to complex modules
- [x] camelCase JSON output via Pydantic alias_generator

**✅ Project Structure**
- [x] Complete monorepo tree — backend, frontend, print-agent, infra
- [x] All 95 FRs mapped to specific file locations
- [x] Test structure mirrors service structure
- [x] Operational scripts included
- [x] Role-specific PWA manifests defined

### Architecture Readiness Assessment

**Overall Status: READY FOR IMPLEMENTATION**
**Confidence Level: High**

**Key strengths:**
- Bill = KOT single document model eliminates an entire class of sync bugs at the data layer
- PostgreSQL RLS means tenant isolation is DB-enforced — no application-level trust required
- Pre-split file structure prevents 100-line violations before implementation begins
- Dual-mode print agent handles all realistic offline scenarios at sphotel
- Suggestion engine fully isolated from billing DB — zero performance coupling
- At-least-once Telegram delivery via Postgres queue — no silent financial alert drops
- All Phase 2 features architecturally supported — zero re-architecture required to unlock them

**First implementation priorities (ordered):**
1. `infra/docker-compose.yml` — Postgres + Valkey running locally
2. `backend/alembic/versions/` — DB schema (bills, bill_items, bill_events, tenants, users)
3. `backend/core/security/` — auth foundation before any routes
4. `backend/api/v1/routes/auth.py` — PIN login + credential + TOTP flows
5. `backend/api/v1/routes/bills.py` + `services/bill_*` — the core billing loop
6. `frontend/features/billing/` — Biller UI (highest-value surface)
7. `print-agent/` — after billing is stable and tested
