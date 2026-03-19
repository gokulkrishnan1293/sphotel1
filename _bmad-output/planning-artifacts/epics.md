---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
workflowStatus: complete
completedAt: '2026-03-17'
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/architecture.md'
  - '_bmad-output/planning-artifacts/ux-design-specification.md'
---

# sphotel - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for sphotel, decomposing the requirements from the PRD, UX Design, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Biller can create a new bill and add menu items via fuzzy text search
FR2: Biller can add menu items via character shortcodes (e.g. `CF` = Chicken Fried Rice) or numeric codes (e.g. `14x2` = item 14, quantity 2)
FR3: Biller can add menu items via a command palette triggered by a keyboard shortcut
FR4: Biller can manage up to 10 simultaneous open bills via a tab interface; the maximum is configurable per tenant by Admin
FR5: Biller can switch between open bills via F-key hotkeys
FR6: Biller can view all active bills in a persistent sidebar panel showing table, item count, time open, and running total
FR7: Biller can fire a KOT for items on a bill, sending only items not yet dispatched to the kitchen
FR8: Biller can fire partial KOTs — sending some items immediately and holding others for a later fire
FR9: Biller can request a void for KOT-fired items (requires Admin approval before removal)
FR10: Biller cannot modify or delete KOT-fired items without explicit Admin approval
FR11: Waiter (optional mode) can create and manage bills on their own device with their identity auto-loaded on login
FR12: Waiter can transfer a finalized bill to the billing counter for payment collection
FR13: System assigns immutable sequential bill numbers; voided bills retain their number with a VOID stamp; gaps are auto-flagged
FR14: Kitchen Staff can view all active KOTs in real time on the Kitchen Display
FR15: Kitchen Staff can mark individual items as ready on an active KOT
FR16: Kitchen Staff can mark a full table order as ready, triggering a notification on the Biller's active tab for that table
FR17: Kitchen Staff can mark menu items as unavailable, propagating the change to all billing terminals in real time
FR18: System sends only delta updates to the kitchen on KOT modification — added or changed items only, not a full reprint
FR19: Biller can collect payment for a bill split across multiple payment methods (cash, UPI, card) in a single transaction
FR21: System predicts expected cash balance at shift close; Biller confirms match or flags discrepancy — investigation triggered only on mismatch
FR22: System automatically flags and logs any bill modified after printing as "amended" in the audit record
FR23: Admin can view the complete audit history of any bill including all changes, timestamps, and actors
FR24: System queues and dispatches print jobs to a locally installed print agent without blocking the billing UI
FR25: Biller can reprint any closed bill on demand via keyboard shortcut
FR26: Print agent maintains a job queue when offline and flushes all queued jobs automatically on reconnect
FR27: Admin can register, view status of, and manage print agents from the Admin panel
FR28: Admin can manage menu items via an inline table-editing interface (name, category, price, availability, GST category)
FR29: Admin can bulk import and export the menu as a CSV file, with a diff preview before applying changes
FR30: Admin can reorder menu categories and items, with order reflected in billing search and display
FR31: Availability changes made by Kitchen Staff or Admin propagate to all active billing terminals within 3 seconds
FR32: System enforces six distinct roles with non-overlapping capability boundaries: Biller, Waiter, Kitchen Staff, Manager, Admin, Super-Admin
FR33: Operational roles (Biller, Waiter, Kitchen Staff, Manager) authenticate via PIN; each action is tagged to the authenticated PIN holder
FR34: Admin and Super-Admin authenticate via email/password credentials with short-lived session tokens (4-hour expiry, auto-invalidated on browser close for shared devices)
FR35: Admin can approve or reject Biller void requests; every void is logged with requester, approver, reason, and timestamp
FR36: Every bill, KOT action, payment, and void is permanently tagged to the authenticated user who performed it
FR37: All sessions auto-expire after 4 hours of inactivity
FR38: Manager or Admin can manually record staff attendance per shift (who worked, which shift)
FR39: Admin can configure reward calculation formulas per tenant (percentage, flat rate, hybrid, or custom)
FR40: System auto-calculates earned rewards per staff member at shift or day close based on the configured formula
FR41: Manager and Admin can view a payroll summary showing attendance, bills handled, total value billed, and calculated payout per staff member per period
FR42: Manager or Admin can record supplier invoices with vendor name, category, amount, date, and payment method
FR43: Admin can manage a configurable vendor and expense category directory per tenant
FR44: System includes supplier expense data in EOD Telegram reports and historical analytics
FR45: System automatically sends a daily EOD summary to the configured tenant Telegram group at a configurable time
FR46: System sends real-time Telegram alerts to the tenant owner group for: void requests, large cash payments (above configurable threshold), cash discrepancies, and print agent going offline
FR47: System sends a daily encrypted backup confirmation message to the tenant owner Telegram group
FR48: Admin configures Telegram integration by adding a single group chat ID per tenant — a bot posts all alerts and EOD reports to the shared owner group
FR49: Admin can view a live operations dashboard showing open bills, KOT pipeline status, staff currently on duty, and printer agent connectivity status
FR50: Admin can view historical analytics including revenue trends by period, peak hour patterns, top items by volume and value, waiter performance over time, void rate trends, and expense vs revenue comparisons
FR51: Admin can configure GST rates, slab structures, and applicable item categories per tenant
FR52: Admin can include or exclude specific bills from the GST report, with excluded bills flagged separately in the export
FR53: System generates an exportable GST report with sequential bill numbers, included totals, and an audit-ready excluded bill record
FR54: System continues to accept bill creation and modification when internet connectivity is unavailable, storing data locally on the device
FR55: System automatically syncs locally stored data to the server upon reconnection, with the server assigning sequential bill numbers to offline-created bills
FR56: System automatically recovers all active bill state after a browser crash without requiring re-entry by the user
FR57: Super-Admin can provision new tenants with isolated data environments, per-tenant URL routing, and an Admin account
FR58: Super-Admin can view aggregate platform analytics (total tenants, total bills processed) without accessing any individual tenant's data
FR59: System enforces complete data isolation between tenants at the database query level
FR60: New tenants are guided through initial system configuration via an onboarding checklist on first login
FR61: Biller can access a keyboard shortcut overlay displaying all available shortcuts
FR62: System surfaces menu items relevant to the current time of day in a "Right Now" section displayed above the main billing search results
FR63: Biller can save and trigger bill templates (preset item combinations) via a keyboard shortcut
FR64: System prevents concurrent edits to the same bill by displaying a lock indicator showing which user holds the bill
FR65: Print agent authenticates with the cloud server via an Admin-generated one-time token
FR66: System displays a persistent offline mode indicator when operating without server connectivity
FR67: System provides audio feedback for key billing events (item added, KOT sent, payment received)
FR69: System suggests up to 3 items that have been co-ordered with the added item in at least 20% of past orders, displayed inline below the added item
FR71: Waiter can view their own performance stats (bills served, total value, shift summary) on login
FR72: Users can set a display theme preference (dark mode / high contrast / light)
FR73: Admin can view a per-bill status timeline showing key timestamps (opened, KOT sent, bill generated, payment collected)
FR74: Admin can create, edit, deactivate, and reset PINs for all staff accounts
FR75: Admin can configure the restaurant's table and section layout used for bill assignment
FR76: Biller can apply a discount or mark a bill as complimentary with a reason, subject to configurable Admin approval rules
FR77: Manager or Biller can formally open and close a shift, gating cash session creation and payroll period tracking
FR78: Admin can configure the token slip print template per tenant (restaurant name, fields displayed)
FR79: Billing search surfaces the top 5 most frequently ordered items (all-time) and the top 5 most recently added items in the current session, displayed above main search results
FR80: Admin can search bill history by bill number, table, waiter, date range, and amount
FR81: Admin can export operational reports (daily revenue summary, payroll report, supplier expense ledger) as CSV or PDF
FR82: Biller or Admin can correct a payment method record post-collection with reason logging
FR83: System logs all Admin and Manager configuration changes with timestamp and actor
FR84: System enforces rate limiting and account lockout after 5 consecutive failed login attempts for any role; locked accounts require Admin reset for staff roles or email-based reset for Admin/Super-Admin
FR85: Admin can immediately invalidate all active sessions for any staff member
FR86: System encrypts sensitive data (financial records, payroll, payment data) at rest in the database
FR87: System prevents any user from granting permissions equal to or higher than their own role level
FR88: All WebSocket connections use WSS (TLS-encrypted) — plain WS is not permitted
FR89: Each role has explicit data visibility boundaries — Billers see only their own session data; Managers see staff data but not financial reports; Admins see everything within their tenant
FR90: Admin and Super-Admin can change their own credentials; Super-Admin can reset any Admin's credentials
FR92: Admin can export a complete data archive of all tenant data (bills, staff, expenses, reports) for portability
FR93: Admin and Super-Admin logins support TOTP-based two-factor authentication via any standard authenticator app
FR94: System retains bill records and audit logs in a hot/archive two-layer architecture — live database holds a rolling week of active data; archive database retains complete historical records for a minimum configurable period (default 7 years) for GST compliance
FR95: Suggestion engine data (item co-occurrence, order frequency, time-based patterns) is maintained in a separate read-optimised datastore with no read/write impact on the live billing database

### NonFunctional Requirements

NFR1: Bill completion time (trained biller) — < 15 seconds end-to-end (core success criterion)
NFR2: Active bill / menu query response — < 10ms (hot data layer — today's data only)
NFR3: KOT and menu sync propagation — < 3 seconds across all terminals (real-time kitchen coordination)
NFR4: App shell First Contentful Paint — < 1.5 seconds on 4G (staff daily login experience)
NFR5: Billing screen Time to Interactive — < 2 seconds on 4G (counter readiness under pressure)
NFR6: Offline mode activation — < 500ms after connection loss (staff must not notice the switch)
NFR7: Print queue flush on reconnect — < 5 seconds for all queued jobs (no delayed receipts post-outage)
NFR8: Command palette response — < 100ms from keystroke to results (keyboard-first UX requires instant feedback)
NFR9: WebSocket reconnect (exponential backoff) — 1s → 2s → 4s → max 30s (predictable recovery behavior)
NFR10: Hot database layer serves only the rolling week of active data — query performance is guaranteed regardless of historical data volume
NFR11: Suggestion engine datastore is read-only and separate from the billing database — zero query contention
NFR12: All Admin and Super-Admin logins require TOTP two-factor authentication
NFR13: All roles enforce rate limiting — account locked after 5 consecutive failed attempts; staff role accounts require Admin reset; Admin/Super-Admin accounts unlock via email reset
NFR14: All session tokens are short-lived (configurable, default 4-hour expiry); no persistent tokens stored on device
NFR15: Sessions auto-invalidate on browser close for Admin roles on shared devices
NFR16: All data in transit encrypted via TLS 1.2+ (HTTPS and WSS — no HTTP or plain WS permitted)
NFR17: All sensitive data at rest encrypted in the database (financial records, payroll, payment records, audit logs)
NFR18: Daily backups encrypted before upload to cloud storage
NFR19: Print agent communication encrypted end-to-end via WSS tunnel
NFR20: Tenant data isolation enforced at database query level — every query scoped by tenant ID
NFR21: Role permissions enforced server-side — client-side role checks are UI conveniences only
NFR22: No user can grant permissions at or above their own role level
NFR23: Each role has explicit read/write boundaries enforced at the API layer
NFR24: Every financial action permanently logged with actor, timestamp, and context — immutable
NFR25: Every Admin and Manager configuration change logged
NFR26: Audit logs retained per configured retention policy (default 7 years) in archive database
NFR27: Voided bills never deleted — retained with VOID stamp and sequential number
NFR28: CORS policy restricts API access to known application origins
NFR29: All API endpoints protected against common injection attacks (SQL injection, XSS, CSRF)
NFR30: Super-Admin access to platform admin panel logged with IP and timestamp
NFR31: Internet outage — zero billing interruption, IndexedDB offline mode activates within 500ms
NFR32: Browser crash — all active bill state recoverable on reload, zero re-entry required
NFR33: Server downtime — active bills on client devices survive independently; sync on reconnect
NFR34: Print agent offline — jobs queued on server; flushed on reconnect; Telegram alert within 60 seconds
NFR35: Data loss — zero, no bill, payment, or audit record lost under any failure scenario
NFR36: Daily backup — encrypted backup completes nightly; failure triggers Telegram alert to all owners
NFR37: Target uptime: 99.5% monthly (excluding planned maintenance windows)
NFR38: Planned maintenance: communicated to Admin via Telegram at least 24 hours in advance
NFR39: Recovery point objective (RPO): maximum 30 seconds of data loss (snapshot interval)
NFR40: Recovery time objective (RTO): system recoverable within 15 minutes of infrastructure failure
NFR41: Tenant isolation — each tenant's data fully isolated at database level, adding tenants has zero impact on existing tenant performance
NFR42: Horizontal scaling — application layer stateless, multiple instances deployable behind a load balancer; WebSocket connections handled by a dedicated real-time service
NFR43: Data volume — hot/archive split ensures live database size stays bounded regardless of historical bill volume
NFR44: Concurrent users per tenant — designed for up to 20 concurrent active sessions per tenant
NFR45: Multi-tenant growth — architecture supports 100+ tenants without infrastructure re-design
NFR46: Suggestion engine — scales independently, separate datastore, separate service, no coupling to billing performance
NFR47: Biller surface — full keyboard navigation; no mouse-only actions; `?` overlay for discoverability
NFR48: Kitchen Display — minimum 56px touch targets; minimum 18px font; high contrast for bright kitchen lighting
NFR49: Waiter Mode — minimum 44px touch targets; one-handed portrait usability
NFR50: Admin / Manager surface — WCAG AA contrast ratios; accessible form labels; responsive data tables
NFR51: All surfaces — system dark/light mode preference respected; no time-limited interactions without warning
NFR52: Telegram Bot API — reliable message delivery to group; graceful retry on API failure; no message loss for financial alerts
NFR53: Print Agent (WebSocket) — persistent WSS connection; auto-reconnect with job queue preservation; one-time token authentication
NFR54: Cloud Storage (Backup) — daily encrypted upload; S3-compatible API (AWS S3, Cloudflare R2)
NFR55: CSV Import/Export — standard UTF-8 CSV; consumable by Excel and Google Sheets without formatting issues
NFR56: TOTP — compatible with all standard authenticator apps (Google Authenticator, Authy, Microsoft Authenticator)

### Additional Requirements

#### From Architecture (Technical Constraints & Decisions)

**Starter Template / Project Setup (Epic 1 Story 1):**
- Frontend: React + Vite SPA (no SSR), Zustand (state), TanStack Query (server state), shadcn/ui + Tailwind CSS, React Router v7
- Backend: FastAPI (Python) with async support, SQLAlchemy async + Alembic migrations
- Database: PostgreSQL 16 with RLS and range partitioning
- Cache / Real-time store: Valkey (open-source Redis fork)
- Deployment: Docker + Docker Compose on Hetzner VPS, Dokploy self-hosted PaaS, Traefik SSL (Let's Encrypt)
- CI/CD: GitHub Actions → Dokploy webhook auto-deploy on push to main
- Makefile with canonical dev commands (make dev, make test-backend, make test-frontend, make migrate, make build-agent)
- Print Agent: Python + PyInstaller → .exe; NSSM as Windows Service; python-escpos for ESC/POS printing
- Monitoring: Sentry free tier (errors) + Uptime Kuma (uptime) from Day 1; Grafana/Loki/Prometheus deferred to Phase 2
- Offline storage: IndexedDB via idb library + Service Worker (Vite PWA plugin / Workbox)

**Infrastructure & Deployment:**
- Self-hosted on Hetzner VPS (CX31, ~€13/month)
- Nightly pg_dump backups encrypted with gpg → Cloudflare R2 (free tier, 10GB)
- 7-year minimum backup retention (GST compliance)
- Docker Compose dev override with hot reload for local development
- Role-specific PWA manifests (biller, kitchen, admin)

**Database & Schema:**
- Multi-tenancy: Row-level isolation via PostgreSQL RLS (not schema-per-tenant)
- Money stored as integer paise only (never float rupees)
- Dates stored as PostgreSQL TIMESTAMPTZ UTC; displayed as IST in frontend
- Append-only audit log tables (bill_events, audit_logs — no updates/deletes ever)
- Per-tenant PostgreSQL SEQUENCE for bill numbers: `tenant_{id}_bill_seq`
- Hot/archive split via pg_partman range partitions on closed_at date
- Valkey suggestion engine: separate instance, ZINCRBY sorted sets; async suggestion_worker.py
- Valkey-backed account lockout tracking

**Security Implementation:**
- Session tokens in httpOnly cookies (not localStorage — XSS-proof)
- IndexedDB financial fields encrypted via Web Crypto API; key derived from session token, held in memory only
- Print agent: one-time registration token (24hr) → permanent Agent API Key stored encrypted locally
- CORS restricted to known origins; no wildcard
- CSP, HSTS, X-Frame-Options headers via middleware
- SQLAlchemy ORM only (no raw SQL)
- Print agent local server binds to 127.0.0.1 only; Chrome Private Network Access header required

**Bill State Machine:**
- Single Document Model: Bill = KOT (no separate documents)
- Bill status flow: draft → kot_sent → partially_kot_sent → billed → void
- KOT item status: pending → sent → ready → voided
- Voids create NEW records — never modify existing ones

**API Design:**
- REST API with `/api/v1/` prefix; wrapped JSON envelope: `{ "data": {...}, "error": null }`
- WebSocket message envelope: `{ "type": "resource.action", "tenantId": "...", "payload": {...}, "ts": "ISO8601" }`
- Canonical WS event types: bill.*, menu.*, print.*, kitchen.*, session.*
- Auto-generated OpenAPI docs (FastAPI native)

**Code Quality:**
- Max 100 lines per file; split immediately on violation
- Backend: mypy --strict in CI; Ruff linting
- Frontend: TypeScript strict mode; no `any` type (ESLint error); feature-based folder structure; no cross-feature imports
- Testing: Unit tests (pytest / vitest), integration tests, E2E tests

**Print Agent Update Design:**
- Two-process model: launcher.exe (Windows Service) + agent.exe (updatable)
- Auto-update: SHA256-verified download; version check on startup + daily at 3am

#### From UX Design (Interaction & Presentation Constraints)

- Keyboard-first design: every primary action must have a keyboard shortcut; no mouse-only actions on Biller surface
- Single app shell: one URL base, role-driven sidebar controls what each role sees
- Command palette (Space bar) is the primary billing input — not a power-user feature
- `?` key overlay: displays all shortcuts in semi-transparent panel; must be available from Day 1
- Optimistic UI updates: item appears in bill instantly; server sync happens in background
- Async print queue: UI never waits for printer; print status indicator only
- Bill tabs (Chrome model): Ctrl+T new bill, Ctrl+W close, F1-F10 switch; active bills sidebar panel
- Keyboard shortcuts: Ctrl+K (fire KOT), Ctrl+B (payment panel), Ctrl+P (print/reprint), Ctrl+W (close bill)
- Layout: Fixed sidebar (240px) + bill tab area + active bills panel (280px) for Biller; full-width card grid for Kitchen
- Design system: shadcn/ui + Tailwind CSS; dark-first (zinc-950 background); configurable accent color per tenant
- Typography: Inter (UI) + JetBrains Mono (financial amounts, bill numbers)
- Kitchen Display: min 18px body, min 56px touch targets, high-contrast, visible from 1.5m
- Accessibility: WCAG AA contrast; visible focus rings; prefers-reduced-motion respected
- No modal dialogs for routine actions; no synchronous print blocking; no full-page navigation for subtasks
- Audio feedback for key events (item added, KOT sent, payment received)
- Biller onboarding checklist on first login; Telegram report on first EOD close

#### Configurability & Modularity (Cross-Cutting Constraint)

- **Feature flags per tenant**: Each major feature area (Waiter Mode, Suggestion Engine, Telegram, GST, Payroll/Rewards, Discount/Complimentary, Waiter transfer) must be individually toggleable per tenant via Admin settings — tenants only see and pay for what they use
- **Modular backend services**: Each domain (billing, kitchen, payments, print, menu, staff, expenses, analytics, telegram, auth, sync) implemented as an independent service module with no direct cross-module imports — modules communicate only via defined interfaces or events
- **Modular frontend features**: Frontend organized as self-contained feature modules (billing, kitchen, menu-management, staff, expenses, reports, settings) — each module owns its routes, state, components, and API calls; no cross-feature imports
- **Plugin-style print agent**: Print transport layer abstracted behind a common interface — USB, Network, Serial, and Windows queue transports are interchangeable plugins; adding a new transport requires no changes to the print queue logic
- **Configurable per-tenant settings**: Bill tab maximum (FR4), Telegram group, GST slabs, token slip template (FR78), reward formula (FR39), void approval rules (FR76), discount approval rules, session expiry duration, accent color — all configurable per tenant without code changes
- **Environment-driven configuration**: All infrastructure concerns (DB URL, Valkey URL, Telegram bot token, R2 credentials, Sentry DSN) resolved from environment variables — zero hardcoded config values in source code
- **Extensible role system**: Role definitions and permission boundaries stored in a configuration layer, not hardcoded — adding a new role or adjusting permissions does not require code changes to individual feature modules
- **Report builder modularity**: Analytics/reporting built as a composable query layer — adding a new report metric or chart type requires only a new query definition and renderer, not changes to the report framework
- **Suggestion engine as optional sidecar**: Suggestion engine (FR69, FR79, FR95) runs as a fully optional background service; disabling it has zero impact on billing functionality or performance

### FR Coverage Map

| FR | Epic | Description |
|---|---|---|
| FR1 | Epic 5 | Fuzzy search item add |
| FR2 | Epic 5 | Shortcode / numeric code item add |
| FR3 | Epic 5 | Command palette item add |
| FR4 | Epic 5 | Multi-tab bill management (configurable max) |
| FR5 | Epic 5 | F-key bill switching |
| FR6 | Epic 5 | Active bills sidebar panel |
| FR7 | Epic 5 | KOT fire (delta only) |
| FR8 | Epic 5 | Partial KOT fire |
| FR9 | Epic 5 | Void request by Biller |
| FR10 | Epic 5 | KOT-fired item lock |
| FR11 | Epic 12 | Waiter bill creation |
| FR12 | Epic 12 | Waiter-to-counter bill transfer |
| FR13 | Epic 5 | Immutable sequential bill numbers |
| FR14 | Epic 8 | Real-time KOT feed for kitchen |
| FR15 | Epic 8 | Mark individual item ready |
| FR16 | Epic 8 | Mark full order ready + Biller notification |
| FR17 | Epic 8 | Kitchen marks item unavailable |
| FR18 | Epic 8 | Delta-only KOT updates |
| FR19 | Epic 6 | Multi-method payment collection |
| FR21 | Epic 6 | Shift cash reconciliation + discrepancy detection |
| FR22 | Epic 5 | Amended bill audit flag |
| FR23 | Epic 6 | Complete bill audit history view |
| FR24 | Epic 7 | Async print queue (non-blocking) |
| FR25 | Epic 7 | Reprint closed bill via shortcut |
| FR26 | Epic 7 | Print agent offline queue + auto-flush |
| FR27 | Epic 7 | Print agent registration + Admin management |
| FR28 | Epic 3 | Inline menu item editing |
| FR29 | Epic 3 | CSV menu import/export with diff preview |
| FR30 | Epic 3 | Menu category/item reordering |
| FR31 | Epic 8 | Availability propagation within 3 seconds |
| FR32 | Epic 2 | Six-role RBAC system |
| FR33 | Epic 2 | PIN authentication for operational roles |
| FR34 | Epic 2 | Email + session auth for Admin/Super-Admin |
| FR35 | Epic 6 | Void approval workflow (Admin) |
| FR36 | Epic 6 | All financial actions tagged to authenticated user |
| FR37 | Epic 2 | Session auto-expiry (4hr) |
| FR38 | Epic 9 | Staff attendance recording per shift |
| FR39 | Epic 9 | Configurable reward formula |
| FR40 | Epic 9 | Auto-calculated staff rewards |
| FR41 | Epic 9 | Payroll summary view |
| FR42 | Epic 9 | Supplier invoice recording |
| FR43 | Epic 9 | Vendor/expense category directory |
| FR44 | Epic 9 | Expenses in EOD reports and analytics |
| FR45 | Epic 10 | Daily EOD Telegram report |
| FR46 | Epic 10 | Real-time financial alerts to Telegram |
| FR47 | Epic 10 | Daily backup confirmation to Telegram |
| FR48 | Epic 10 | Single group chat ID Telegram config |
| FR49 | Epic 11 | Live operations dashboard |
| FR50 | Epic 11 | Historical analytics |
| FR51 | Epic 3 | GST rate configuration per tenant |
| FR52 | Epic 11 | Bill GST exclusion with flagged audit record |
| FR53 | Epic 11 | Exportable GST report |
| FR54 | Epic 5 | Offline bill creation via IndexedDB |
| FR55 | Epic 5 | Auto-sync + server sequential number assignment |
| FR56 | Epic 5 | Crash recovery — full bill state restore |
| FR57 | Epic 3 | Super-Admin tenant provisioning |
| FR58 | Epic 3 | Super-Admin platform analytics (no tenant data) |
| FR59 | Epic 3 | Complete tenant data isolation (RLS) |
| FR60 | Epic 3 | Admin onboarding checklist |
| FR61 | Epic 5 | Keyboard shortcut overlay (`?` key) |
| FR62 | Epic 5 | "Right Now" time-of-day item section |
| FR63 | Epic 5 | Bill templates (preset item combos) |
| FR64 | Epic 5 | Concurrent edit lock indicator |
| FR65 | Epic 7 | Print agent one-time token authentication |
| FR66 | Epic 5 | Persistent offline mode indicator |
| FR67 | Epic 5 | Audio feedback for billing events |
| FR69 | Epic 12 | Co-order item suggestions (inline) |
| FR71 | Epic 12 | Waiter performance stats on login |
| FR72 | Epic 2 | Per-user display theme preference |
| FR73 | Epic 11 | Per-bill status timeline view |
| FR74 | Epic 2 | Admin: create/edit/deactivate/reset staff PINs |
| FR75 | Epic 3 | Table and section layout configuration |
| FR76 | Epic 5 | Discount / complimentary bill (with approval rules) |
| FR77 | Epic 6 | Formal shift open/close |
| FR78 | Epic 7 | Token slip print template configuration |
| FR79 | Epic 5 | Top-5 all-time + top-5 recent items in billing search |
| FR80 | Epic 11 | Bill history search (multi-filter) |
| FR81 | Epic 11 | Operational report export (CSV/PDF) |
| FR82 | Epic 6 | Post-collection payment method correction |
| FR83 | Epic 3 | Admin/Manager config change audit logging |
| FR84 | Epic 2 | Rate limiting + account lockout |
| FR85 | Epic 2 | Admin: immediate session invalidation for staff |
| FR86 | Epic 2 | Sensitive data encrypted at rest |
| FR87 | Epic 2 | No permission escalation above own role |
| FR88 | Epic 1 | WSS-only WebSocket connections |
| FR89 | Epic 2 | Role-scoped data visibility boundaries |
| FR90 | Epic 2 | Credential self-management + Super-Admin reset |
| FR92 | Epic 3 | Full tenant data archive export |
| FR93 | Epic 2 | TOTP 2FA for Admin/Super-Admin |
| FR94 | Epic 11 | Hot/archive 7-year retention architecture |
| FR95 | Epic 12 | Suggestion engine isolated datastore |

## Epic List

### Epic 1: Project Foundation & Infrastructure Setup
The development team can start building immediately with a production-ready scaffold, containerized infrastructure, CI/CD pipeline, feature flag system, modular folder architecture, and base security hardening — deployed to a live environment from day one.
**FRs covered:** FR88 + Architecture technical requirements
**Story sequencing convention (applies to ALL epics):** schema/migration → service layer → API endpoints → UI

### Epic 2: Authentication & Role-Based Access Control
All staff and admin roles can securely authenticate using the appropriate method for their role (PIN, email+password, TOTP); sessions are enforced with proper expiry; access is controlled server-side throughout; audit log schema is locked here and populated progressively across all future epics.
**FRs covered:** FR32, FR33, FR34, FR37, FR72, FR74, FR84, FR85, FR86, FR87, FR89, FR90, FR93

### Epic 3: Tenant Setup & Full Admin Configuration
Super-Admin can provision a new tenant with complete data isolation and per-tenant URL routing; the tenant's Admin is immediately able to configure everything needed to run the restaurant — menu, tables, GST, print templates, feature flags — before billing begins. All configuration changes are audit-logged.
**FRs covered:** FR28, FR29, FR30, FR51, FR57, FR58, FR59, FR60, FR75, FR83, FR92

### Epic 4: Core Billing Engine with Offline Resilience
Biller can complete the full bill lifecycle — open bill, add items via command palette/shortcodes/fuzzy search, fire KOT, apply discounts, and close the bill — entirely via keyboard. The app recovers instantly from crashes and continues working through internet outages with full IndexedDB sync on reconnect.
**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR8, FR9, FR10, FR13, FR22, FR54, FR55, FR56, FR61, FR62, FR63, FR64, FR66, FR67, FR76, FR79

### Epic 5: Payment, Cash & Void Management
Billers can collect payment across multiple methods; managers and admins can approve void requests with a full audit trail; shift cash sessions are opened, closed, and reconciled with automated discrepancy detection.
**FRs covered:** FR19, FR21, FR23, FR35, FR36, FR77, FR82

### Epic 6: Async Print System & Print Agent
The billing UI never waits for a printer. A locally installed print agent manages all print jobs asynchronously, queues them during offline periods, auto-flushes on reconnect, and is registered and monitored by Admin.
**FRs covered:** FR24, FR25, FR26, FR27, FR65, FR78

### Epic 7: Kitchen Display & Real-Time Operations
Kitchen staff can view all active KOTs in real time on their dedicated display, mark items and orders as ready, and control item availability — with changes propagating to all billing terminals within 3 seconds.
**FRs covered:** FR14, FR15, FR16, FR17, FR18, FR31

### Epic 8: Staff Management, Payroll & Expense Tracking
Managers and Admins can record staff attendance per shift, auto-calculate rewards/payroll via configurable formulas, view payroll summaries, and log supplier invoices — all feeding into financial reporting.
**FRs covered:** FR38, FR39, FR40, FR41, FR42, FR43, FR44

### Epic 9: Telegram Notifications & Intelligent Alerting
Admin receives real-time financial alerts (voids, cash discrepancies, printer offline) and a daily EOD report in their Telegram group automatically — configured with a single group chat ID. Zero manual reporting required.
**FRs covered:** FR45, FR46, FR47, FR48

### Epic 10: Analytics, Reporting & GST Compliance
Admin and Owner can view live operations, query historical analytics, search bill history, export operational reports, generate GST-compliant records, and rely on a 7-year hot/archive retention architecture.
**FRs covered:** FR49, FR50, FR52, FR53, FR73, FR80, FR81, FR94

### Epic 11: Waiter Mode *(Feature-flagged per tenant)*
Waiters can create and manage bills at the table on their own devices, view their own performance stats, and transfer finalized bills to the billing counter for payment collection.
**FRs covered:** FR11, FR12, FR71

### Epic 12: Smart Suggestions & Intelligent Features *(Feature-flagged per tenant)*
The billing engine proactively surfaces co-order suggestions and order frequency insights via a fully isolated suggestion engine that never contends with billing database performance.
**FRs covered:** FR69, FR95

---

## Epic 1: Project Foundation & Infrastructure Setup

The development team can start building immediately with a production-ready scaffold, containerized infrastructure, CI/CD pipeline, feature flag system, modular folder architecture, and base security hardening — deployed to a live environment from day one.

**Story sequencing convention (applies to ALL epics):** schema/migration → service layer → API endpoints → UI

### Story 1.1: Monorepo Scaffold & Docker Dev Environment

As a **developer**,
I want a fully configured monorepo with Docker Compose running both frontend and backend with hot reload,
So that the team can start writing features immediately with a consistent, reproducible local environment.

**Acceptance Criteria:**

**Given** the repo is cloned fresh
**When** `make dev` is run
**Then** the FastAPI backend starts with hot reload on port 8000, the React+Vite frontend starts on port 5173, PostgreSQL 16 starts on port 5432, and Valkey starts on port 6379
**And** the Makefile exposes: `make dev`, `make test-backend`, `make test-frontend`, `make migrate`, `make build-agent`
**And** the folder structure separates `backend/`, `frontend/`, `agent/` (print agent), `infra/` at the root
**And** backend uses Python 3.12+, FastAPI, SQLAlchemy async, Alembic; frontend uses React 18+, Vite, TypeScript strict mode, Tailwind CSS, shadcn/ui
**And** `docker-compose.dev.yml` overrides the base compose file for local dev (volumes, hot reload, no SSL)
**And** `README.md` documents the `make` commands and one-command setup

### Story 1.2: Database Migration Framework & Schema Conventions

As a **developer**,
I want Alembic migrations configured with naming conventions and a base schema locked,
So that all future stories have a consistent, predictable way to evolve the database schema.

**Acceptance Criteria:**

**Given** `make migrate` is run against a fresh PostgreSQL instance
**When** all existing migrations are applied
**Then** the database contains: `tenants`, `tenant_users`, `audit_logs` tables with correct column types
**And** all monetary columns use `INTEGER` (paise) — no `FLOAT` or `DECIMAL` for currency anywhere in the schema
**And** all timestamp columns use `TIMESTAMPTZ` (UTC) — no `TIMESTAMP WITHOUT TIME ZONE`
**And** table names are `snake_case` plural; column names `snake_case`; foreign keys `{singular_table}_id`; indexes `idx_{table}_{column}`
**And** `audit_logs` is append-only with a DB-level trigger that raises an exception on UPDATE or DELETE
**And** Alembic's `env.py` is configured for async SQLAlchemy and runs migrations in a transaction
**And** `make migrate` is idempotent — running it twice produces no errors

### Story 1.3: Backend Module Scaffold, API Baseline & Health Endpoint

As a **developer**,
I want a modular FastAPI backend with a working health endpoint, response envelope, and module structure,
So that all future backend stories have a consistent, importable pattern to build on.

**Acceptance Criteria:**

**Given** the backend is running
**When** `GET /api/v1/health` is called
**Then** it returns `{ "data": { "status": "ok", "version": "0.1.0" }, "error": null }` with HTTP 200
**And** all API responses use the envelope: `{ "data": {...}, "error": null }` or `{ "data": null, "error": { "code": "...", "message": "...", "details": {} } }`
**And** the backend folder structure has: `app/modules/{billing,kitchen,payment,print,menu,staff,expenses,analytics,telegram,auth,sync}/` — each with `router.py`, `service.py`, `models.py`, `schemas.py`
**And** modules do not import from each other directly — cross-module communication uses a shared `app/events/` bus or `app/db/` layer only
**And** OpenAPI docs are available at `/api/v1/docs` (FastAPI native)
**And** `mypy --strict` passes on the entire `app/` directory with zero errors
**And** Ruff linting passes with rules `E,F,I,UP` and `line-length=88`

### Story 1.4: Frontend Module Scaffold, PWA Config & Design System Bootstrap

As a **developer**,
I want a modular React frontend with Tailwind, shadcn/ui, the dark-first design token system, and PWA manifests configured,
So that all future frontend stories have a consistent component foundation and the app is installable from day one.

**Acceptance Criteria:**

**Given** the frontend is running
**When** the app is opened in a browser
**Then** the page renders with `zinc-950` background (`#09090b`), Inter font for UI text, and JetBrains Mono for any numeric/financial text
**And** design tokens are defined in `tailwind.config` as CSS custom properties: `--bg-base`, `--bg-surface`, `--bg-elevated`, `--border`, `--text-primary`, `--text-secondary`, `--accent` (default `violet-500`)
**And** the frontend folder structure has: `src/features/{billing,kitchen,menu-management,staff,expenses,reports,settings,auth}/` — each feature owns its own components, hooks, stores, and routes; no cross-feature imports (ESLint rule enforced)
**And** Vite PWA plugin (Workbox) is configured with three role-specific manifests: `biller.webmanifest`, `kitchen.webmanifest`, `admin.webmanifest`
**And** TypeScript strict mode is on; `noImplicitAny: true`; `@typescript-eslint/no-explicit-any` is an ESLint error
**And** `prefers-reduced-motion` media query is globally respected — all transitions disabled when set
**And** the app shell renders an empty sidebar and main content area (no content yet — populated by auth epic)

### Story 1.5: CI/CD Pipeline & Production Deployment

As a **developer**,
I want GitHub Actions deploying to Dokploy on Hetzner automatically on every push to `main`, with SSL via Traefik,
So that every merged story is live in production within minutes and the team never manually deploys.

**Acceptance Criteria:**

**Given** a commit is pushed to `main`
**When** the GitHub Actions workflow runs
**Then** backend Docker image is built, tests run (`make test-backend`), and on success the Dokploy webhook triggers a redeploy
**And** frontend is built (`make test-frontend` + `vite build`) and deployed
**And** Traefik automatically provisions and renews a Let's Encrypt TLS certificate for the configured domain
**And** `https://` is the only accessible protocol — HTTP redirects to HTTPS (301)
**And** WSS is the only WebSocket protocol — plain WS connections are rejected at the Traefik level (FR88)
**And** `docker-compose.prod.yml` is separate from dev compose and contains no volume mounts or hot reload config
**And** the CI workflow completes in under 5 minutes for a standard build

### Story 1.6: Feature Flag Infrastructure

As an **Admin**,
I want per-tenant feature flags that can enable or disable major features without code changes,
So that tenants only have access to the features they need and the platform can ship features incrementally.

**Acceptance Criteria:**

**Given** a tenant exists in the database
**When** the backend processes any request
**Then** it can read the tenant's feature flags from Valkey via `get_feature_flags(tenant_id)` returning a typed dict
**And** the flags schema includes: `waiter_mode`, `suggestion_engine`, `telegram_alerts`, `gst_module`, `payroll_rewards`, `discount_complimentary`, `waiter_transfer` — all `bool`, defaulting to `False`
**And** flags are cached in Valkey with a 60-second TTL; cache miss falls back to the `tenant_feature_flags` PostgreSQL table
**And** the frontend reads flags from `GET /api/v1/tenants/{id}/features` on app load and stores them in a Zustand `featureFlagStore`
**And** a `useFeatureFlag('waiter_mode')` hook returns `true/false` and any component wrapped in `<FeatureGate flag="waiter_mode">` renders only when the flag is enabled
**And** toggling a flag in the database takes effect within 60 seconds with no deployment required

### Story 1.7: Base Security Hardening & Observability Setup

As a **platform operator**,
I want security headers, CORS policy, Sentry error tracking, and Uptime Kuma monitoring active from day one,
So that the app is secure by default and any production error is captured immediately.

**Acceptance Criteria:**

**Given** the production app is running
**When** any HTTP response is returned
**Then** the following headers are present: `Strict-Transport-Security: max-age=31536000; includeSubDomains`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Content-Security-Policy` (restrictive default)
**And** CORS allows only the configured application origin — no wildcard `*` origins permitted
**And** Sentry SDK is initialized in both backend (Python) and frontend (TypeScript) using DSN from environment variables — unhandled exceptions are captured with no PII in payloads
**And** Uptime Kuma is deployed and monitoring `/api/v1/health` with a 60-second check interval, alerting via Telegram on downtime
**And** all secrets (DB URL, Valkey URL, Sentry DSN, domain names) are read from environment variables — zero hardcoded values in source code
**And** `make test-backend` runs `mypy --strict` and `ruff check` as part of the test suite — either failure fails the CI build

---

## Epic 2: Authentication & Role-Based Access Control

All staff and admin roles can securely authenticate using the appropriate method for their role; sessions are enforced with proper expiry; access is controlled server-side throughout; audit log schema is locked here and populated progressively across all future epics.

### Story 2.1: Role & Permission Schema + Server-Side RBAC Middleware

As a **developer**,
I want the six-role schema defined and RBAC middleware enforced at the API layer,
So that every future endpoint can declare its required role and the server rejects unauthorized requests — never trusting the client.

**Acceptance Criteria:**

**Given** the migration runs
**When** the roles table is queried
**Then** six roles exist: `biller`, `waiter`, `kitchen_staff`, `manager`, `admin`, `super_admin` — with explicit permission sets stored in a `role_permissions` config (not hardcoded per endpoint)
**And** a `require_role(*roles)` FastAPI dependency raises HTTP 403 if the authenticated user's role is not in the allowed list
**And** role checks are enforced server-side on every protected endpoint — client-side role state is decorative only
**And** no user can be assigned a role equal to or higher than the assigning user's own role (FR87)
**And** each role has explicitly defined data visibility boundaries enforced at the query layer (FR89): Billers scoped to their session, Managers scoped to their tenant's staff data, Admins scoped to their full tenant

### Story 2.2: PIN Authentication for Operational Roles

As a **Biller, Waiter, Kitchen Staff, or Manager**,
I want to authenticate with my PIN and receive a short-lived session token,
So that I can access my role's features quickly without a full login flow, and every action I take is tagged to my identity.

**Acceptance Criteria:**

**Given** a valid PIN is submitted to `POST /api/v1/auth/pin`
**When** the PIN matches a `tenant_users` record for the correct tenant
**Then** a short-lived JWT (4-hour expiry) is returned in an `httpOnly` cookie — never in a response body or localStorage
**And** the JWT payload contains: `user_id`, `tenant_id`, `role`, `iat`, `exp`
**And** `POST /api/v1/auth/pin` is rate-limited to 5 attempts per minute per IP via slowapi; after 5 failures the account is locked in Valkey and returns HTTP 429 (FR84)
**And** a locked account requires Admin reset before it can authenticate again
**And** all sessions auto-expire after 4 hours of inactivity (FR37)
**And** sensitive data (financial records) is encrypted at rest in PostgreSQL using pgcrypto for applicable columns (FR86)

### Story 2.3: Admin & Super-Admin Email + TOTP Authentication

As an **Admin or Super-Admin**,
I want to authenticate with email, password, and TOTP, and have my session auto-invalidated on browser close,
So that privileged access requires multi-factor verification and shared devices cannot be left logged in.

**Acceptance Criteria:**

**Given** valid email, password, and TOTP code are submitted to `POST /api/v1/auth/admin`
**When** all three factors are verified
**Then** a short-lived JWT (4-hour expiry) is returned in an `httpOnly` cookie with `SameSite=Strict`
**And** the TOTP implementation uses `pyotp` and is compatible with Google Authenticator, Authy, and Microsoft Authenticator (FR93, NFR56)
**And** `GET /api/v1/auth/totp/setup` returns a provisioning URI and QR code seed for initial TOTP enrollment
**And** the session cookie has `Secure` and `HttpOnly` flags; it is NOT set as persistent — browser close invalidates it for Admin roles (FR34)
**And** rate limiting applies identically to Admin login: 5 attempts per minute, lockout after 5 failures, email-based unlock (FR84)
**And** Super-Admin logins are additionally logged with IP address and timestamp (NFR30)

### Story 2.4: Staff PIN Management (Admin)

As an **Admin**,
I want to create, edit, deactivate, and reset PINs for all staff accounts in my tenant,
So that I have full control over who can access the system and can immediately revoke access when needed.

**Acceptance Criteria:**

**Given** an authenticated Admin makes a request to `POST /api/v1/staff`
**When** a new staff member is created with name, role, and PIN
**Then** the PIN is hashed (bcrypt) before storage — plaintext PIN is never persisted
**And** `PATCH /api/v1/staff/{id}/pin` allows PIN reset; `PATCH /api/v1/staff/{id}/deactivate` blocks login immediately
**And** `DELETE /api/v1/staff/{id}/sessions` immediately invalidates all active sessions for that staff member across all devices (FR85)
**And** Admin cannot create or modify staff with a role equal to or higher than their own (FR87)
**And** all PIN management actions are written to `audit_logs` with `actor_id`, `action`, `target_id`, and `created_at`
**And** the frontend renders a staff management table in `src/features/auth/` with create/edit/deactivate actions — accessible only to Admin and Super-Admin roles

### Story 2.5: Session Management & Credential Self-Service

As any **authenticated user**,
I want my session to auto-expire after inactivity, and as an Admin I want to manage my own credentials,
So that stale sessions don't remain active and I can maintain my own account security.

**Acceptance Criteria:**

**Given** a session JWT is 4 hours old with no activity
**When** the next request is made with that token
**Then** the server returns HTTP 401 and the frontend clears the session cookie and redirects to login
**And** `POST /api/v1/auth/logout` clears the httpOnly cookie and invalidates the token in Valkey's blocklist
**And** `PATCH /api/v1/auth/credentials` allows Admin and Super-Admin to change their own email or password (FR90)
**And** `POST /api/v1/auth/admin-reset/{id}` allows Super-Admin to reset any Admin's credentials (FR90)
**And** the login screen detects role from the submitted credentials and routes to the correct authenticated surface (Biller → billing screen, Kitchen → KOT display, Admin → admin panel)

### Story 2.6: Per-User Display Theme Preference

As any **authenticated user**,
I want to set my display theme (dark / high-contrast / light),
So that I can work comfortably across different lighting environments.

**Acceptance Criteria:**

**Given** an authenticated user opens their profile settings
**When** they select a theme preference
**Then** `PATCH /api/v1/users/me/preferences` persists `{ "theme": "dark" | "high_contrast" | "light" }` to `tenant_users.preferences` JSONB column
**And** on next login the stored theme is applied before the first render — no flash of wrong theme
**And** `prefers-color-scheme` system preference is the default when no stored preference exists
**And** theme switching applies instantly without a page reload via a `data-theme` attribute on `<html>` mapped to Tailwind's dark mode class strategy

---

## Epic 3: Tenant Setup & Full Admin Configuration

Super-Admin can provision a new tenant with complete data isolation and per-tenant URL routing; the tenant's Admin is immediately able to configure everything needed to run the restaurant — menu, tables, GST, print templates, feature flags — before billing begins. All configuration changes are audit-logged.

### Story 3.1: Tenant Provisioning & Data Isolation (Super-Admin)

As a **Super-Admin**,
I want to provision a new tenant with isolated data and a dedicated Admin account,
So that each restaurant operates in a completely separate data environment with no risk of cross-tenant data leakage.

**Acceptance Criteria:**

**Given** Super-Admin calls `POST /api/v1/super-admin/tenants`
**When** the request includes `{ name, subdomain, admin_email, admin_password }`
**Then** a new tenant record is created with a unique `tenant_id` (UUID)
**And** PostgreSQL Row-Level Security (RLS) policies are activated for the tenant — every query on `bills`, `bill_items`, `menu_items`, `staff`, `expenses`, `audit_logs` is automatically scoped by `tenant_id`
**And** a per-tenant bill number SEQUENCE is created: `tenant_{id}_bill_seq`
**And** the Admin account is created with TOTP enrollment pending — Admin receives an email with setup link
**And** `GET /api/v1/super-admin/stats` returns aggregate platform analytics (total tenants, total bills processed) without exposing any individual tenant's data (FR58)
**And** adding a new tenant has zero impact on existing tenants' query performance (NFR41)

### Story 3.2: Admin Onboarding Checklist

As a **new Admin**,
I want a guided onboarding checklist on first login,
So that I know exactly what to configure before the restaurant goes live and nothing is missed.

**Acceptance Criteria:**

**Given** an Admin logs in for the first time (tenant `onboarding_completed = false`)
**When** the admin dashboard loads
**Then** an onboarding checklist is displayed with steps: Add menu items, Configure tables, Set GST rates, Configure print template, Register print agent, Add staff PINs, Configure Telegram (if flag enabled)
**And** each checklist item shows completion status — green tick when done, pending indicator otherwise
**And** clicking any checklist item navigates directly to the relevant configuration screen
**And** the checklist is dismissible once all required steps are complete; `tenant.onboarding_completed` is set to `true`
**And** the checklist is accessible again from Settings after dismissal (FR60)

### Story 3.3: Menu Item Management

As an **Admin**,
I want to manage menu items via an inline table-editing interface,
So that the menu can be kept accurate without navigating away from the management screen.

**Acceptance Criteria:**

**Given** an authenticated Admin navigates to Menu Management
**When** they click "Add Item" or inline-edit an existing row
**Then** `POST /api/v1/menu/items` or `PATCH /api/v1/menu/items/{id}` persists: `name`, `category`, `price_paise` (integer), `shortcode`, `gst_category_id`, `is_available`, `display_order`
**And** price is stored as integer paise; the UI displays as `₹{paise/100}` formatted to 2 decimal places
**And** shortcodes are validated unique within the tenant and uppercased automatically
**And** `PATCH /api/v1/menu/categories` allows reordering categories; `PATCH /api/v1/menu/items/{id}/order` allows item reordering within a category (FR30)
**And** all menu changes are written to `audit_logs` with actor, action, and before/after values (FR83)
**And** the menu management table supports inline editing with keyboard navigation (Tab between fields, Enter to save)

### Story 3.4: Menu CSV Import & Export

As an **Admin**,
I want to bulk import and export the menu as a CSV file with a diff preview before applying,
So that I can set up or migrate a large menu quickly without manual data entry.

**Acceptance Criteria:**

**Given** an Admin uploads a CSV file to `POST /api/v1/menu/import`
**When** the file is parsed
**Then** the API returns a diff preview: `{ added: [...], modified: [...], removed: [...] }` — no changes are applied yet
**And** `POST /api/v1/menu/import/confirm` applies the confirmed diff atomically in a single transaction
**And** CSV columns are: `name`, `category`, `price`, `shortcode`, `gst_category`, `available` — UTF-8 encoding, compatible with Excel and Google Sheets (NFR55)
**And** `GET /api/v1/menu/export` returns the current menu as a downloadable UTF-8 CSV (FR29)
**And** import errors (duplicate shortcode, invalid price) are returned per-row with line numbers — partial imports are rejected entirely

### Story 3.5: Table & Section Layout Configuration

As an **Admin**,
I want to configure the restaurant's table and section layout,
So that Billers can assign bills to specific tables and sections during service.

**Acceptance Criteria:**

**Given** an authenticated Admin navigates to Table Configuration
**When** they create a section with tables
**Then** `POST /api/v1/tables/sections` creates a section (e.g. "Ground Floor"); `POST /api/v1/tables` creates a table with `section_id`, `name`, `capacity`
**And** tables can be reordered within a section; sections can be reordered
**And** deactivated tables are hidden from the billing screen but retained in historical bill records
**And** table names are visible in the Biller's active bills sidebar panel (FR6) — populated in Epic 4

### Story 3.6: GST Rate Configuration

As an **Admin**,
I want to configure GST rates, slab structures, and applicable item categories for my tenant,
So that all bills are taxed correctly per the restaurant's GST registration and item types.

**Acceptance Criteria:**

**Given** an authenticated Admin navigates to GST Configuration
**When** they create a GST category
**Then** `POST /api/v1/gst/categories` persists: `name` (e.g. "5% Food"), `cgst_rate_bps` (basis points integer), `sgst_rate_bps` — rates stored as integers (500 = 5.00%)
**And** GST categories are assignable to menu items (linked in Story 3.3)
**And** `GET /api/v1/gst/categories` returns all categories for the tenant — used by the billing engine to compute tax per line item
**And** GST rate changes apply to new bills only — historical bills retain the rate at time of billing (snapshotted in `bill_items`)
**And** all GST config changes are written to `audit_logs` (FR83)

### Story 3.7: Print Template Configuration

As an **Admin**,
I want to configure the token slip print template for my tenant,
So that every printed receipt shows the correct restaurant name, fields, and branding.

**Acceptance Criteria:**

**Given** an authenticated Admin navigates to Print Settings
**When** they configure the template
**Then** `PATCH /api/v1/tenants/me/print-template` persists: `restaurant_name`, `header_line_1`, `header_line_2`, `show_gst_number`, `show_table`, `show_waiter`, `footer_message`
**And** a live preview renders the token slip layout (max 6 lines, no logos, no borders — thermal-optimised)
**And** the template is fetched by the print agent when generating ESC/POS output
**And** template changes take effect on the next print job with no agent restart required

### Story 3.8: Tenant Data Export & Feature Flag Admin UI

As an **Admin**,
I want to export a complete archive of my tenant's data and control which features are enabled,
So that I have full data portability and can activate only the features relevant to my restaurant.

**Acceptance Criteria:**

**Given** an authenticated Admin navigates to Settings
**When** they request a data export via `POST /api/v1/tenants/me/export`
**Then** a background job packages all tenant data (bills, staff, expenses, audit logs) as a ZIP archive and emails a download link when ready (FR92)
**And** the Settings screen displays toggles for all feature flags: Waiter Mode, Suggestion Engine, Telegram Alerts, GST Module, Payroll & Rewards, Discounts & Complimentary
**And** toggling a flag calls `PATCH /api/v1/tenants/me/features` and takes effect within 60 seconds (via Valkey TTL from Story 1.6)
**And** all feature flag changes are written to `audit_logs` with actor and timestamp (FR83)
**And** the tenant accent colour picker (8–10 curated WCAG AA-safe options) calls `PATCH /api/v1/tenants/me/theme` and re-themes the entire UI via `--accent` CSS custom property with no page reload

---

## Epic 4: Core Billing Engine with Offline Resilience

Biller can complete the full bill lifecycle — open bill, add items via command palette/shortcodes/fuzzy search, fire KOT, apply discounts, and close the bill — entirely via keyboard with no mouse required. The app recovers instantly from crashes and continues working through internet outages with full IndexedDB sync on reconnect.

### Story 4.1: Bill & Bill Item Schema + State Machine Service

As a **developer**,
I want the complete bill database schema and state machine service layer implemented,
So that all billing stories have a tested, immutable foundation to build on.

**Acceptance Criteria:**

**Given** the migration runs
**When** the `bills` and `bill_items` tables are queried
**Then** `bills` has: `id` (UUID), `tenant_id`, `bill_number` (NULL until closed), `status` ENUM (`draft|kot_sent|partially_kot_sent|billed|void`), `table_id`, `opened_by`, `opened_at`, `closed_at`
**And** `bill_items` has: `id`, `bill_id`, `tenant_id`, `menu_item_id`, `quantity`, `unit_price_paise` (snapshotted at add time), `gst_rate_bps` (snapshotted), `kot_status` ENUM (`pending|sent|ready|voided`), `void_requested_at`, `void_approved_by`
**And** `bill_events` is an append-only audit ledger: `id`, `bill_id`, `tenant_id`, `actor_id`, `event_type` ENUM, `payload` JSONB, `created_at` — with a DB trigger preventing UPDATE/DELETE
**And** `bill_create_service.py`, `bill_kot_service.py`, `bill_void_service.py`, `bill_sync_service.py` each stay under 100 lines
**And** the state machine enforces valid transitions only: `draft → kot_sent`, `draft → billed`, `kot_sent → partially_kot_sent`, `kot_sent → billed`, `* → void` (with audit)
**And** unit tests cover all valid and invalid state transitions with 100% branch coverage

### Story 4.2: Bill CRUD API Endpoints

As a **Biller**,
I want API endpoints to open, modify, and close bills,
So that the frontend billing engine has a complete, tested REST interface to build against.

**Acceptance Criteria:**

**Given** an authenticated Biller calls `POST /api/v1/bills`
**When** the request succeeds
**Then** a new bill in `draft` status is returned with a UUID — `bill_number` is NULL at this stage
**And** `POST /api/v1/bills/{id}/items` adds an item: validates `menu_item_id` belongs to the tenant, snapshots `unit_price_paise` and `gst_rate_bps` from the menu at add time
**And** `DELETE /api/v1/bills/{id}/items/{item_id}` removes a `pending` (pre-KOT) item only — `sent` items return HTTP 409
**And** `POST /api/v1/bills/{id}/kot` transitions applicable items to `sent`, writes a `kot_fired` event to `bill_events`, returns only the delta items (not full bill)
**And** `POST /api/v1/bills/{id}/close` assigns the next value from `tenant_{id}_bill_seq` as `bill_number`, transitions status to `billed`
**And** all endpoints enforce tenant isolation via RLS — cross-tenant bill access returns HTTP 404

### Story 4.3: IndexedDB Offline Layer & Service Worker

As a **Biller**,
I want the app to continue accepting bill creation and modification when the internet goes offline,
So that a network outage never interrupts service and no bill data is lost.

**Acceptance Criteria:**

**Given** the browser loses internet connectivity
**When** offline mode activates
**Then** activation happens within 500ms — a persistent amber offline indicator appears in the UI (FR66, NFR6)
**And** the Service Worker (Workbox) intercepts all `/api/v1/bills` and `/api/v1/menu` requests and serves from IndexedDB cache
**And** new bills created offline receive a provisional local UUID; `bill_number` remains NULL until server sync
**And** financial fields in IndexedDB (`unit_price_paise`, totals) are encrypted via Web Crypto API; the encryption key is derived from the session token and held in memory only — lost on logout
**And** when connectivity is restored, `SyncQueueFlusher` submits queued operations to `POST /api/v1/sync` in order; the server assigns canonical sequential bill numbers via `tenant_{id}_bill_seq`
**And** the menu snapshot in IndexedDB is refreshed on every successful reconnect and on app load

### Story 4.4: Crash Recovery — Active Bill State Restore

As a **Biller**,
I want all open bills to be fully restored after a browser crash or accidental tab close,
So that I never have to re-enter a bill and customers are never kept waiting while I reconstruct lost work.

**Acceptance Criteria:**

**Given** the browser crashes or the tab is force-closed with active open bills
**When** the Biller reopens the app and re-authenticates
**Then** all open bills are restored from IndexedDB with their exact state — items, quantities, KOT status, table assignment (FR56)
**And** a "Restored N bills from [time]" non-blocking toast is shown — no modal, no confirmation required
**And** a 30-second snapshot writes all active bill state to IndexedDB continuously while the app is open (NFR39)
**And** the httpOnly session cookie persists across browser crashes — the Biller re-authenticates with PIN only, not a full re-login
**And** after crash recovery, the encryption key is re-derived from the new session token and IndexedDB data is re-decrypted transparently

### Story 4.5: Command Palette — Item Search & Add

As a **Biller**,
I want to press Space to open the command palette, type a shortcode or partial name, and add items to the active bill instantly,
So that I can build a complete bill without touching the mouse, in under 15 seconds.

**Acceptance Criteria:**

**Given** the Biller is on the billing screen with an active bill
**When** they press Space
**Then** the command palette opens within 50ms — input is focused, ready to type
**And** typing a shortcode (`CF`) or partial name (`chick`) returns ranked results in under 100ms from first keystroke (NFR8) — search runs client-side against the IndexedDB menu snapshot
**And** results display: item name, shortcode, price, and availability status
**And** pressing Enter adds the top result to the bill instantly (optimistic UI — item appears before server confirms)
**And** quantity expression parsing works: `CF 2 BT 1` adds 2× Chicken Fried Rice and 1× Butter Tea in one input
**And** the top 5 all-time most-ordered items and top 5 recently added items in the current session are displayed above search results when the palette opens (FR79)
**And** unavailable items are shown greyed out and cannot be added
**And** the palette placeholder reads: `Type item name, shortcode, or "CF 2 BT 1"...`

### Story 4.6: Multi-Tab Bill Management & Active Bills Panel

As a **Biller**,
I want to manage up to 10 open bills simultaneously via browser-style tabs with F-key switching,
So that I can handle multiple tables concurrently without losing context or slowing down.

**Acceptance Criteria:**

**Given** the Biller is on the billing screen
**When** they press Ctrl+T
**Then** a new bill tab opens, a `POST /api/v1/bills` is called, and the command palette auto-focuses (FR4)
**And** F1–F10 switch instantly to the corresponding open bill tab — no loading state (FR5)
**And** Ctrl+W closes the active bill tab (only if bill is in `billed` or `void` status — otherwise a confirmation is shown)
**And** a fixed active-bills sidebar panel (280px) shows all open bills: table name, item count, time open, running total (FR6)
**And** the tab bar shows bill identifier and a status badge: amber for KOT pending, green for billed
**And** the maximum concurrent bills is read from the tenant's config (default 10, configurable by Admin per FR4)
**And** concurrent edit lock: if another user opens the same bill, a lock indicator shows their name and the bill becomes read-only for the second user (FR64)

### Story 4.7: KOT Fire & Partial KOT

As a **Biller**,
I want to fire a KOT with Ctrl+K, sending only new items to the kitchen,
So that the kitchen receives orders instantly without blocking my billing UI.

**Acceptance Criteria:**

**Given** the active bill has at least one item in `pending` KOT status
**When** the Biller presses Ctrl+K
**Then** a `POST /api/v1/bills/{id}/kot` is called — only `pending` items are transitioned to `sent`; already-sent items are unaffected (FR7, FR18)
**And** the KOT is dispatched to the kitchen WebSocket channel `kitchen.kot.fired` with the delta payload only
**And** the bill tab shows a subtle amber KOT badge and an audio tick plays (FR67)
**And** the UI never blocks — KOT dispatch is fire-and-forget; if the WebSocket is offline the KOT is queued in IndexedDB and sent on reconnect
**And** partial KOT: if the Biller selects specific items before pressing Ctrl+K, only those items are sent — remaining items stay `pending` (FR8)
**And** bill status transitions: `draft → kot_sent` on first KOT; `kot_sent → partially_kot_sent` when only some items are sent

### Story 4.8: Void Request by Biller

As a **Biller**,
I want to request a void for a KOT-fired item, which is then locked pending Admin approval,
So that I can flag mistakes without being able to unilaterally remove items that have already gone to the kitchen.

**Acceptance Criteria:**

**Given** a bill item is in `sent` or `ready` KOT status
**When** the Biller selects the item and requests a void
**Then** `POST /api/v1/bills/{id}/items/{item_id}/void-request` sets `void_requested_at` timestamp and writes a `void_requested` event to `bill_events`
**And** the item is visually marked as "Void Pending" in the bill — it cannot be re-ordered or modified
**And** the Biller cannot remove the item unilaterally — HTTP 409 is returned if they attempt a direct delete (FR10)
**And** a real-time WebSocket event `bill.void_requested` is broadcast to Admin/Manager sessions for the tenant
**And** the void request is queued as a Telegram alert stub — dispatched when Telegram is wired in Epic 9

### Story 4.9: Bill Templates, Discounts & Keyboard Shortcut Overlay

As a **Biller**,
I want to save bill templates, apply discounts, and access a keyboard shortcut overlay,
So that repeat orders are instant and I always know the keyboard shortcuts without asking for help.

**Acceptance Criteria:**

**Given** a Biller has an active bill with items
**When** they press the save-template shortcut
**Then** `POST /api/v1/bills/templates` saves the current item combination with a name; `GET /api/v1/bills/templates` lists saved templates; triggering a template adds all items to the active bill at once (FR63)
**And** discount: `PATCH /api/v1/bills/{id}/discount` accepts `{ type: "percent"|"flat"|"complimentary", value_paise, reason }` — if Admin approval is required (per feature flag config), the bill is locked until approved; if not required, discount is applied immediately (FR76)
**And** pressing `?` at any time renders a full-screen semi-transparent overlay listing all keyboard shortcuts grouped by category — closes on `Escape` or `?` again (FR61)
**And** all shortcuts are documented in the overlay: Space (palette), Ctrl+K (KOT), Ctrl+B (payment), Ctrl+P (print), Ctrl+T (new bill), Ctrl+W (close bill), F1–F10 (switch bill), `?` (this overlay)
**And** the "Right Now" section in the command palette shows items popular at the current time of day (hour-bucket query from Valkey) — displayed above main search results (FR62)

---

## Epic 5: Payment, Cash & Void Management

Billers can collect payment across multiple methods in a single transaction; managers and admins can approve void requests with a full audit trail; shift cash sessions are opened, closed, and reconciled with automated discrepancy detection.

### Story 5.1: Payment Schema & Shift Session Schema

As a **developer**,
I want the payment, shift session, and void approval tables defined with immutability constraints,
So that all financial records are fintech-grade from day one — nothing can be silently modified or deleted.

**Acceptance Criteria:**

**Given** the migration runs
**When** the payment tables are queried
**Then** `payments` has: `id` (UUID), `bill_id`, `tenant_id`, `method` ENUM (`cash|upi|card`), `amount_paise` (INTEGER), `collected_by`, `collected_at`, `correction_reason` (nullable), `corrected_by` (nullable), `corrected_at` (nullable)
**And** `shift_sessions` has: `id`, `tenant_id`, `opened_by`, `opened_at`, `closed_by`, `closed_at`, `opening_cash_paise`, `expected_cash_paise`, `actual_cash_paise`, `discrepancy_paise`, `status` ENUM (`open|closed`)
**And** `void_approvals` has: `id`, `bill_item_id`, `tenant_id`, `requested_by`, `requested_at`, `approved_by` (nullable), `rejected_by` (nullable), `resolved_at`, `reason`, `status` ENUM (`pending|approved|rejected`)
**And** a DB-level constraint prevents any `payments` row from being hard-deleted — soft deletes only via `correction_reason`
**And** all monetary values stored as INTEGER paise — no exceptions

### Story 5.2: Multi-Method Payment Collection API

As a **Biller**,
I want to collect payment split across cash, UPI, and card in a single transaction,
So that mixed-payment bills are settled accurately with every method recorded.

**Acceptance Criteria:**

**Given** an authenticated Biller calls `POST /api/v1/bills/{id}/payment`
**When** the request includes `{ methods: [{ method: "cash", amount_paise: 10000 }, { method: "upi", amount_paise: 5000 }] }`
**Then** each payment method is inserted as a separate `payments` row tagged with `collected_by` = authenticated user (FR36)
**And** the sum of all payment amounts must equal the bill total (including GST, minus discounts) — HTTP 422 if there is a mismatch
**And** on successful payment, the bill transitions to `billed` status and `bill_number` is assigned via `tenant_{id}_bill_seq`
**And** a `payment_collected` event is written to `bill_events` with the full payment breakdown
**And** `POST /api/v1/bills/{id}/payment/correct` allows correction of payment method post-collection: accepts `{ payment_id, new_method, reason }`, sets `correction_reason`, `corrected_by`, `corrected_at` — original record is never deleted (FR82)

### Story 5.3: Payment Collection UI (Ctrl+B)

As a **Biller**,
I want to press Ctrl+B to open the payment panel and collect payment without leaving the billing screen,
So that payment is a seamless continuation of the billing loop, not a navigation away.

**Acceptance Criteria:**

**Given** the Biller is on the billing screen with an active bill
**When** they press Ctrl+B
**Then** a payment panel slides in from the right — the bill total is pre-filled, cursor is in the cash amount field
**And** Tab moves between payment method fields (cash, UPI, card); the remaining balance updates in real time as amounts are entered
**And** pressing Enter on a fully-filled payment form submits and closes the bill — the bill tab closes, the next active bill is auto-focused
**And** an audio confirmation plays on successful payment (FR67)
**And** if a discount is pending approval, the payment panel shows the pending discount amount greyed out with "Awaiting approval" label
**And** the panel is keyboard-navigable end-to-end — no mouse required

### Story 5.4: Shift Open/Close & Cash Reconciliation

As a **Biller or Manager**,
I want to formally open and close my shift with a cash count, and have discrepancies flagged automatically,
So that cash accountability is enforced at every shift boundary without manual calculation.

**Acceptance Criteria:**

**Given** a Biller calls `POST /api/v1/shifts/open`
**When** the request includes `{ opening_cash_paise }`
**Then** a `shift_sessions` record is created in `open` status, tagged to the authenticated user (FR77)
**And** `POST /api/v1/shifts/close` accepts `{ actual_cash_paise }`, calculates `expected_cash_paise` (opening + all cash payments in session), sets `discrepancy_paise = actual - expected`
**And** if `discrepancy_paise != 0` a `cash_discrepancy` event is emitted — this triggers a Telegram alert stub (wired in Epic 9) (FR21)
**And** if `discrepancy_paise == 0` the shift closes silently — no confirmation modal, no friction for clean closes
**And** only one shift session can be open per user at a time — HTTP 409 if a second open is attempted
**And** `GET /api/v1/shifts/current` returns the active shift session for the authenticated user

### Story 5.5: Void Approval Workflow (Admin/Manager)

As an **Admin or Manager**,
I want to approve or reject Biller void requests in real time,
So that fraudulent or erroneous voids are controlled, fully traceable, and never happen without authorisation.

**Acceptance Criteria:**

**Given** a void request exists (from Story 4.8)
**When** an Admin calls `POST /api/v1/voids/{id}/approve`
**Then** the `void_approvals` record is updated: `approved_by`, `resolved_at`, `status = approved`
**And** the `bill_item.kot_status` transitions to `voided`; a `void_approved` event is written to `bill_events` with approver identity (FR35)
**And** `POST /api/v1/voids/{id}/reject` sets `status = rejected`; the item reverts to its previous KOT status; a `void_rejected` event is written
**And** voided items are retained in the bill with a strikethrough visual and `VOIDED` label — they are never deleted from the database (NFR27)
**And** `GET /api/v1/voids/pending` returns all pending void requests for the tenant — accessible to Admin and Manager roles only
**And** the Admin/Manager UI shows a real-time void request panel that updates via WebSocket event `bill.void_requested`

### Story 5.6: Bill Audit History View (Admin)

As an **Admin**,
I want to view the complete audit history of any bill,
So that I can investigate any dispute, discrepancy, or suspicious activity with a full immutable record.

**Acceptance Criteria:**

**Given** an authenticated Admin calls `GET /api/v1/bills/{id}/audit`
**When** the bill has a complete event history
**Then** all `bill_events` for the bill are returned in chronological order: `event_type`, `actor_id`, `actor_name`, `payload`, `created_at`
**And** the response includes: bill opened, items added/removed, KOT fired, payment collected, voids requested/approved/rejected, discounts applied, amendments
**And** the Admin UI renders a per-bill status timeline: opened → KOT sent → bill generated → payment collected — with actor name and timestamp at each step (FR73)
**And** the audit log is read-only — no Admin action can modify or delete any event record

---

## Epic 6: Async Print System & Print Agent

The billing UI never waits for a printer. A locally installed print agent manages all print jobs asynchronously, queues them during offline periods, auto-flushes on reconnect, and is registered and monitored by Admin.

### Story 6.1: Print Job Schema & Server-Side Print Queue

As a **developer**,
I want the print job queue persisted in PostgreSQL with at-least-once delivery guarantees,
So that no print job is ever silently dropped, even if the print agent disconnects mid-queue.

**Acceptance Criteria:**

**Given** the migration runs
**When** the `print_jobs` table is queried
**Then** it has: `id` (UUID), `tenant_id`, `bill_id`, `agent_id`, `status` ENUM (`queued|dispatched|printed|failed`), `payload` JSONB (ESC/POS data), `created_at`, `dispatched_at`, `printed_at`, `retry_count` (INTEGER, default 0)
**And** `print_agents` has: `id`, `tenant_id`, `name`, `registration_token_hash`, `api_key_hash`, `last_seen_at`, `status` ENUM (`online|offline`), `printer_config` JSONB
**And** `print_job_service.py` exposes: `enqueue(bill_id, tenant_id)` — generates ESC/POS payload from bill + print template, inserts a `queued` job
**And** jobs remain in `queued` status until an agent acknowledges receipt — `dispatched` on send, `printed` on agent confirmation
**And** failed jobs (retry_count ≥ 3) emit a `print.agent_offline` event — triggers Telegram alert stub (wired in Epic 9)

### Story 6.2: Print Agent Registration & Authentication

As an **Admin**,
I want to register a print agent using a one-time token and have it authenticate permanently thereafter,
So that only authorised agents can receive print jobs and I can revoke access at any time.

**Acceptance Criteria:**

**Given** Admin calls `POST /api/v1/print/agents/register-token`
**When** the token is generated
**Then** a 24-hour one-time registration token is returned and stored as a bcrypt hash in `print_agents.registration_token_hash` (FR65)
**And** the print agent exchanges the token via `POST /api/v1/print/agents/activate` — receives a permanent `agent_api_key` stored encrypted locally on the agent machine
**And** the registration token is single-use — a second activation attempt returns HTTP 410
**And** `DELETE /api/v1/print/agents/{id}` revokes the agent's API key immediately — subsequent WSS connections from that agent are rejected (FR27)
**And** Admin UI shows all registered agents with: name, status (online/offline), last seen timestamp, and a revoke button

### Story 6.3: Print Agent — Windows Service & ESC/POS Printing

As a **restaurant operator**,
I want a locally installed Windows print agent that receives jobs via WSS and prints to any connected thermal printer,
So that printing works with USB, network, or serial printers without any browser plugin or driver configuration.

**Acceptance Criteria:**

**Given** the print agent is installed as a Windows Service via NSSM
**When** it starts
**Then** it establishes a persistent outbound WSS connection to the cloud server authenticated with its `agent_api_key` (NFR19)
**And** it listens for `print.job` WebSocket messages containing ESC/POS payload and printer config
**And** it supports printer transports: USB (vendor_id + product_id), Network (IP + port), Serial/COM port — transport selected from `printer_config` JSONB
**And** on receiving a job it prints via `python-escpos`, sends a `print.job.confirmed` acknowledgement, and updates `print_jobs.status = printed`
**And** if the printer is unavailable it retries up to 3 times with 5-second backoff before marking the job `failed`
**And** the agent maintains a local job queue (SQLite) — jobs survive agent restart and are replayed on reconnect (FR26)
**And** `launcher.exe` checks the version endpoint on startup and daily at 3am; downloads and SHA256-verifies a new `agent.exe` if available

### Story 6.4: Async Print Trigger & Reprint

As a **Biller**,
I want print jobs to be fired automatically on bill close and reprinted on demand via Ctrl+P, without the UI ever waiting for the printer,
So that a paper jam or offline printer never blocks billing.

**Acceptance Criteria:**

**Given** a bill is successfully closed (payment collected, `billed` status)
**When** the close API responds
**Then** `print_job_service.enqueue()` is called immediately — the print job is created and dispatched to the agent asynchronously; the billing UI does not wait (FR24)
**And** a small print status indicator in the corner shows: queued → printing → done (or failed) — updates via WebSocket `print.*` events
**And** pressing Ctrl+P on any closed bill in the billing screen or history calls `POST /api/v1/print/jobs` with the bill ID — a new print job is enqueued immediately (FR25)
**And** if no print agent is online, the job is queued in `print_jobs` with `queued` status and dispatched automatically when the agent reconnects — no manual intervention required (FR26, NFR7)
**And** the UI never shows a blocking spinner waiting for print confirmation — print is always fire-and-forget

---

## Epic 7: Kitchen Display & Real-Time Operations

Kitchen staff can view all active KOTs in real time on their dedicated display, mark items and orders as ready, and control item availability — with changes propagating to all billing terminals within 3 seconds.

### Story 7.1: WebSocket Real-Time Infrastructure & Kitchen Schema

As a **developer**,
I want a dedicated WebSocket service handling real-time pub/sub for kitchen and billing events,
So that all terminals receive updates within 3 seconds without polling and without coupling the real-time layer to the REST API server.

**Acceptance Criteria:**

**Given** the WebSocket service is running
**When** a `kitchen.kot.fired` event is published for a tenant
**Then** all connected Kitchen Display clients for that tenant receive the message within 3 seconds (NFR3)
**And** the WebSocket service is stateless — connection state stored in Valkey pub/sub channels keyed by `tenant_id`
**And** all WebSocket messages use the envelope: `{ "type": "resource.action", "tenantId": "...", "payload": {...}, "ts": "ISO8601" }`
**And** canonical event types implemented: `kitchen.kot.fired`, `kitchen.item.ready`, `kitchen.item.unavailable`, `bill.void_requested`, `menu.availability.changed`, `print.job.*`
**And** the WebSocket service enforces tenant isolation — a client subscribed to tenant A never receives tenant B events
**And** WebSocket connections use WSS only; reconnect with exponential backoff: 1s → 2s → 4s → max 30s (NFR9)

### Story 7.2: KOT Feed API & Kitchen Display UI

As a **Kitchen Staff member**,
I want to see all active KOTs in real time on a large-card display,
So that I always know exactly what needs to be prepared without checking with the billing counter.

**Acceptance Criteria:**

**Given** an authenticated Kitchen Staff member opens the kitchen display
**When** the page loads
**Then** `GET /api/v1/kitchen/kots` returns all active KOTs for the tenant with items in `sent` or `partially_sent` status, ordered by `kot_fired_at` ascending (oldest first) (FR14)
**And** the UI renders KOT cards in a responsive grid: 2 columns on tablet, 3 on desktop — each card shows table, items, quantities, and time elapsed
**And** font size is minimum 18px for item names; touch targets minimum 56px (NFR48)
**And** new KOTs appear in real time via `kitchen.kot.fired` WebSocket event — no page refresh required
**And** when a KOT is updated (item added via partial KOT), only the delta items are appended to the existing card — the card does not re-render from scratch (FR18)
**And** the kitchen display uses the `kitchen.webmanifest` PWA manifest and is installable as a standalone app on tablets

### Story 7.3: Mark Items & Orders Ready

As a **Kitchen Staff member**,
I want to mark individual items or a full order as ready,
So that Billers are notified immediately when food is ready to serve.

**Acceptance Criteria:**

**Given** a KOT card is displayed on the kitchen screen
**When** Kitchen Staff taps an individual item's ready button
**Then** `PATCH /api/v1/kitchen/items/{bill_item_id}/ready` transitions `bill_items.kot_status` to `ready` (FR15)
**And** the item is visually marked as ready on the KOT card (strikethrough or green tick) across all connected kitchen displays via WebSocket
**And** when all items on a KOT are marked ready, `PATCH /api/v1/kitchen/kots/{bill_id}/ready` marks the full order ready (FR16)
**And** on full order ready, a `kitchen.order.ready` WebSocket event is sent to Biller sessions — the corresponding bill tab flashes a green "Ready" badge
**And** a completed KOT card is visually distinguished (dimmed/moved to bottom) but remains visible until the bill is closed

### Story 7.4: Item Availability Control & Real-Time Propagation

As a **Kitchen Staff member or Admin**,
I want to mark menu items as unavailable and have that propagate to all billing terminals instantly,
So that Billers never add an item to a bill that the kitchen cannot fulfil.

**Acceptance Criteria:**

**Given** Kitchen Staff taps an item's availability toggle on the kitchen display
**When** `PATCH /api/v1/menu/items/{id}/availability` is called with `{ is_available: false }`
**Then** the change is persisted and a `menu.availability.changed` WebSocket event is broadcast to all Biller sessions for the tenant (FR17, FR31)
**And** within 3 seconds, all connected billing terminals show the item greyed out in the command palette — it cannot be added to any bill (NFR3)
**And** the IndexedDB menu snapshot on each client is updated immediately on receiving the WebSocket event — no page reload required
**And** re-enabling an item follows the same flow: `{ is_available: true }` broadcasts `menu.availability.changed` and the item reappears as available within 3 seconds
**And** availability changes made by Admin (Story 3.3) use the same propagation path — single code path for all availability changes

---

## Epic 8: Staff Management, Payroll & Expense Tracking

Managers and Admins can record staff attendance per shift, auto-calculate rewards/payroll via configurable formulas, view payroll summaries, and log supplier invoices — all feeding into financial reporting.

### Story 8.1: Staff, Attendance & Expense Schema

As a **developer**,
I want the staff attendance, payroll, supplier invoice, and vendor directory tables defined,
So that all payroll and expense stories have a clean, queryable foundation.

**Acceptance Criteria:**

**Given** the migration runs
**When** the staff management tables are queried
**Then** `staff_attendance` has: `id`, `tenant_id`, `user_id`, `shift_session_id`, `shift_date`, `shift_type` (configurable), `recorded_by`, `created_at`
**And** `reward_formulas` has: `id`, `tenant_id`, `name`, `type` ENUM (`percent|flat|hybrid|custom`), `config` JSONB, `is_active`
**And** `payroll_entries` has: `id`, `tenant_id`, `user_id`, `period_start`, `period_end`, `bills_handled`, `total_billed_paise`, `reward_paise`, `formula_snapshot` JSONB, `created_at`
**And** `suppliers` has: `id`, `tenant_id`, `name`, `category_id`, `contact`, `is_active`
**And** `expense_categories` has: `id`, `tenant_id`, `name`, `is_active`
**And** `supplier_invoices` has: `id`, `tenant_id`, `supplier_id`, `category_id`, `amount_paise` (INTEGER), `invoice_date`, `payment_method` ENUM (`cash|upi|card|credit`), `notes`, `recorded_by`, `created_at`
**And** all monetary columns are INTEGER paise — no exceptions

### Story 8.2: Attendance Recording & Reward Formula Configuration

As a **Manager or Admin**,
I want to record staff attendance per shift and configure how rewards are calculated,
So that payroll is always based on accurate attendance and a formula the restaurant controls.

**Acceptance Criteria:**

**Given** an authenticated Manager calls `POST /api/v1/attendance`
**When** the request includes `{ user_id, shift_date, shift_type }`
**Then** an `staff_attendance` record is created linked to the current open `shift_session_id` (FR38)
**And** `GET /api/v1/attendance?date=YYYY-MM-DD` returns all attendance records for the tenant on that date — accessible to Manager and Admin
**And** `POST /api/v1/reward-formulas` creates a formula: type `percent`, `flat`, `hybrid`, or `custom` JSONB (FR39)
**And** only one formula can be `is_active = true` per tenant at a time — activating a new formula deactivates the previous one
**And** formula changes are written to `audit_logs` with the before/after config snapshot

### Story 8.3: Payroll Calculation & Summary View

As a **Manager or Admin**,
I want the system to auto-calculate each staff member's earned rewards and show a payroll summary,
So that I never manually compute payroll and can review it before processing payment.

**Acceptance Criteria:**

**Given** a shift session is closed
**When** `POST /api/v1/payroll/calculate` is called with `{ period_start, period_end }`
**Then** for each staff member with attendance in the period: bills handled, total value billed (paise), and reward amount (paise) are calculated using the active `reward_formula` (FR40)
**And** the formula config is snapshotted into `payroll_entries.formula_snapshot` — historical payroll is never affected by future formula changes
**And** `GET /api/v1/payroll/summary?period_start=...&period_end=...` returns per-staff: name, shifts attended, bills handled, total billed, payout — accessible to Manager and Admin (FR41)
**And** the Admin UI renders the payroll summary as a sortable data table with totals row
**And** payroll entries are read-only once created — corrections require a new entry with a note, not an edit

### Story 8.4: Waiter Performance Stats

As a **Waiter**,
I want to see my own performance stats on login,
So that I can track my productivity and feel accountable for my shift's output.

**Acceptance Criteria:**

**Given** an authenticated Waiter opens their dashboard
**When** `GET /api/v1/staff/me/stats` is called
**Then** it returns: bills served today, total value billed today, shift summary (start time, duration), and comparison to yesterday (FR71)
**And** a Waiter can only see their own stats — cross-staff data returns HTTP 403
**And** the stats page is accessible from the Waiter's role-driven sidebar without navigating away from the billing surface

### Story 8.5: Supplier & Vendor Directory Management

As a **Manager or Admin**,
I want to maintain a vendor directory and record supplier invoices,
So that all business expenses are tracked alongside revenue for complete financial visibility.

**Acceptance Criteria:**

**Given** an authenticated Admin navigates to Expenses
**When** they create a supplier
**Then** `POST /api/v1/suppliers` creates a record with `name`, `category_id`, `contact` (FR43)
**And** `POST /api/v1/expense-categories` creates a configurable category (e.g. "Vegetables", "Electricity", "Maintenance")
**And** `POST /api/v1/invoices` records a supplier invoice: `supplier_id`, `category_id`, `amount_paise`, `invoice_date`, `payment_method`, `notes` — `recorded_by` auto-set from session (FR42)
**And** `GET /api/v1/invoices?date_from=...&date_to=...` returns all invoices for the period — accessible to Manager and Admin
**And** all invoice data is included in the EOD Telegram report event payload (FR44) — dispatched when Telegram is wired in Epic 9
**And** invoice amounts appear in the analytics expense vs revenue comparison — populated when analytics are wired in Epic 10

---

## Epic 9: Telegram Notifications & Intelligent Alerting

Admin receives real-time financial alerts (voids, cash discrepancies, printer offline) and a daily EOD report in their Telegram group automatically — configured with a single group chat ID. Zero manual reporting required.

### Story 9.1: Telegram Alert Queue Schema & Worker Infrastructure

As a **developer**,
I want a Postgres-backed Telegram alert queue with an async worker processing at-least-once delivery,
So that no financial alert is ever silently dropped, even if the Telegram API is temporarily unavailable.

**Acceptance Criteria:**

**Given** the migration runs
**When** the `telegram_alerts` table is queried
**Then** it has: `id` (UUID), `tenant_id`, `alert_type` ENUM (`void_request|cash_discrepancy|printer_offline|eod_report|backup_confirmation|large_cash_payment`), `payload` JSONB, `status` ENUM (`queued|sent|failed`), `retry_count` (INTEGER default 0), `created_at`, `sent_at`, `error_message`
**And** `telegram_config` has: `tenant_id` (PK), `bot_token_encrypted`, `group_chat_id`, `large_cash_threshold_paise`, `eod_report_time` (TIME), `is_active`
**And** `telegram_worker.py` polls `telegram_alerts` every 10 seconds for `queued` or `failed` (retry_count < 3) records and dispatches via the Telegram Bot API
**And** on successful send: `status = sent`, `sent_at = now()`; on failure: `retry_count++`; after 3 failures: `status = failed` — no further retries without manual intervention
**And** the worker runs as a separate long-running process in its own Docker container — not inside the FastAPI process

### Story 9.2: Telegram Integration Configuration (Admin)

As an **Admin**,
I want to connect my Telegram group to the platform with a single group chat ID,
So that all alerts and reports are delivered to my team without any per-alert configuration.

**Acceptance Criteria:**

**Given** an authenticated Admin navigates to Telegram Settings (visible only when `telegram_alerts` feature flag is enabled)
**When** they submit `{ group_chat_id, large_cash_threshold_paise, eod_report_time }`
**Then** `PATCH /api/v1/tenants/me/telegram` stores the config with `bot_token_encrypted` (platform bot token, not per-tenant) (FR48)
**And** `POST /api/v1/tenants/me/telegram/test` sends a test message to the configured group — Admin sees success/failure confirmation in the UI
**And** `large_cash_threshold_paise` defaults to 50000 (₹500) — configurable per tenant
**And** `eod_report_time` defaults to `23:00` IST — configurable per tenant
**And** disabling the `telegram_alerts` feature flag immediately stops all alert delivery without deleting the config

### Story 9.3: Real-Time Financial Alerts

As an **Admin**,
I want to receive instant Telegram alerts for void requests, large cash payments, cash discrepancies, and printer going offline,
So that I'm aware of critical events as they happen — even when I'm not looking at the dashboard.

**Acceptance Criteria:**

**Given** the Telegram config is active for a tenant
**When** a void request is submitted (Story 4.8)
**Then** a `void_request` alert is enqueued in `telegram_alerts` with payload: bill number, item name, requester name, timestamp (FR46)
**And** when a cash payment exceeds `large_cash_threshold_paise`, a `large_cash_payment` alert is enqueued with: bill number, amount, Biller name
**And** when a shift closes with `discrepancy_paise != 0` (Story 5.4), a `cash_discrepancy` alert is enqueued with: discrepancy amount, shift owner, expected vs actual
**And** when a print agent goes offline (Story 6.1 failed job threshold), a `printer_offline` alert is enqueued with: agent name, last seen timestamp
**And** all alerts are formatted by `alert_formatter.py` — concise, human-readable, includes tenant name and timestamp in IST
**And** alerts are delivered within 60 seconds of the triggering event (NFR34)

### Story 9.4: Daily EOD Report & Backup Confirmation

As an **Admin or Owner**,
I want to receive a daily EOD summary and backup confirmation in my Telegram group automatically,
So that I know the day's financial performance and data safety without logging into the system.

**Acceptance Criteria:**

**Given** the configured `eod_report_time` is reached
**When** the EOD report scheduler triggers
**Then** `eod_report_formatter.py` generates a report including: total revenue (paise formatted as ₹), bills count, top 3 items by volume, total expense amount, void count, and staff attendance summary (FR45, FR44)
**And** the report is enqueued as an `eod_report` alert and delivered to the tenant's Telegram group
**And** the nightly `pg_dump` backup job runs after EOD report delivery; on success a `backup_confirmation` alert is enqueued with: backup size, timestamp, storage location (FR47, NFR36)
**And** if the backup fails, a `backup_failed` alert is enqueued immediately with priority retry
**And** the EOD scheduler is a cron job in the `telegram_worker` container — configurable per tenant timezone (default IST)

---

## Epic 10: Analytics, Reporting & GST Compliance

Admin and Owner can view live operations, query historical analytics, search bill history, export operational reports, generate GST-compliant records with sequential bill numbers, and rely on a 7-year hot/archive retention architecture.

### Story 10.1: Hot/Archive Partition Architecture & Retention Policy

As a **developer**,
I want the hot/archive data split implemented via PostgreSQL range partitioning managed by pg_partman,
So that live billing queries remain under 10ms regardless of historical data volume and 7-year GST retention is guaranteed.

**Acceptance Criteria:**

**Given** the migration runs
**When** pg_partman is configured for `bills` and `bill_events`
**Then** monthly range partitions are created automatically on `closed_at` date — `pg_partman` manages partition creation for future months
**And** the "hot" partition covers the rolling current week — queries scoped to `closed_at > now() - interval '7 days'` never touch archive partitions
**And** `GET /api/v1/bills` (active billing queries) executes in under 10ms via the hot layer + Valkey cache (NFR2, NFR10)
**And** archive partitions older than the retention period (default 7 years, configurable per tenant) are flagged for cold storage — data is never deleted, only moved
**And** the partition boundary is transparent to the application layer — all queries work identically against partitioned and non-partitioned data
**And** `GET /api/v1/tenants/me/retention-policy` returns current retention config; `PATCH` allows Admin to extend (never shorten) the retention period (FR94)

### Story 10.2: Live Operations Dashboard

As an **Admin or Manager**,
I want a real-time dashboard showing open bills, KOT pipeline status, staff on duty, and printer connectivity,
So that I have complete situational awareness of the restaurant floor without asking anyone.

**Acceptance Criteria:**

**Given** an authenticated Admin navigates to the dashboard
**When** the page loads
**Then** `GET /api/v1/dashboard/live` returns: open bill count, bills by status (draft/kot_sent/billed), active KOT count, staff currently on shift, print agent status (online/offline/last_seen) (FR49)
**And** the dashboard updates in real time via WebSocket events — bill status changes, KOT fires, and print agent heartbeats refresh the relevant panel without a full page reload
**And** clicking any open bill navigates to its detail view with the per-bill status timeline (FR73)
**And** the dashboard is accessible to Manager and Admin roles; Super-Admin sees aggregate platform stats without tenant data

### Story 10.3: Bill History Search & Export

As an **Admin**,
I want to search bill history with multiple filters and export results,
So that I can investigate any transaction and produce reports for any period.

**Acceptance Criteria:**

**Given** an authenticated Admin calls `GET /api/v1/bills/history`
**When** query params include any combination of `bill_number`, `table_id`, `staff_id`, `date_from`, `date_to`, `amount_min_paise`, `amount_max_paise`, `status`
**Then** results are returned paginated (50 per page) with: bill number, table, staff name, opened/closed timestamps, total paise, status (FR80)
**And** results respect the hot/archive partition boundary transparently — queries spanning both layers return complete results
**And** `POST /api/v1/reports/export` accepts the same filters and returns a downloadable CSV or PDF: daily revenue summary, payroll report, supplier expense ledger (FR81, NFR55)
**And** CSV export is UTF-8, Excel/Google Sheets compatible; PDF export uses a clean tabular layout
**And** export jobs run asynchronously for large date ranges — Admin receives a download link when ready

### Story 10.4: Historical Analytics

As an **Admin or Owner**,
I want to view historical analytics covering revenue trends, peak hours, top items, staff performance, void rates, and expense comparisons,
So that I can make data-driven decisions about the business without a separate analytics tool.

**Acceptance Criteria:**

**Given** an authenticated Admin navigates to Analytics
**When** they select a date range and metric
**Then** `GET /api/v1/analytics/revenue?period=...` returns daily revenue totals (paise) for the period — rendered as a line/bar chart via Recharts (FR50)
**And** `GET /api/v1/analytics/peak-hours` returns order count by hour-of-day aggregated over the period — rendered as a heatmap
**And** `GET /api/v1/analytics/top-items?limit=10` returns items ranked by order volume and revenue value
**And** `GET /api/v1/analytics/staff-performance` returns per-staff: bills handled, total value, void rate — accessible to Admin only
**And** `GET /api/v1/analytics/expense-vs-revenue` returns daily revenue vs expense totals — includes supplier invoice data from Epic 8
**And** all analytics queries run against the archive layer — zero impact on live billing performance (NFR11)
**And** the analytics UI is responsive for Owner's mobile monitoring use case: charts stack single-column on narrow viewports

### Story 10.5: GST Report Generation & Bill Exclusion

As an **Admin**,
I want to generate an exportable GST report with sequential bill numbers and manage bill exclusions with a full audit record,
So that my GST filings are accurate, auditable, and produced without manual calculation.

**Acceptance Criteria:**

**Given** an authenticated Admin calls `POST /api/v1/gst/report`
**When** the request includes `{ period_start, period_end }`
**Then** the report includes all `billed` status bills in the period: sequential bill number, date, items, CGST amount (paise), SGST amount (paise), total paise — calculated from snapshotted `gst_rate_bps` on each `bill_item` (FR53)
**And** `POST /api/v1/gst/exclude/{bill_id}` marks a bill as excluded from GST with a mandatory reason — excluded bills appear in a separate section of the report, not removed (FR52)
**And** the GST report is exportable as CSV — sequential bill numbers are unbroken; voided bills appear with VOID stamp and ₹0 amounts
**And** bill exclusions are written to `audit_logs` with actor, reason, and timestamp
**And** `GET /api/v1/gst/report/{id}` retrieves a previously generated report — reports are immutable once generated

---

## Epic 11: Waiter Mode *(Feature-flagged — `waiter_mode` flag)*

Waiters can create and manage bills at the table on their own devices, view their own performance stats, and transfer finalized bills to the billing counter for payment collection.

### Story 11.1: Waiter Bill Creation & Mobile Surface

As a **Waiter**,
I want to create and manage bills on my own mobile device with my identity auto-loaded on login,
So that I can take orders at the table without returning to the billing counter.

**Acceptance Criteria:**

**Given** the `waiter_mode` feature flag is enabled for the tenant
**When** an authenticated Waiter opens the app on a mobile device
**Then** the Waiter surface renders in portrait-first layout: bottom nav replaces sidebar, touch targets minimum 44px, one-handed usability (NFR49, FR11)
**And** the Waiter uses the same `POST /api/v1/bills` endpoint — bills are tagged with `opened_by = waiter_user_id`
**And** the command palette is accessible via a large floating action button (touch-first — Space bar remains functional for keyboard users)
**And** the Waiter can add items, fire KOT, and view bill state — all same underlying APIs as Biller
**And** the Waiter surface is gated by `<FeatureGate flag="waiter_mode">` — renders nothing if flag is disabled
**And** `GET /api/v1/bills?opened_by=me&status=draft,kot_sent` returns only the authenticated Waiter's own active bills

### Story 11.2: Bill Transfer to Billing Counter

As a **Waiter**,
I want to transfer a finalized bill to the billing counter for payment collection,
So that I can hand off the payment step to the Biller without re-entering any bill data.

**Acceptance Criteria:**

**Given** a Waiter has a bill in `kot_sent` or `partially_kot_sent` status
**When** they tap "Transfer to Counter"
**Then** `POST /api/v1/bills/{id}/transfer` sets `bill.transferred_to_counter = true` and emits a `bill.transferred` WebSocket event to all Biller sessions (FR12)
**And** the transferred bill appears in the Biller's active bills sidebar panel with a "Transferred" badge
**And** the Biller can open the transferred bill in a new tab and proceed with payment collection
**And** after transfer, the Waiter's view of the bill becomes read-only — they can see status but not modify it
**And** transfer is only possible when all KOT items have been fired — HTTP 409 if any items remain in `pending` KOT status

---

## Epic 12: Smart Suggestions & Intelligent Features *(Feature-flagged — `suggestion_engine` flag)*

The billing engine proactively surfaces co-order suggestions and order frequency insights via a fully isolated suggestion engine that never contends with billing database performance.

### Story 12.1: Suggestion Engine Schema & Async Worker

As a **developer**,
I want a separate Valkey-backed suggestion engine with an async worker that builds co-occurrence and frequency data,
So that suggestion reads are sub-millisecond and billing database performance is never impacted.

**Acceptance Criteria:**

**Given** the `suggestion_engine` feature flag is enabled for a tenant
**When** a bill is closed
**Then** `suggestion_worker.py` consumes the `bill.closed` event asynchronously and updates Valkey sorted sets: `freq:{tenant_id}:{item_id}` (ZINCRBY for all-time frequency), `co:{tenant_id}:{item_id}` (ZINCRBY for each co-ordered item) (FR95)
**And** the suggestion worker runs in its own Docker container — it never imports from the billing module or queries the `bills` PostgreSQL table directly
**And** `seed_suggestions.py` backfills Valkey from historical closed bills on first enable — runs as a one-time job, not on every startup
**And** all Valkey suggestion keys are namespaced by `tenant_id` — cross-tenant contamination is impossible
**And** if the suggestion worker is down, billing continues normally — suggestions degrade gracefully to empty (no error surfaced to the Biller)

### Story 12.2: Co-Order Suggestions in Command Palette

As a **Biller**,
I want to see up to 3 co-order suggestions inline after adding an item,
So that I can add commonly paired items in one extra keystroke rather than searching again.

**Acceptance Criteria:**

**Given** the `suggestion_engine` feature flag is enabled
**When** a Biller adds an item to the active bill
**Then** `GET /api/v1/suggestions/co-order?item_id={id}&tenant_id={tid}&limit=3` returns up to 3 items co-ordered with the added item in at least 20% of past orders (FR69)
**And** suggestions appear inline below the added item in the bill canvas: item name, shortcode, price — each with a one-click/Enter add button
**And** suggestions disappear after 5 seconds or when the next command palette action begins
**And** adding a suggested item fires the same `POST /api/v1/bills/{id}/items` endpoint — no special suggestion API for adds
**And** if fewer than 3 items meet the 20% co-occurrence threshold, only qualifying suggestions are shown — no padding with low-confidence suggestions
**And** the suggestion read from Valkey completes in under 5ms — if it exceeds 100ms suggestions are silently skipped
