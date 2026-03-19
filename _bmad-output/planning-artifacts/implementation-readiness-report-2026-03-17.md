---
stepsCompleted: ['step-01-document-discovery', 'step-02-prd-analysis', 'step-03-epic-coverage-validation', 'step-04-ux-alignment', 'step-05-epic-quality-review', 'step-06-final-assessment']
workflowStatus: complete
completedAt: '2026-03-17'
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/architecture.md'
  - '_bmad-output/planning-artifacts/epics.md'
  - '_bmad-output/planning-artifacts/ux-design-specification.md'
---

# Implementation Readiness Assessment Report

**Date:** 2026-03-17
**Project:** sphotel

## Document Inventory

| Document | File | Status |
|---|---|---|
| PRD | `prd.md` | ✅ Complete |
| Architecture | `architecture.md` | ✅ Complete |
| Epics & Stories | `epics.md` | ✅ Complete (12 epics, 62 stories) |
| UX Design | `ux-design-specification.md` | ⚠️ frontmatter in-progress flag; content complete |

## PRD Analysis

### Summary
- **Total Functional Requirements:** 89 FRs (FR1–FR95, with gaps at FR20, FR68, FR70, FR91 — these numbers were not defined in the PRD)
- **Total Non-Functional Requirements:** 56 NFRs (NFR1–NFR56)
- **PRD Status:** Complete (`workflowStatus: complete`, 2026-03-12)

### Functional Requirement Categories (89 FRs)
- Billing Engine: FR1–FR13, FR61–FR63, FR64, FR66–FR67, FR76, FR79
- Kitchen Management: FR14–FR18, FR31
- Payment & Cash: FR19, FR21–FR23, FR35–FR36, FR77, FR82
- Print Management: FR24–FR27, FR65, FR78
- Menu Management: FR28–FR30, FR51, FR75, FR83
- Auth & Security: FR32–FR37, FR74, FR84–FR90, FR93
- Staff & Payroll: FR38–FR41, FR71
- Expenses: FR42–FR44
- Telegram: FR45–FR48
- Analytics & Reporting: FR49–FR50, FR52–FR53, FR73, FR80–FR81
- Offline & Resilience: FR54–FR56, FR66
- Tenant Management: FR57–FR60, FR92
- GST Compliance: FR51, FR53, FR94
- Waiter Mode: FR11–FR12, FR71
- Suggestion Engine: FR69, FR95

### NFR Categories (56 NFRs)
- Performance (NFR1–NFR11): Response times, query performance, offline activation
- Security (NFR12–NFR30): Auth, encryption, audit, CORS, injection prevention
- Reliability (NFR31–NFR40): Offline resilience, crash recovery, RPO/RTO, uptime
- Scalability (NFR41–NFR46): Tenant isolation, horizontal scaling, data volume
- Accessibility (NFR47–NFR51): Keyboard navigation, touch targets, WCAG AA
- Integrations (NFR52–NFR56): Telegram, Print Agent, Backup, CSV, TOTP

### PRD Completeness Assessment
✅ Requirements are numbered, unambiguous, and testable
✅ Clear scope boundaries defined (out-of-scope: customer-facing display)
✅ User roles and personas well-defined (6 roles)
✅ Success metrics defined (< 15s bill completion, < 100ms command palette)
⚠️ FR20, FR68, FR70, FR91 numbers are absent — intentional gaps in PRD numbering (not missing requirements)

## Epic Coverage Validation

### Coverage Statistics
- **Total PRD FRs defined:** 89
- **FRs covered in epics:** 89
- **Coverage percentage: 100%** ✅
- **PRD numbering gaps (not missing):** FR20, FR68, FR70, FR91

### Coverage Matrix

| FR | PRD Requirement (summary) | Epic | Status |
|---|---|---|---|
| FR1 | Fuzzy text search item add | Epic 4 — Story 4.5 | ✅ Covered |
| FR2 | Shortcode / numeric code item add | Epic 4 — Story 4.5 | ✅ Covered |
| FR3 | Command palette keyboard trigger | Epic 4 — Story 4.5 | ✅ Covered |
| FR4 | Up to 10 simultaneous open bills (configurable) | Epic 4 — Story 4.6 | ✅ Covered |
| FR5 | F-key bill switching | Epic 4 — Story 4.6 | ✅ Covered |
| FR6 | Active bills sidebar panel | Epic 4 — Story 4.6 | ✅ Covered |
| FR7 | Fire KOT — delta only | Epic 4 — Story 4.7 | ✅ Covered |
| FR8 | Partial KOT fire | Epic 4 — Story 4.7 | ✅ Covered |
| FR9 | Void request by Biller | Epic 4 — Story 4.8 | ✅ Covered |
| FR10 | KOT-fired item lock | Epic 4 — Story 4.8 | ✅ Covered |
| FR11 | Waiter bill creation on own device | Epic 11 — Story 11.1 | ✅ Covered |
| FR12 | Waiter bill transfer to counter | Epic 11 — Story 11.2 | ✅ Covered |
| FR13 | Immutable sequential bill numbers | Epic 4 — Story 4.2 | ✅ Covered |
| FR14 | Kitchen real-time KOT feed | Epic 7 — Story 7.2 | ✅ Covered |
| FR15 | Mark individual item ready | Epic 7 — Story 7.3 | ✅ Covered |
| FR16 | Mark full order ready + Biller notification | Epic 7 — Story 7.3 | ✅ Covered |
| FR17 | Kitchen marks item unavailable | Epic 7 — Story 7.4 | ✅ Covered |
| FR18 | Delta-only KOT updates | Epic 7 — Story 7.2 | ✅ Covered |
| FR19 | Multi-method payment collection | Epic 5 — Story 5.2 | ✅ Covered |
| FR21 | Shift cash reconciliation + discrepancy detection | Epic 5 — Story 5.4 | ✅ Covered |
| FR22 | Amended bill audit flag | Epic 4 — Story 4.2 | ✅ Covered |
| FR23 | Complete bill audit history view | Epic 5 — Story 5.6 | ✅ Covered |
| FR24 | Async print queue (non-blocking) | Epic 6 — Story 6.4 | ✅ Covered |
| FR25 | Reprint closed bill via shortcut | Epic 6 — Story 6.4 | ✅ Covered |
| FR26 | Print agent offline queue + auto-flush | Epic 6 — Story 6.4 | ✅ Covered |
| FR27 | Print agent registration + Admin management | Epic 6 — Story 6.2 | ✅ Covered |
| FR28 | Inline menu item editing | Epic 3 — Story 3.3 | ✅ Covered |
| FR29 | CSV menu import/export with diff preview | Epic 3 — Story 3.4 | ✅ Covered |
| FR30 | Menu category/item reordering | Epic 3 — Story 3.3 | ✅ Covered |
| FR31 | Availability propagation within 3 seconds | Epic 7 — Story 7.4 | ✅ Covered |
| FR32 | Six-role RBAC system | Epic 2 — Story 2.1 | ✅ Covered |
| FR33 | PIN authentication for operational roles | Epic 2 — Story 2.2 | ✅ Covered |
| FR34 | Email + session auth for Admin/Super-Admin | Epic 2 — Story 2.3 | ✅ Covered |
| FR35 | Void approval workflow (Admin) | Epic 5 — Story 5.5 | ✅ Covered |
| FR36 | All financial actions tagged to authenticated user | Epic 5 — Story 5.2 | ✅ Covered |
| FR37 | Session auto-expiry (4hr) | Epic 2 — Story 2.5 | ✅ Covered |
| FR38 | Staff attendance recording per shift | Epic 8 — Story 8.2 | ✅ Covered |
| FR39 | Configurable reward formula | Epic 8 — Story 8.2 | ✅ Covered |
| FR40 | Auto-calculated staff rewards | Epic 8 — Story 8.3 | ✅ Covered |
| FR41 | Payroll summary view | Epic 8 — Story 8.3 | ✅ Covered |
| FR42 | Supplier invoice recording | Epic 8 — Story 8.5 | ✅ Covered |
| FR43 | Vendor/expense category directory | Epic 8 — Story 8.5 | ✅ Covered |
| FR44 | Expenses in EOD reports and analytics | Epic 8 — Story 8.5 | ✅ Covered |
| FR45 | Daily EOD Telegram report | Epic 9 — Story 9.4 | ✅ Covered |
| FR46 | Real-time financial alerts to Telegram | Epic 9 — Story 9.3 | ✅ Covered |
| FR47 | Daily backup confirmation to Telegram | Epic 9 — Story 9.4 | ✅ Covered |
| FR48 | Single group chat ID Telegram config | Epic 9 — Story 9.2 | ✅ Covered |
| FR49 | Live operations dashboard | Epic 10 — Story 10.2 | ✅ Covered |
| FR50 | Historical analytics | Epic 10 — Story 10.4 | ✅ Covered |
| FR51 | GST rate configuration per tenant | Epic 3 — Story 3.6 | ✅ Covered |
| FR52 | Bill GST exclusion with flagged audit record | Epic 10 — Story 10.5 | ✅ Covered |
| FR53 | Exportable GST report | Epic 10 — Story 10.5 | ✅ Covered |
| FR54 | Offline bill creation via IndexedDB | Epic 4 — Story 4.3 | ✅ Covered |
| FR55 | Auto-sync + server sequential number assignment | Epic 4 — Story 4.3 | ✅ Covered |
| FR56 | Crash recovery — full bill state restore | Epic 4 — Story 4.4 | ✅ Covered |
| FR57 | Super-Admin tenant provisioning | Epic 3 — Story 3.1 | ✅ Covered |
| FR58 | Super-Admin platform analytics (no tenant data) | Epic 3 — Story 3.1 | ✅ Covered |
| FR59 | Complete tenant data isolation (RLS) | Epic 3 — Story 3.1 | ✅ Covered |
| FR60 | Admin onboarding checklist | Epic 3 — Story 3.2 | ✅ Covered |
| FR61 | Keyboard shortcut overlay (`?` key) | Epic 4 — Story 4.9 | ✅ Covered |
| FR62 | "Right Now" time-of-day item section | Epic 4 — Story 4.9 | ✅ Covered |
| FR63 | Bill templates (preset item combos) | Epic 4 — Story 4.9 | ✅ Covered |
| FR64 | Concurrent edit lock indicator | Epic 4 — Story 4.6 | ✅ Covered |
| FR65 | Print agent one-time token authentication | Epic 6 — Story 6.2 | ✅ Covered |
| FR66 | Persistent offline mode indicator | Epic 4 — Story 4.3 | ✅ Covered |
| FR67 | Audio feedback for billing events | Epic 4 — Story 4.7 | ✅ Covered |
| FR69 | Co-order item suggestions inline | Epic 12 — Story 12.2 | ✅ Covered |
| FR71 | Waiter performance stats on login | Epic 8 — Story 8.4 | ✅ Covered |
| FR72 | Per-user display theme preference | Epic 2 — Story 2.6 | ✅ Covered |
| FR73 | Per-bill status timeline view | Epic 10 — Story 10.2 | ✅ Covered |
| FR74 | Admin: create/edit/deactivate/reset staff PINs | Epic 2 — Story 2.4 | ✅ Covered |
| FR75 | Table and section layout configuration | Epic 3 — Story 3.5 | ✅ Covered |
| FR76 | Discount / complimentary bill | Epic 4 — Story 4.9 | ✅ Covered |
| FR77 | Formal shift open/close | Epic 5 — Story 5.4 | ✅ Covered |
| FR78 | Token slip print template configuration | Epic 3 — Story 3.7 | ✅ Covered |
| FR79 | Top-5 all-time + top-5 recent items in billing search | Epic 4 — Story 4.5 | ✅ Covered |
| FR80 | Bill history search (multi-filter) | Epic 10 — Story 10.3 | ✅ Covered |
| FR81 | Operational report export (CSV/PDF) | Epic 10 — Story 10.3 | ✅ Covered |
| FR82 | Post-collection payment method correction | Epic 5 — Story 5.2 | ✅ Covered |
| FR83 | Admin/Manager config change audit logging | Epic 3 — Stories 3.3, 3.6, 3.8 | ✅ Covered |
| FR84 | Rate limiting + account lockout | Epic 2 — Stories 2.2, 2.3 | ✅ Covered |
| FR85 | Admin: immediate session invalidation for staff | Epic 2 — Story 2.4 | ✅ Covered |
| FR86 | Sensitive data encrypted at rest | Epic 2 — Story 2.2 | ✅ Covered |
| FR87 | No permission escalation above own role | Epic 2 — Stories 2.1, 2.4 | ✅ Covered |
| FR88 | WSS-only WebSocket connections | Epic 1 — Story 1.5 | ✅ Covered |
| FR89 | Role-scoped data visibility boundaries | Epic 2 — Story 2.1 | ✅ Covered |
| FR90 | Credential self-management + Super-Admin reset | Epic 2 — Story 2.5 | ✅ Covered |
| FR92 | Full tenant data archive export | Epic 3 — Story 3.8 | ✅ Covered |
| FR93 | TOTP 2FA for Admin/Super-Admin | Epic 2 — Story 2.3 | ✅ Covered |
| FR94 | Hot/archive 7-year retention architecture | Epic 10 — Story 10.1 | ✅ Covered |
| FR95 | Suggestion engine isolated datastore | Epic 12 — Story 12.1 | ✅ Covered |

### Missing Requirements
**None.** All 89 defined FRs have full traceability to at least one story with testable acceptance criteria.

## UX Alignment Assessment

### UX Document Status
✅ Found: `ux-design-specification.md` — 8 steps completed, visual foundation complete
⚠️ Advisory: `workflowStatus: in-progress` in frontmatter (content is substantive; detailed per-screen wireframes not produced — acceptable for this stage)

### UX ↔ PRD Alignment

| UX Requirement | PRD Requirement | Status |
|---|---|---|
| Space bar opens command palette | FR3 | ✅ Aligned |
| Ctrl+K fire KOT, Ctrl+B payment, Ctrl+P print, Ctrl+T new bill, Ctrl+W close | FR3, FR7, FR19, FR24, FR25 | ✅ Aligned |
| F1–F10 bill switching | FR5 | ✅ Aligned |
| `?` keyboard shortcut overlay | FR61 | ✅ Aligned |
| Active bills sidebar panel (280px) | FR6 | ✅ Aligned |
| Optimistic UI — item appears instantly | NFR8, NFR1 | ✅ Aligned |
| Async print — UI never waits | FR24 | ✅ Aligned |
| Kitchen: min 18px font, min 56px touch targets | NFR48 | ✅ Aligned |
| Biller: full keyboard navigation, no mouse-only actions | NFR47 | ✅ Aligned |
| Offline indicator (amber, persistent) | FR66 | ✅ Aligned |
| Dark-first design (zinc-950), configurable tenant accent | FR72, UX spec | ✅ Aligned |
| Crash recovery toast (non-blocking) | FR56 | ✅ Aligned |
| Audio feedback (item add, KOT sent, payment) | FR67 | ✅ Aligned |
| WCAG AA contrast, visible focus rings, prefers-reduced-motion | NFR47, NFR50, NFR51 | ✅ Aligned |
| Role-driven sidebar — single app shell | FR32, FR89 | ✅ Aligned |

### UX ↔ Architecture Alignment

| UX Decision | Architecture Decision | Status |
|---|---|---|
| shadcn/ui + Tailwind CSS | Architecture specifies same stack | ✅ Aligned |
| React SPA, keyboard-first | Architecture: React + Vite SPA (no SSR) | ✅ Aligned |
| Zustand for bill tab state | Architecture specifies Zustand | ✅ Aligned |
| TanStack Query for server state | Architecture specifies TanStack Query | ✅ Aligned |
| "Kitchen receives KOT in real time" | Architecture: dedicated WebSocket service, <3s NFR3 | ✅ Aligned |
| Optimistic UI pattern | IndexedDB + async API supports this | ✅ Aligned |
| Configurable tenant accent colour | Story 3.8: PATCH /api/v1/tenants/me/theme | ✅ Aligned |
| Role-specific PWA manifests | Story 1.4: biller/kitchen/admin manifests | ✅ Aligned |
| Owner mobile monitoring (single-column) | Story 10.4: responsive analytics UI | ✅ Aligned |

### Warnings (Non-Blocking)

⚠️ **W1 — Waiter Mode portrait UX not specified:** The UX document does not include a portrait-first screen layout for Waiter Mode. Story 11.1 specifies bottom nav + 44px touch targets but there are no interaction mockups. Recommend producing a Waiter Mode UX addendum before Sprint 11 begins. *Flagged by UX Designer in party mode discussion.*

⚠️ **W2 — Manager & Admin screens underspecified:** The UX document thoroughly covers the Biller and Kitchen surfaces. Manager oversight screens and Admin configuration screens are implied but not laid out in detail. This is acceptable for MVP planning but should be addressed in early implementation sprints.

⚠️ **W3 — UX frontmatter status:** The `workflowStatus: in-progress` flag in the UX document should be updated to `complete` to reflect actual state. No content gaps were identified — this is a documentation hygiene issue only.

---

## Epic Quality Review

Beginning **Epic Quality Review** against create-epics-and-stories standards.

Validated: user value focus, epic independence, story dependency chains, database creation timing, acceptance criteria completeness, and forward dependency analysis across all 12 epics and 62 stories.

---

### A. User Value Focus Check

| Epic | Title | User Value Assessment | Verdict |
|---|---|---|---|
| Epic 1 | Project Foundation & Infrastructure Setup | Technical in nature — acceptable for greenfield. Goal clearly states developer outcome: "team can start building immediately." All 7 stories have testable ACs. | ⚠️ Minor: Technical title — expected for foundation epic |
| Epic 2 | Authentication & RBAC | User-centric: "All staff and admin roles can securely authenticate." Stories framed from Biller, Admin, Super-Admin perspectives. | ✅ Pass |
| Epic 3 | Tenant Setup & Full Admin Configuration | User-centric: Admin can configure everything needed before billing begins. | ✅ Pass |
| Epic 4 | Core Billing Engine with Offline Resilience | User-centric: Biller can complete full bill lifecycle via keyboard. | ✅ Pass |
| Epic 5 | Payment, Cash & Void Management | User-centric: payment collection, void governance, cash reconciliation. | ✅ Pass |
| Epic 6 | Async Print System & Print Agent | User-centric: "billing UI never waits for a printer." | ✅ Pass |
| Epic 7 | Kitchen Display & Real-Time Operations | User-centric: kitchen staff can view and act on KOTs in real time. | ✅ Pass |
| Epic 8 | Staff Management, Payroll & Expense Tracking | User-centric: managers can record attendance, calculate rewards, track expenses. | ✅ Pass |
| Epic 9 | Telegram Notifications & Intelligent Alerting | User-centric: Admin receives alerts and EOD report without manual effort. | ✅ Pass |
| Epic 10 | Analytics, Reporting & GST Compliance | User-centric: Admin can view live ops, query history, export reports. | ✅ Pass |
| Epic 11 | Waiter Mode *(Feature-flagged)* | User-centric: Waiter can take orders at table on own device. | ✅ Pass |
| Epic 12 | Smart Suggestions & Intelligent Features *(Feature-flagged)* | User-centric: Biller receives co-order suggestions proactively. | ✅ Pass |

---

### B. Epic Independence Validation

**Sequential dependency chain (correct and expected):**
Epic 1 → Epic 2 → Epic 3 → Epic 4 → Epic 5 → Epic 6 → Epic 7 → Epic 8 → Epic 9 → Epic 10 → Epic 11 → Epic 12

Each epic can function using only the output of all prior epics. No circular dependencies detected. ✅

**Forward reference handling for Telegram (correct pattern):** Stories 4.8, 5.4, 6.1 explicitly acknowledge Telegram dependency with stub notes ("triggers a Telegram alert stub — wired in Epic 9"). This is the correct pattern for managing forward dependencies without blocking stories. ✅

---

### C. Database/Entity Creation Timing

| Epic | Schema Story | Tables Created | Verdict |
|---|---|---|---|
| Epic 1 | Story 1.2 | `tenants`, `tenant_users`, `audit_logs` | ✅ |
| Epic 2 | Story 2.1 | `role_permissions`, `tenant_users` (extends) | ✅ |
| Epic 3 | **None** | `menu_items`, `menu_categories`, `sections`, `tables`, `gst_categories`, `print_templates` — implied in API stories, never explicitly defined | 🔴 **Missing** |
| Epic 4 | Story 4.1 | `bills`, `bill_items`, `bill_events` — full column-level ACs | ✅ |
| Epic 5 | Story 5.1 | `payments`, `shift_sessions`, `void_approvals` — full column-level ACs | ✅ |
| Epic 6 | Story 6.1 | `print_jobs`, `print_agents` — full column-level ACs | ✅ |
| Epic 7 | Story 7.1 | WebSocket service (no new tables — kitchen data in existing `bills`/`bill_items`) | ✅ |
| Epic 8 | Story 8.1 | `staff_attendance`, `reward_formulas`, `payroll_entries`, `suppliers`, `expense_categories`, `supplier_invoices` — full column-level ACs | ✅ |
| Epic 9 | Story 9.1 | `telegram_alerts`, `telegram_config` — full column-level ACs | ✅ |
| Epic 10 | Story 10.1 | Partition architecture on `bills`, `bill_events` | ✅ |
| Epic 11 | No new tables needed (extends existing `bills`) | — | ✅ |
| Epic 12 | No PostgreSQL tables (Valkey only) | — | ✅ |

---

### D. Violations Found

#### 🔴 Critical Violation 1 — WebSocket Forward Dependency

**Affected stories:** Epic 4 (Stories 4.7, 4.8), Epic 5 (Story 5.5), Epic 6 (Story 6.4)

**Evidence:**
- Story 4.7: *"the KOT is dispatched to the kitchen WebSocket channel `kitchen.kot.fired` with the delta payload only"*
- Story 4.8: *"a real-time WebSocket event `bill.void_requested` is broadcast to Admin/Manager sessions for the tenant"*
- Story 5.5: *"Admin/Manager UI shows a real-time void request panel that updates via WebSocket event `bill.void_requested`"*
- Story 6.4: *"a small print status indicator shows queued → printing → done — updates via WebSocket `print.*` events"*

**The violation:** The dedicated WebSocket service (Valkey pub/sub router, connection management, WSS enforcement, event envelope spec) is first established in **Story 7.1** (Epic 7). Stories 4.7, 4.8, 5.5, and 6.4 cannot be independently completed — they all require WebSocket event dispatch infrastructure that does not exist until 3 epics later.

This is a forward dependency that breaks story independence. Unlike the Telegram stubs (which explicitly acknowledge deferral), these stories present WebSocket dispatch as an active, functioning requirement.

**Remediation:** Move basic WebSocket bootstrap — connection manager, Valkey pub/sub channel routing, WSS event envelope, reconnect policy — to a new **Story 1.8** in Epic 1. Story 7.1 would then focus exclusively on kitchen-specific features (KOT feed, item ready events, availability propagation) built on top of the already-established connection infrastructure.

---

#### 🟠 Major Issue 2 — Epic 3 Missing Schema Story

**Affected stories:** Stories 3.3, 3.4, 3.5, 3.6, 3.7

**Evidence:**
Every feature epic that creates new domain tables has a dedicated schema-first story with the pattern: *"Given the migration runs, When the X table is queried, Then X has: id (type), column_name (type with constraint)..."*

- Epic 4 → Story 4.1: bills, bill_items, bill_events — all columns specified
- Epic 5 → Story 5.1: payments, shift_sessions, void_approvals — all columns specified
- Epic 6 → Story 6.1: print_jobs, print_agents — all columns specified
- Epic 8 → Story 8.1: staff_attendance, reward_formulas, payroll_entries, suppliers, expense_categories, supplier_invoices — all columns specified

**Epic 3 has no schema story.** The following tables are referenced in Epic 3 stories but their schema is never explicitly defined with column types, constraints, FK rules, or index conventions:
- `menu_items` (referenced in Story 3.3 — column names listed informally in API payload but no migration AC)
- `menu_categories` (referenced, no schema)
- `sections` / `tables` (referenced in Story 3.5, no migration AC)
- `gst_categories` (referenced in Story 3.6, rate columns are defined — closest to a schema AC but embedded in an API story)
- `print_template_config` (referenced in Story 3.7, no explicit schema)

Without an explicit schema story, implementers have no testable, authoritative reference for column types (especially the integer paise constraint on `price_paise`), null constraints, uniqueness rules, or the append-only audit trigger for config change logging (FR83).

**Remediation:** Add **Story 3.0: Menu, Configuration & Layout Schema** as the first story in Epic 3, following the same schema-first pattern as Story 4.1. This story defines all Epic 3 domain tables with explicit column types, constraints, and the schema conventions (snake_case, INTEGER paise, TIMESTAMPTZ UTC, audit triggers).

---

#### 🟠 Major Issue 3 — "Right Now" Valkey Data Pipeline Undefined

**Affected story:** Story 4.9 (FR62)

**Evidence:**
Story 4.9 states: *"the 'Right Now' section in the command palette shows items popular at the current time of day (hour-bucket query from Valkey)"*

This requires time-of-day order frequency data to exist in Valkey, keyed by hour bucket (e.g., `time:{tenant_id}:{hour}:{item_id}`). No story in any epic defines:
- The Valkey key schema for time-of-day data
- The worker or event handler that populates these keys
- How the population mechanism works for historical backfill vs new orders

The suggestion engine (Epic 12, Story 12.1) populates `freq:{tenant_id}:{item_id}` (all-time) and `co:{tenant_id}:{item_id}` (co-occurrence) but does NOT populate any time-of-day keys. Story 4.9 references a Valkey query that has no producer anywhere in the 62 stories.

This means FR62 ("System surfaces menu items relevant to the current time of day") is partially unimplemented — the AC exists in Story 4.9 but the data pipeline that feeds it does not.

**Remediation:** Two options:
- **Option A (preferred):** Extend Story 12.1 (suggestion engine worker) to also populate `time:{tenant_id}:{hour}:{item_id}` Valkey keys using ZINCRBY on bill close. Update Story 4.9's AC to be gated on `suggestion_engine` feature flag — if flag is disabled, "Right Now" section is hidden.
- **Option B:** Replace the Valkey query in Story 4.9 with a simple SQL COUNT query from the hot partition (acceptable given hot layer < 10ms guarantee). Remove the Valkey dependency entirely from this feature.

---

#### 🟠 Major Issue 4 — FR Coverage Map in epics.md Has Stale Pre-Merge Epic Numbers

**Location:** epics.md "FR Coverage Map" section

**Evidence:**
After party mode discussion, old Epics 3 (Tenant Management) and 4 (Menu & Config) were merged into a single Epic 3. This shifted all subsequent epic numbers down by one. However, the FR Coverage Map in epics.md was not updated:

| FR | Coverage Map Shows (stale) | Actual Location |
|---|---|---|
| FR1–FR13 | Epic 5 | Epic 4 (Core Billing Engine) |
| FR14–FR18, FR31 | Epic 8 | Epic 7 (Kitchen Display) |
| FR19, FR21–FR23, FR35–FR36, FR77, FR82 | Epic 6 | Epic 5 (Payment) |
| FR24–FR27, FR65, FR78 | Epic 7 | Epic 6 (Print) |
| FR38–FR44 | Epic 9 | Epic 8 (Staff & Payroll) |
| FR45–FR48 | Epic 10 | Epic 9 (Telegram) |
| FR49–FR50, FR52–FR53, FR73, FR80–FR81, FR94 | Epic 11 | Epic 10 (Analytics) |
| FR11–FR12 | Epic 12 | Epic 11 (Waiter Mode) |
| FR69, FR95 | Epic 13 | Epic 12 (Smart Suggestions) |
| FR71 | Epic 12 | Epic 8, Story 8.4 |

The implementation-readiness-report has the CORRECT mapping (validated against actual story locations). The epics.md internal coverage map is a documentation artifact from the pre-merge state.

**Remediation:** Update the FR Coverage Map section in epics.md to reflect the current 12-epic numbering. Correct FR71 to Epic 8, Story 8.4.

---

### E. Minor Concerns

🟡 **MC1 — Story 3.5 forward reference:** Story 3.5 (Table & Section Layout) contains: *"table names are visible in the Biller's active bills sidebar panel (FR6) — populated in Epic 4."* This is informational only. The table configuration IS completable independently. Noted for documentation clarity.

🟡 **MC2 — Epic 1 technical title:** "Project Foundation & Infrastructure Setup" uses technical language. Acceptable for greenfield foundation epics — no remediation needed.

🟡 **MC3 — `tenant_feature_flags` table not in migration AC:** Story 1.6 references this table as Valkey cache fallback but the migration AC in Story 1.2 doesn't list it. Add to Story 1.2 or 1.6's AC.

---

### F. Acceptance Criteria Completeness Spot Check

Sampled 12 stories across all epics for AC quality:

| Story | Given/When/Then | Error Conditions | Measurable Thresholds | Verdict |
|---|---|---|---|---|
| 1.1 Monorepo Scaffold | ✅ | N/A (setup story) | `make dev` = single verifiable command ✅ | ✅ |
| 2.2 PIN Auth | ✅ | HTTP 429 on 5 failures ✅ | 4-hour expiry defined ✅ | ✅ |
| 2.3 Admin + TOTP Auth | ✅ | Rate limit, lockout, email unlock ✅ | TOTP app compatibility listed ✅ | ✅ |
| 3.3 Menu Management | ✅ | Shortcode uniqueness violation ✅ | Integer paise enforced ✅ | ✅ |
| 4.1 Bill Schema | ✅ | Invalid state transitions tested ✅ | 100% branch coverage required ✅ | ✅ |
| 4.5 Command Palette | ✅ | Unavailable items blocked ✅ | 50ms open, 100ms results ✅ | ✅ |
| 4.7 KOT Fire | ✅ | WebSocket offline queued ✅ | Delta-only dispatch ✅ | ✅ |
| 5.2 Payment Collection | ✅ | Amount mismatch HTTP 422 ✅ | Integer paise sum validated ✅ | ✅ |
| 7.4 Availability Control | ✅ | Re-enable flow tested ✅ | Propagation ≤ 3 seconds ✅ | ✅ |
| 9.3 Real-Time Alerts | ✅ | Retry/failure handling ✅ | Delivered within 60 seconds ✅ | ✅ |
| 10.5 GST Report | ✅ | Void stamps, exclusion audit ✅ | Sequential numbers unbroken ✅ | ✅ |
| 12.2 Co-Order Suggestions | ✅ | < 3 qualifying items handled ✅ | ≥20% threshold, 5ms Valkey read ✅ | ✅ |

**Conclusion:** AC quality is consistently high. BDD format is maintained. Measurable thresholds (ms, paise, percentages) are specified. Error conditions are covered. No vague acceptance criteria found.

---

## Summary and Recommendations

### Overall Readiness Status

**NEEDS WORK** — 4 significant issues require remediation before Sprint Planning. Epics 1–3 can begin immediately. Epics 4+ have a forward dependency that must be addressed.

---

### Issues Summary by Severity

| # | Severity | Issue | Blocking? |
|---|---|---|---|
| 1 | 🔴 Critical | WebSocket forward dependency: Epic 4 stories require infrastructure not set up until Epic 7 | Yes — affects Stories 4.7, 4.8, 5.5, 6.4 |
| 2 | 🟠 Major | Epic 3 missing schema story — no migration AC for menu/config domain tables | Yes — schema gaps before implementation |
| 3 | 🟠 Major | "Right Now" Valkey data pipeline undefined — FR62 partially unimplemented (Story 4.9) | Partial — feature will fail at runtime |
| 4 | 🟠 Major | FR Coverage Map in epics.md has stale pre-merge epic numbers | No — documentation only; readiness report is correct |
| 5 | ⚠️ Warning | Waiter Mode portrait UX not specified (W1) | No — pre-Sprint 11 only |
| 6 | ⚠️ Warning | Manager & Admin screens underspecified in UX doc (W2) | No — addressable during implementation |
| 7 | ⚠️ Warning | UX frontmatter `workflowStatus: in-progress` (W3) | No — documentation hygiene only |
| 8 | 🟡 Minor | `tenant_feature_flags` table not explicitly in migration AC | No — add to Story 1.2 or 1.6 |
| 9 | 🟡 Minor | FR71 stale mapping in epics.md FR coverage map | No — documentation only |

---

### Recommended Next Steps

1. **[Critical — Before Sprint 1 begins]** Add **Story 1.8 "WebSocket Service Bootstrap"** to Epic 1. Scope: connection manager, Valkey pub/sub router, WSS event envelope (`{ type, tenantId, payload, ts }`), exponential backoff reconnect (1s→2s→4s→max 30s). Refactor Story 7.1 to be kitchen-feature-specific only, built on the Story 1.8 infrastructure.

2. **[Critical — Before Epic 3 sprint begins]** Add **Story 3.0 "Menu, Configuration & Layout Schema"** to Epic 3 as the first story. Define `menu_items`, `menu_categories`, `sections`, `tables`, `gst_categories`, and `print_template_config` tables with full column-level migration ACs following the Story 4.1 pattern. Add `tenant_feature_flags` table here.

3. **[Major — Resolve before Story 4.9 sprint]** Choose an implementation path for FR62 ("Right Now"):
   - **Option A:** Extend Story 12.1 to populate `time:{tenant_id}:{hour}:{item_id}` Valkey keys; gate Story 4.9's "Right Now" AC on `suggestion_engine` flag.
   - **Option B:** Replace Story 4.9's Valkey query with a hot-partition COUNT SQL; remove Valkey dependency from this feature.

4. **[Major — Documentation fix]** Update the FR Coverage Map in epics.md to use post-merge epic numbers. Correct FR71 to Epic 8, Story 8.4.

5. **[Pre-Sprint 11]** Produce a Waiter Mode UX addendum: portrait-first screen layouts, bottom nav interaction patterns, 44px touch target specification for the mobile billing surface.

---

### What Is Already Strong

- ✅ 100% FR coverage across all 89 defined requirements — zero gaps
- ✅ Database-first story sequencing enforced across all feature epics (schema → service → API → UI)
- ✅ Integer paise money handling specified consistently across all domain schema stories
- ✅ TIMESTAMPTZ UTC enforced at schema level and documented in every relevant story
- ✅ Append-only audit log with DB trigger — locked in Story 1.2, reinforced throughout
- ✅ Telegram stub pattern correctly used for forward dependencies (Stories 4.8, 5.4, 6.1)
- ✅ Feature flag gating fully designed: Valkey cache, `<FeatureGate>` component, `useFeatureFlag()` hook
- ✅ BDD-format ACs with measurable thresholds and error conditions throughout
- ✅ Modular backend and frontend architecture enforced with no-cross-import rules in CI
- ✅ All performance NFRs (< 15s billing, < 100ms palette, < 3s KOT sync) referenced in relevant story ACs
- ✅ Security requirements (httpOnly cookies, RLS, rate limiting, lockout, TOTP) fully specified at AC level

---

### Final Note

This assessment identified **9 issues** across **3 categories** (epic structure, documentation accuracy, partial implementation). **4 issues require action before Sprint Planning**; the remaining 5 are advisory.

The epics are substantively sound, well-structured, and ready for story-level development once the 4 remediation items are addressed. The most impactful single fix is adding Story 1.8 (WebSocket bootstrap) to Epic 1 — this resolves the forward dependency for Stories 4.7, 4.8, 5.5, and 6.4 without restructuring any other epics.

**Report generated:** 2026-03-17
**Assessed by:** BMAD Implementation Readiness Check Workflow
**Input artifacts:** prd.md (complete), architecture.md (complete), epics.md (complete — 4 fixes required), ux-design-specification.md (substantively complete)

