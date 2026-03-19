---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish', 'step-12-complete']
workflowStatus: 'complete'
completedAt: '2026-03-12'
inputDocuments: ['_bmad-output/brainstorming/brainstorming-session-2026-03-12-1.md']
workflowType: 'prd'
briefCount: 0
researchCount: 0
brainstormingCount: 1
projectDocsCount: 0
classification:
  projectType: 'PWA'
  domain: 'general'
  domainNote: 'fintech-grade data integrity standards'
  complexity: 'high'
  projectContext: 'greenfield'
  tenancy: 'multi-tenant'
  userSurfaces: ['biller', 'admin', 'kitchen-display']
  printArchitecture: 'any-device → cloud → websocket → print-agent → printer'
  realtimeLayer: 'single WebSocket infrastructure'
  outOfScope: ['customer-facing display']
---

# Product Requirements Document - sphotel

**Author:** Gokul
**Date:** 2026-03-12

## Executive Summary

sphotel-billing is a multi-tenant, Progressive Web App restaurant billing platform built to replace PetPooja at sphotel and evolve into an AI-powered POS product for the Indian restaurant market. The system is designed around a single governing principle: **speed is survival** — every architectural and UX decision exists to minimize time between a customer's order and a printed token slip.

The platform targets three distinct users: the **Biller** (counter staff handling the full billing lifecycle under pressure), the **Admin** (owner with remote oversight via any device and Telegram), and the **Kitchen Display** (read-mostly tablet view for kitchen staff). A lightweight print agent runs locally on a restaurant machine, connecting to the cloud app via a secure WebSocket tunnel — enabling billing from any device (phone, tablet, laptop) without exposing the printer to the internet.

sphotel serves as the production lab: real traffic, real staff, real failures — giving the team the battle-tested foundation needed before the platform scales to other restaurants.

### What Makes This Special

PetPooja is a vendor. sphotel-billing is a platform the owner controls. That distinction drives every decision:

- **Keyboard-first, command-palette billing** — a trained biller completes a full bill in under 15 seconds without touching a mouse
- **Bill = KOT (one document model)** — eliminates the duplication between kitchen order and billing at the data model level, not just the UI
- **Cloud-hosted, offline-resilient** — IndexedDB fallback means internet outages are minor inconveniences, not business stoppages
- **Token slip model** — replaces a 3-print workflow with a single 6-line thermal slip, reducing paper consumption by 66%
- **Fintech-grade accountability** — immutable sequential bill numbers, post-print modification flags, two-person void approval, and full audit trails are structural, not optional
- **AI-ready architecture** — multi-tenant data model and modular design allow AI features (demand forecasting, anomaly detection, natural language reporting) to be layered in without re-architecture

## Project Classification

| Field | Value |
|-------|-------|
| **Project Type** | Progressive Web App (installable, offline-capable, fully responsive) |
| **Domain** | General — restaurant/hospitality operations |
| **Data Standards** | Fintech-grade integrity (immutable records, audit trails, GST-ready) |
| **Complexity** | High |
| **Project Context** | Greenfield |
| **Tenancy** | Multi-tenant (sphotel as tenant #1) |
| **User Surfaces** | Biller PWA · Admin PWA · Kitchen Display PWA |
| **Print Architecture** | Any device → Cloud → WebSocket tunnel → Local print agent → Printer |

## Success Criteria

### User Success

- A trained biller completes a full bill — items added, KOT fired, payment collected, token printed — in **under 15 seconds**
- Biller manages up to 10 simultaneous open bills without losing context; switching between bills takes one keystroke
- Printer never blocks the billing UI — print jobs are always asynchronous; a printer error never stops a biller from taking the next order
- A browser crash or internet drop causes zero bill re-entry — all active bill state recovers automatically on reload
- Kitchen staff receive KOT updates in real time; no shouting across the restaurant to confirm order status

### Business Success

- **The 3-month signal:** All 3 owners receive automated EOD summaries and live alerts on their phones — and none of them has had to manually tally cash, generate a report, or close the day by hand
- Every void request triggers an instant alert to all 3 owners before approval; no void goes unnoticed
- Every significant cash collection (configurable threshold) sends a live Telegram alert to all 3 owners
- Cash discrepancies are surfaced automatically — owners are notified of mismatches, not surprises
- Admin can audit any bill's full history — who created it, what changed, when, and who approved it — in under 30 seconds

### Technical Success

- **Zero data loss under any circumstance** — active bills survive browser crashes, internet outages, and server restarts via IndexedDB offline sync and 30-second snapshots
- Bill numbers are immutable and sequential — gaps are auto-flagged; voided bills retain their number with a VOID stamp (GST-ready)
- Daily encrypted backup to cloud storage with Telegram confirmation sent to all 3 owners
- Active bill queries resolve in **sub-10ms** (hot data layer)
- Menu availability changes propagate to all active terminals within **3 seconds**
- Print agent offline status triggers immediate Telegram alert to all 3 owners

### Measurable Outcomes

| Metric | Target |
|--------|--------|
| Bill completion time (trained biller) | < 15 seconds |
| Terminal sync latency (menu/KOT updates) | < 3 seconds |
| Active data query time | < 10ms |
| Data loss on crash/outage | Zero |
| Manual owner intervention for day-close | Zero |
| Void transparency | 100% — every void alerted to all 3 owners |

## User Journeys

### Journey 1: Ravi the Biller — Dinner Rush (Happy Path)

It's 8pm on a Friday. Ravi has 6 tables open simultaneously and a queue at the counter. He doesn't panic — he's done this before.

He hits `Ctrl+T` — a new bill tab opens. He types "CF 2 BT 1" into the command palette — Chicken Fried Rice ×2, Butter Tea ×1, added instantly. No clicking, no searching. He hits `Ctrl+K` — KOT fires to the kitchen. The tab flashes orange (KOT sent). He hits `F3` — jumps to Table 3's bill. Adds two more items. `Ctrl+K`. Back to `F1` for the counter queue.

Forty minutes later, Table 2 wants their bill. Ravi hits `F2`, `Ctrl+B` — bill generated. `Ctrl+P` — token slip prints in the background while he's already on `F5` taking the next order. The printer never once blocked his screen.

Cash collected at the counter. Ravi enters ₹500 cash + ₹340 UPI — split payment logged. `Ctrl+W` — bill closed. Total time from "bill please" to closed: 22 seconds.

**Requirements revealed:** Command palette, multi-tab management, F-key switching, KOT firing, async print, split payment, keyboard shortcut overlay.

---

### Journey 2: Ravi the Biller — The Crash (Edge Case)

Mid-service, the browser tab crashes. Ravi blinks. He reopens the tab. Three open bills restore automatically — exactly where he left them. One had a KOT pending — it shows as "unsent, queued." He confirms it fires. No order lost. No customer re-explains their food.

Ten minutes later, the internet drops. Ravi keeps billing. New bills create locally, KOTs queue. The tab header shows "Offline — syncing when reconnected." WiFi comes back four minutes later — everything flushes to the server silently. Bill numbers assigned by the server in sequence. No gaps, no duplicates.

**Requirements revealed:** IndexedDB offline sync, crash recovery, offline bill creation, auto-reconnect sync, bill locking, offline mode indicator.

---

### Journey 3: Priya the Waiter — Optional Device Mode

Priya has her own Android phone and has been given a Waiter PIN. She opens the billing PWA, taps "Waiter Mode" — her ID (Priya-W03) is auto-loaded. No dropdown, no search.

She's at Table 7. She opens a new bill — Table 7 auto-tagged to her. She adds starters, hits "Send KOT." Kitchen sees the order. Twenty minutes later, mains — she adds them, hits "Send KOT" again. Delta update only reaches the kitchen.

When the table is ready to pay, she taps "Send to Counter." The bill appears on the Biller's screen as a tab — T7, owned by Priya-W03, ready for payment. Ravi collects cash, prints token, closes it. Priya's stats update automatically.

If Priya doesn't have her phone tonight, nothing changes. Ravi handles Table 7 exactly as always and types "Priya" at bill creation.

**Requirements revealed:** Waiter Mode PWA (simplified Biller view), auto-ID selection on login, bill transfer to counter, optional mode with graceful fallback, waiter performance auto-tracking.

---

### Journey 4: Chef Kumar — Kitchen Display

Chef Kumar's tablet is mounted on the kitchen pass. As KOTs arrive, they appear as cards — Table number, waiter name, items, timestamp. No paper. No shouting.

He marks "Butter Chicken ×2" as ready — the item gets a green tick. When the full order is ready, he taps "Table 5 Ready." A subtle notification badge appears on Ravi's billing tab for T5.

If an item is unavailable, Chef Kumar taps it and marks "86'd" — it grays out immediately on every billing terminal. No biller accidentally adds it.

**Requirements revealed:** Kitchen Display PWA, live KOT feed, per-item ready marking, table-ready notification to Biller, real-time item availability control from kitchen.

---

### Journey 5: Gokul the Admin — From Home

It's 11:15pm. Gokul is at home. His Telegram gets a message:

> 📊 **sphotel EOD — March 12**
> Bills: 84 | Gross: ₹62,340 | Cash: ₹38,200 | UPI: ₹24,140
> Voids: 2 (approved) | Top item: Chicken Biryani ×47
> Waiter performance: Priya 31 bills · Raju 28 bills · Anand 25 bills
> Backup: ✅ Complete (4.1MB, 84 bills archived)

He taps the void line — sees both voids with reason, requester, and approver. Everything adds up. He puts his phone down.

Earlier at 9pm, he got: "⚠️ Void requested: Table 11 — Masala Dosa ×1 by Ravi. Approve?" He tapped Approve from Telegram. Done.

Tomorrow he logs into the Admin PWA to adjust menu prices before lunch. He downloads the current menu as CSV, edits 8 prices in Excel, re-uploads. Diff preview shows "8 changed." He confirms. All billing terminals update within 3 seconds.

The next morning, before opening, Gokul's Telegram has one more message from the previous night: "✅ Backup complete — 4.1MB, 84 bills archived, encrypted." He doesn't need to think about it. It's just there.

**Requirements revealed:** Multi-owner Telegram (×3 recipients), EOD auto-report, live void approval via Telegram, menu CSV import/export, diff preview, live terminal sync, daily encrypted backup confirmation.

---

### Journey 6: Gokul the Super-Admin — Onboarding a New Tenant

Six months later. A restaurant owner, Meena (Spice Garden, Coimbatore), wants to try the platform.

Gokul logs into the Super-Admin panel. He creates a new tenant — "spicegarden" — sets an Admin account for Meena, and assigns a plan. Meena gets an onboarding email with her URL (`spicegarden.billing.app`) and a setup checklist: add menu, add staff, configure print agent, set reward rules.

Meena's data is fully isolated from sphotel's. Gokul can see aggregate platform stats — total tenants, total bills processed today — but never sees individual tenant data.

**Requirements revealed:** Super-admin tenant management panel, tenant isolation, onboarding checklist, per-tenant URL routing, aggregate platform analytics (no cross-tenant data access).

---

## Domain-Specific Requirements

### GST & Tax Compliance

- GST not displayed on individual bills — calculated at submission/reporting time on the total
- GST formula fully configurable per tenant (rate, slab, applicable categories)
- Admin can exclude specific bills or adjust reported values for GST submission
- GST report exportable with sequential bill numbers, included totals, excluded bills flagged separately
- No PCI-DSS requirements — payment method and amount recorded, not processed

### Role Model

| Role | Access Scope |
|------|-------------|
| **Biller** | Full billing lifecycle — items, KOT, payment, print, close. Void request only. |
| **Waiter** *(optional)* | Own-device order taking, KOT firing, bill handoff to counter |
| **Kitchen Staff** | KOT feed, item ready marking, item availability control |
| **Manager** | Attendance entry, staff list, payroll view, supplier expense entry |
| **Admin** | All above + menu, void approval, GST report, Telegram config, financial reports, operations dashboard |
| **Super-Admin** | Tenant management, platform analytics, onboarding |

- Role-specific URL paths and screen layouts — each role sees only what's relevant
- Manager and Admin share the same app entry point (`/admin`), differentiated by permission scope after login
- PIN-based login for all operational roles (Biller, Waiter, Kitchen Staff, Manager)
- Admin and Super-Admin use full credential login (email + password + short-lived session token)

### Staff Management & Payroll

- Attendance **manually entered by Manager or Admin** per shift — who worked, which shift
- Reward formula configurable per tenant — percentage, flat, hybrid, or custom
- Auto-calculation at shift/day close — earned rewards per waiter based on bills + formula
- Manager sees payroll view: attendance + bills handled + calculated payout per staff member
- Admin sees same payroll view plus approval capability
- Payroll summary in EOD Telegram report to all 3 owners

### Supplier Expense Tracking

- Manager or Admin records supplier invoices — vendor name, category, amount, date, payment method
- Expenses tracked alongside revenue — daily/weekly in vs out visible to Admin
- Configurable supplier/vendor directory per tenant
- Expense summary in EOD report and historical analytics

### Operations Dashboard *(Admin only)*

- **Live view** — open bills, KOT pipeline, staff on duty, printer agent status
- **Historical analytics** — revenue trends, peak hours, top items, waiter performance, void rates, expense vs revenue

### Configurable Formulas (Per Tenant)

| Formula | Configurable By |
|---------|----------------|
| GST rate and reporting rules | Admin |
| Waiter reward formula | Admin |
| Cash alert threshold | Admin |
| Supplier category list | Admin or Manager |

---

## Innovation & Novel Patterns

### Detected Innovation Areas

**1. Bill = KOT: One Document, Two States**
The fundamental duplication in every existing POS system — billing and kitchen order as separate workflows — is eliminated at the data model level. A bill in draft state IS the KOT. Firing to kitchen changes its state. Finalizing for payment changes it again. One document, one source of truth, zero re-entry. This isn't a UI simplification — it's an architectural rethinking of how a restaurant transaction flows.

**2. Cloud-to-Local Printing via WebSocket Tunnel**
The hardest problem in cloud-hosted restaurant POS: the printer is local, the app is cloud. The solution — a lightweight agent on the restaurant machine that opens a persistent outbound WebSocket to the cloud — means no port forwarding, no firewall changes, no network configuration. The cloud queues print jobs; the agent flushes them. Any device on any network can trigger a print without ever knowing where the printer is. This pattern is novel in the restaurant POS space.

**3. Command Palette Billing (Cross-Domain UX Pollination)**
Developer tooling UX (VS Code command palette, Bloomberg terminal keyboard-first workflows) applied to restaurant billing. A biller who never touches a mouse, navigates menus, or waits for dropdowns — operating entirely via typed shortcodes and keyboard shortcuts. This mental model shift — from "POS as a form" to "POS as a command interface" — is the primary speed differentiator.

**4. Waiter Mode as Optional Graceful Overlay**
Most POS systems require full participation from all roles to function. This system is designed so waiter participation improves the experience but is never required. If a waiter has a phone and logs in, they take orders at the table — bills flow to the counter seamlessly. If they don't, the Biller handles it exactly as before. The system degrades gracefully to its baseline without any workflow change.

**5. AI-First Multi-Tenant Architecture**
Building a restaurant POS where the multi-tenant data model and modular architecture are designed from day one to accept AI layers — demand forecasting, anomaly detection on voids and cash, natural language reporting — without re-architecture. Most restaurant software adds AI as a bolt-on. This system treats AI as a planned evolution, not an afterthought.

### Market Context & Competitive Landscape

- PetPooja, Posist, and similar Indian POS systems are click-first, locally-installed or hybrid, and treat billing and KOT as separate workflows
- No major Indian restaurant POS offers keyboard-first command palette billing
- Cloud-hosted POS with offline-first resilience is rare in the Indian SMB restaurant market
- The WebSocket print agent pattern is used in enterprise printing but not in Indian restaurant POS
- AI integration in Indian restaurant software is nascent — mostly limited to analytics dashboards bolted onto existing systems

### Validation Approach

| Innovation | Validation Method |
|-----------|------------------|
| Bill = KOT model | Measure re-entry errors and KOT confusion during first 2 weeks at sphotel |
| Command palette billing | Time trained billers: target < 15 seconds per bill within 1 week of training |
| WebSocket print tunnel | Stress test: 100 print jobs in 10 minutes, agent disconnect/reconnect scenarios |
| Waiter Mode overlay | Run sphotel for 1 month with and without waiter participation — measure counter load |
| AI-ready architecture | Validate by successfully adding first AI feature without schema migration |

### Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Command palette has learning curve | `?` key hotkey overlay, onboarding checklist, shortcode printed above counter |
| Print agent goes offline | Queue on cloud, flush on reconnect; Telegram alert within 60 seconds of disconnect |
| Bill = KOT model confuses kitchen staff | Kitchen Display shows clear state labels (Draft / KOT Sent / Billed); training before go-live |
| Waiter Mode creates sync conflicts | Optimistic locking on bills; "Bill locked by [user]" shown on second device |
| AI layer requires data volume | Multi-tenant model accumulates cross-restaurant data over time — AI improves with scale |

## PWA-Specific Requirements

### Project-Type Overview

sphotel-billing is a Single Page Application (SPA) built as a fully installable Progressive Web App. There is no server-side rendering or MPA — the app shell loads once and all navigation is client-side. Each role surface (Biller, Waiter, Kitchen, Admin/Manager) is a distinct view within the same PWA, optimized for its target device class but fully functional on any device.

### Role-Based Device Matrix

Every role surface is fully responsive across all breakpoints — phone, tablet, desktop. The "primary optimization" determines the default layout and interaction model. On other device sizes, the UI adapts without losing functionality.

| Role Surface | Primary Optimization | Also Fully Functional On |
|-------------|---------------------|--------------------------|
| **Biller** | Desktop / laptop (keyboard-first) | Tablet, mobile (touch fallback) |
| **Waiter Mode** | Mobile (portrait, one-handed) | Tablet, desktop |
| **Kitchen Display** | Tablet landscape (large cards) | Mobile, desktop |
| **Manager** | Desktop or tablet | Mobile |
| **Admin** | Mobile (remote monitoring) + desktop (config) | All devices |
| **Super-Admin** | Desktop | Tablet, mobile |

- Keyboard shortcuts are accelerators, not requirements — all actions accessible via touch/mouse
- Kitchen Display on mobile: cards stack vertically, touch targets remain large
- Admin on mobile: data tables become scrollable card lists
- PWA installed to home screen on all shared devices
- Minimum OS: Android 9+, iOS 14+, Windows 10+, macOS 11+
- Browser support: Chrome, Firefox, Safari, Edge (latest 2 versions each)

### Responsive Design

- **Four breakpoints:** mobile (< 640px), tablet (640–1024px), desktop (1024–1440px), wide (> 1440px)
- Each role surface has a layout optimized for its primary breakpoint — not a one-size-fits-all layout
- Biller view: optimized for 1024px+ landscape; adapts to tablet and mobile
- Kitchen Display: optimized for tablet landscape; large card layout, min 18px font, min 56px touch targets
- Waiter Mode: optimized for mobile portrait; thumb-reachable action buttons, min 44px touch targets
- Admin/Manager: fully responsive — mobile for monitoring, desktop for data entry and config

### Performance Targets

| Metric | Target |
|--------|--------|
| First Contentful Paint (app shell) | < 1.5 seconds on 4G |
| Time to Interactive (billing screen) | < 2 seconds on 4G |
| Active bill query response | < 10ms (hot data layer) |
| Menu/KOT sync propagation | < 3 seconds across all terminals |
| Offline fallback activation | < 500ms after connection loss detected |
| Print job queue flush on reconnect | < 5 seconds for queued jobs |

### Real-Time Architecture

- Single WebSocket connection per client session — handles: KOT updates, menu availability changes, bill locking, kitchen ready notifications, print job dispatch, admin broadcasts
- Reconnect strategy: exponential backoff (1s → 2s → 4s → max 30s)
- Offline mode: WebSocket loss triggers IndexedDB-only mode; visible indicator in UI
- No polling — all live updates are push-based via WebSocket

### SEO Strategy

- Not applicable — internal tool, all routes require authentication, no public pages

### Accessibility

Role-optimized for each environment:

| Role Surface | Accessibility Requirements |
|-------------|--------------------------|
| **Biller** | Dark mode + high contrast; full keyboard navigation; `?` key shortcut overlay |
| **Kitchen Display** | Min 56px touch targets; high contrast for bright kitchen; min 18px font size |
| **Waiter Mode** | Min 44px touch targets; thumb-friendly layout in portrait mode |
| **Admin / Manager** | WCAG AA contrast; responsive table layouts; accessible form labels |

- All surfaces support system dark/light mode preference
- No time-limited interactions without warning

### Service Worker & Offline Strategy

- Service worker caches: app shell, menu data, active bill state, staff list
- IndexedDB stores: all open bills, pending KOT queue, pending print queue, menu snapshot
- Cache invalidation: menu and staff data refresh on WebSocket reconnect
- PWA install prompt shown after first successful login on any device

### Implementation Considerations

- React SPA with role-based route protection
- PWA manifest with role-specific install icons (Biller, Kitchen, Admin)
- Single WebSocket client shared across the app — multiple event channels
- Print agent communication handled server-side — client never communicates with agent directly
- Waiter Mode: simplified Biller view with auto-identity injection on login

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Complete Production Replacement
This is not a proof-of-concept MVP — it is a full PetPooja replacement that sphotel goes live on. The MVP must be complete enough to handle every aspect of daily restaurant operations from day one: billing, kitchen flow, printing, staff management, owner visibility, and financial accountability.

**Rationale:** sphotel is the production lab. Shipping an incomplete system creates operational risk for a live restaurant. The MVP is intentionally large because the bar is "replace what we have and do it better," not "validate an assumption."

**Resource Requirements:** Full-stack team with React PWA + backend expertise, WebSocket experience, and local agent (print agent) development capability.

### MVP Feature Set (Phase 1)
*Everything ships before sphotel goes live.*

**Core User Journeys Supported:**
- Ravi (Biller) — full billing lifecycle, happy path and crash recovery
- Priya (Waiter) — optional device mode with graceful fallback
- Chef Kumar (Kitchen Display) — KOT feed and item management
- Manager — attendance entry, payroll view, supplier expense tracking
- Admin (×3 owners) — full oversight, Telegram visibility, menu management, void approval
- Super-Admin — tenant provisioning for sphotel as tenant #1

**Must-Have Capabilities:**

*Billing Engine:*
- Fuzzy search + shortcodes + command palette (Space bar)
- Browser-tab multi-bill interface + F1–F10 hotkey switching
- Watchlist-style active bills sidebar
- Bill = KOT (one document, two states) with partial firing and delta-only updates
- Void/cancel with reason logging; Biller requests, Admin approves
- Keyboard shortcut overlay (`?` key)

*Printing:*
- Local print agent via WebSocket tunnel
- Async print queue (never blocks UI)
- Token slip only — 6 lines, no QR code
- Ctrl+P reprint any closed bill
- Print agent offline Telegram alert to all 3 owners

*Roles & Access:*
- Biller, Waiter (optional mode), Kitchen Staff, Manager, Admin, Super-Admin
- PIN-based login for operational roles; credential login for Admin/Super-Admin
- Role-specific screen layouts and URL entry points
- Admin-only void approval; Biller cannot delete KOT-fired items

*Cash & Payments:*
- Cash sessions per shift (opening balance → expected vs actual)
- Split payment methods (cash + UPI + card on one bill)
- Post-print modification flagging
- Immutable sequential bill numbers (GST-ready)
- Cash discrepancy auto-alert to all 3 owners

*Menu Management:*
- Table-based inline editing UI
- CSV bulk import/export with diff preview
- Live item availability flags (kitchen-controlled)
- Updates propagate to all terminals within 3 seconds

*KOT Pipeline:*
- Kitchen Display PWA — real-time KOT feed, per-item ready marking
- Kitchen-to-Biller ready notification
- Item availability control from Kitchen Display

*Staff & Payroll:*
- Manual attendance entry per shift by Manager or Admin
- Configurable reward formula per tenant
- Auto reward calculation at shift/day close
- Admin payroll view — attendance + bills + calculated payout per staff member

*Supplier Expense Tracking:*
- Manager or Admin records supplier invoices
- Configurable vendor/category directory per tenant
- Expense summary in EOD report and analytics

*Operations & Analytics:*
- Live operations dashboard — open bills, KOT pipeline, staff on duty, printer status
- Historical analytics — revenue trends, peak hours, top items, waiter performance, void rates, expense vs revenue

*Telegram Integration:*
- Auto EOD report to all 3 owners
- Live alerts: large payments, voids, printer offline, cash discrepancy, payroll summary
- Daily encrypted backup confirmation to all 3 owners

*GST & Compliance:*
- Configurable GST formula per tenant (rate, slab, categories)
- Bill inclusion/exclusion control for GST reporting
- Exportable GST report

*Infrastructure:*
- Multi-tenant data architecture (sphotel as tenant #1)
- IndexedDB offline fallback + 30-second crash recovery snapshots
- Auto offline detection with queued sync on reconnect
- HTTPS + short-lived session tokens + 4-hour auto-logout
- Daily encrypted backup to cloud storage (90-day retention)
- Concurrent edit protection (bill locking)

*Super-Admin:*
- Tenant provisioning and management panel
- Tenant isolation with aggregate platform analytics
- Onboarding checklist for new tenants

### Post-MVP Features (Phase 2)
*After stable launch with real usage data from sphotel.*

- Waiter reward auto-calculation visible to waiters on their own login
- Kitchen Display lifecycle states (Sent → Acknowledged → Ready → Served)
- Telegram bot control panel (`/sales`, `/void`, `/open`)
- Admin broadcast message to all terminals
- Bill merge/split (Ctrl+M)
- One-Click Day Close
- Print agent status panel + multi-printer routing (counter vs kitchen)
- Bill aging alerts (45 min idle)
- Waiter performance dashboard with weekly leaderboard

### Vision (Phase 3)
*When sphotel-billing becomes a product sold to other restaurants.*

- AI demand forecasting and menu optimization
- AI anomaly detection on voids and cash patterns
- Natural language reporting via Telegram bot
- Multi-location branch system with consolidated reports
- Self-serve SaaS onboarding for new restaurant tenants
- Loyalty points module
- Hotel room linking add-on
- Inventory ingredient tracking

### Risk Mitigation Strategy

| Risk | Mitigation |
|------|-----------|
| **MVP scope is large** | sphotel is a controlled environment — launch billing core first, enable other modules progressively |
| **WebSocket print tunnel reliability** | Stress testing pre-launch; print queue survives agent restart; Telegram alert on disconnect |
| **Offline sync conflicts** | Optimistic locking; server assigns sequential bill numbers on reconnect; conflict resolution favors server state |
| **Staff adoption (keyboard-first)** | Hotkey overlay, printed shortcode card above counter, 1-day training session before go-live |
| **Multi-tenant data isolation** | Tenant ID scoped at DB query level from day one; no cross-tenant data access possible by design |
| **Second tenant before system is stable** | No second tenant onboarded until sphotel has run stably for 90 days |

## Functional Requirements

### Billing & Order Management

- **FR1:** Biller can create a new bill and add menu items via fuzzy text search
- **FR2:** Biller can add menu items via character shortcodes (e.g. `CF` = Chicken Fried Rice) or numeric codes (e.g. `14x2` = item 14, quantity 2)
- **FR3:** Biller can add menu items via a command palette triggered by a keyboard shortcut
- **FR4:** Biller can manage up to 10 simultaneous open bills via a tab interface; the maximum is configurable per tenant by Admin
- **FR5:** Biller can switch between open bills via F-key hotkeys
- **FR6:** Biller can view all active bills in a persistent sidebar panel showing table, item count, time open, and running total
- **FR7:** Biller can fire a KOT for items on a bill, sending only items not yet dispatched to the kitchen
- **FR8:** Biller can fire partial KOTs — sending some items immediately and holding others for a later fire
- **FR9:** Biller can request a void for KOT-fired items (requires Admin approval before removal)
- **FR10:** Biller cannot modify or delete KOT-fired items without explicit Admin approval
- **FR11:** Waiter (optional mode) can create and manage bills on their own device with their identity auto-loaded on login
- **FR12:** Waiter can transfer a finalized bill to the billing counter for payment collection
- **FR13:** System assigns immutable sequential bill numbers; voided bills retain their number with a VOID stamp; gaps are auto-flagged
- **FR61:** Biller can access a keyboard shortcut overlay displaying all available shortcuts
- **FR62:** System surfaces menu items relevant to the current time of day in a dedicated "Right Now" section displayed above the main billing search results
- **FR63:** Biller can save and trigger bill templates (preset item combinations) via a keyboard shortcut
- **FR69:** System suggests up to 3 items that have been co-ordered with the added item in at least 20% of past orders, displayed inline below the added item
- **FR79:** Billing search surfaces the top 5 most frequently ordered items (all-time) and the top 5 most recently added items in the current session, displayed above main search results

### Kitchen & KOT Management

- **FR14:** Kitchen Staff can view all active KOTs in real time on the Kitchen Display
- **FR15:** Kitchen Staff can mark individual items as ready on an active KOT
- **FR16:** Kitchen Staff can mark a full table order as ready, triggering a notification on the Biller's active tab for that table
- **FR17:** Kitchen Staff can mark menu items as unavailable, propagating the change to all billing terminals in real time
- **FR18:** System sends only delta updates to the kitchen on KOT modification — added or changed items only, not a full reprint

### Payment & Cash Management

- **FR19:** Biller can collect payment for a bill split across multiple payment methods (cash, UPI, card) in a single transaction
- **FR21:** System predicts expected cash balance at shift close; Biller confirms match or flags discrepancy — investigation triggered only on mismatch
- **FR22:** System automatically flags and logs any bill modified after printing as "amended" in the audit record
- **FR23:** Admin can view the complete audit history of any bill including all changes, timestamps, and actors
- **FR76:** Biller can apply a discount or mark a bill as complimentary with a reason, subject to configurable Admin approval rules
- **FR77:** Manager or Biller can formally open and close a shift, gating cash session creation and payroll period tracking
- **FR82:** Biller or Admin can correct a payment method record post-collection with reason logging

### Printing

- **FR24:** System queues and dispatches print jobs to a locally installed print agent without blocking the billing UI
- **FR25:** Biller can reprint any closed bill on demand via keyboard shortcut
- **FR26:** Print agent maintains a job queue when offline and flushes all queued jobs automatically on reconnect
- **FR27:** Admin can register, view status of, and manage print agents from the Admin panel
- **FR65:** Print agent authenticates with the cloud server via an Admin-generated one-time token
- **FR78:** Admin can configure the token slip print template per tenant (restaurant name, fields displayed)

### Menu Management

- **FR28:** Admin can manage menu items via an inline table-editing interface (name, category, price, availability, GST category)
- **FR29:** Admin can bulk import and export the menu as a CSV file, with a diff preview before applying changes
- **FR30:** Admin can reorder menu categories and items, with order reflected in billing search and display
- **FR31:** Availability changes made by Kitchen Staff or Admin propagate to all active billing terminals within 3 seconds
- **FR75:** Admin can configure the restaurant's table and section layout used for bill assignment

### User & Access Management

- **FR32:** System enforces six distinct roles with non-overlapping capability boundaries: Biller, Waiter, Kitchen Staff, Manager, Admin, Super-Admin
- **FR33:** Operational roles (Biller, Waiter, Kitchen Staff, Manager) authenticate via PIN; each action is tagged to the authenticated PIN holder
- **FR34:** Admin and Super-Admin authenticate via email/password credentials with short-lived session tokens (4-hour expiry, auto-invalidated on browser close for shared devices)
- **FR35:** Admin can approve or reject Biller void requests; every void is logged with requester, approver, reason, and timestamp
- **FR36:** Every bill, KOT action, payment, and void is permanently tagged to the authenticated user who performed it
- **FR37:** All sessions auto-expire after 4 hours of inactivity
- **FR64:** System prevents concurrent edits to the same bill by displaying a lock indicator showing which user holds the bill
- **FR74:** Admin can create, edit, deactivate, and reset PINs for all staff accounts
- **FR87:** System prevents any user from granting permissions equal to or higher than their own role level
- **FR89:** Each role has explicit data visibility boundaries — Billers see only their own session data; Managers see staff data but not financial reports; Admins see everything within their tenant
- **FR90:** Admin and Super-Admin can change their own credentials; Super-Admin can reset any Admin's credentials
- **FR93:** Admin and Super-Admin logins support TOTP-based two-factor authentication via any standard authenticator app

### Staff Management & Payroll

- **FR38:** Manager or Admin can manually record staff attendance per shift (who worked, which shift)
- **FR39:** Admin can configure reward calculation formulas per tenant (percentage, flat rate, hybrid, or custom)
- **FR40:** System auto-calculates earned rewards per staff member at shift or day close based on the configured formula
- **FR41:** Manager and Admin can view a payroll summary showing attendance, bills handled, total value billed, and calculated payout per staff member per period
- **FR71:** Waiter can view their own performance stats (bills served, total value, shift summary) on login

### Supplier Expense Tracking

- **FR42:** Manager or Admin can record supplier invoices with vendor name, category, amount, date, and payment method
- **FR43:** Admin can manage a configurable vendor and expense category directory per tenant
- **FR44:** System includes supplier expense data in EOD Telegram reports and historical analytics

### Notifications & Telegram

- **FR45:** System automatically sends a daily EOD summary to the configured tenant Telegram group at a configurable time
- **FR46:** System sends real-time Telegram alerts to the tenant owner group for: void requests, large cash payments (above configurable threshold), cash discrepancies, and print agent going offline
- **FR47:** System sends a daily encrypted backup confirmation message to the tenant owner Telegram group
- **FR48:** Admin configures Telegram integration by adding a single group chat ID per tenant — a bot posts all alerts and EOD reports to the shared owner group

### Operations & Analytics

- **FR49:** Admin can view a live operations dashboard showing open bills, KOT pipeline status, staff currently on duty, and printer agent connectivity status
- **FR50:** Admin can view historical analytics including revenue trends by period, peak hour patterns, top items by volume and value, waiter performance over time, void rate trends, and expense vs revenue comparisons
- **FR73:** Admin can view a per-bill status timeline showing key timestamps (opened, KOT sent, bill generated, payment collected)
- **FR80:** Admin can search bill history by bill number, table, waiter, date range, and amount
- **FR81:** Admin can export operational reports (daily revenue summary, payroll report, supplier expense ledger) as CSV or PDF

### GST & Compliance

- **FR51:** Admin can configure GST rates, slab structures, and applicable item categories per tenant
- **FR52:** Admin can include or exclude specific bills from the GST report, with excluded bills flagged separately in the export
- **FR53:** System generates an exportable GST report with sequential bill numbers, included totals, and an audit-ready excluded bill record

### Offline Resilience & Data Integrity

- **FR54:** System continues to accept bill creation and modification when internet connectivity is unavailable, storing data locally on the device
- **FR55:** System automatically syncs locally stored data to the server upon reconnection, with the server assigning sequential bill numbers to offline-created bills
- **FR56:** System automatically recovers all active bill state after a browser crash without requiring re-entry by the user
- **FR66:** System displays a persistent offline mode indicator when operating without server connectivity
- **FR67:** System provides audio feedback for key billing events (item added, KOT sent, payment received)

### Security

- **FR83:** System logs all Admin and Manager configuration changes with timestamp and actor
- **FR84:** System enforces rate limiting and account lockout after 5 consecutive failed login attempts for any role; locked accounts require Admin reset for staff roles or email-based reset for Admin/Super-Admin
- **FR85:** Admin can immediately invalidate all active sessions for any staff member
- **FR86:** System encrypts sensitive data (financial records, payroll, payment data) at rest in the database
- **FR88:** All WebSocket connections use WSS (TLS-encrypted) — plain WS is not permitted

### Tenant & Platform Management

- **FR57:** Super-Admin can provision new tenants with isolated data environments, per-tenant URL routing, and an Admin account
- **FR58:** Super-Admin can view aggregate platform analytics (total tenants, total bills processed) without accessing any individual tenant's data
- **FR59:** System enforces complete data isolation between tenants at the database query level
- **FR60:** New tenants are guided through initial system configuration via an onboarding checklist on first login
- **FR72:** Users can set a display theme preference (dark mode / high contrast / light)
- **FR92:** Admin can export a complete data archive of all tenant data (bills, staff, expenses, reports) for portability
- **FR94:** System retains bill records and audit logs in a hot/archive two-layer architecture — live database holds a rolling week of active data; archive database retains complete historical records for a minimum configurable period (default 7 years) for GST compliance
- **FR95:** Suggestion engine data (item co-occurrence, order frequency, time-based patterns) is maintained in a separate read-optimised datastore with no read/write impact on the live billing database

## Non-Functional Requirements

### Performance

Speed is the primary differentiator. Every target below is derived from user success criteria established in this PRD.

| Metric | Target | Rationale |
|--------|--------|-----------|
| Bill completion time (trained biller) | < 15 seconds end-to-end | Core success criterion |
| Active bill / menu query response | < 10ms | Hot data layer — today's data only |
| KOT and menu sync propagation | < 3 seconds across all terminals | Real-time kitchen coordination |
| App shell First Contentful Paint | < 1.5 seconds on 4G | Staff daily login experience |
| Billing screen Time to Interactive | < 2 seconds on 4G | Counter readiness under pressure |
| Offline mode activation | < 500ms after connection loss | Staff must not notice the switch |
| Print queue flush on reconnect | < 5 seconds for all queued jobs | No delayed receipts post-outage |
| Command palette response | < 100ms from keystroke to results | Keyboard-first UX requires instant feedback |
| WebSocket reconnect (exponential backoff) | 1s → 2s → 4s → max 30s | Predictable recovery behavior |

- Hot database layer serves only the rolling week of active data — query performance is guaranteed regardless of historical data volume
- Suggestion engine datastore is read-only and separate from the billing database — zero query contention

### Security

**Authentication & Access:**
- All Admin and Super-Admin logins require TOTP two-factor authentication
- All roles enforce rate limiting — account locked after 5 consecutive failed attempts; staff role accounts require Admin reset; Admin/Super-Admin accounts unlock via email reset
- All session tokens are short-lived (configurable, default 4-hour expiry); no persistent tokens stored on device
- Sessions auto-invalidate on browser close for Admin roles on shared devices

**Encryption:**
- All data in transit encrypted via TLS 1.2+ (HTTPS and WSS — no HTTP or plain WS permitted)
- All sensitive data at rest encrypted in the database (financial records, payroll, payment records, audit logs)
- Daily backups encrypted before upload to cloud storage
- Print agent communication encrypted end-to-end via WSS tunnel

**Authorisation:**
- Tenant data isolation enforced at database query level — every query scoped by tenant ID
- Role permissions enforced server-side — client-side role checks are UI conveniences only
- No user can grant permissions at or above their own role level
- Each role has explicit read/write boundaries enforced at the API layer

**Audit & Compliance:**
- Every financial action permanently logged with actor, timestamp, and context — immutable
- Every Admin and Manager configuration change logged
- Audit logs retained per configured retention policy (default 7 years) in archive database
- Voided bills never deleted — retained with VOID stamp and sequential number

**Infrastructure:**
- CORS policy restricts API access to known application origins
- All API endpoints protected against common injection attacks (SQL injection, XSS, CSRF)
- Super-Admin access to platform admin panel logged with IP and timestamp

### Reliability

| Scenario | Requirement |
|----------|------------|
| Internet outage | Zero billing interruption — IndexedDB offline mode activates within 500ms |
| Browser crash | All active bill state recoverable on reload — zero re-entry required |
| Server downtime | Active bills on client devices survive independently; sync on reconnect |
| Print agent offline | Jobs queued on server; flushed on reconnect; Telegram alert within 60 seconds |
| Data loss | Zero — no bill, payment, or audit record lost under any failure scenario |
| Daily backup | Encrypted backup completes nightly; failure triggers Telegram alert to all owners |

- Target uptime: 99.5% monthly (excluding planned maintenance windows)
- Planned maintenance: communicated to Admin via Telegram at least 24 hours in advance
- Recovery point objective (RPO): maximum 30 seconds of data loss (snapshot interval)
- Recovery time objective (RTO): system recoverable within 15 minutes of infrastructure failure

### Scalability

- **Tenant isolation:** Each tenant's data fully isolated at database level — adding tenants has zero impact on existing tenant performance
- **Horizontal scaling:** Application layer stateless — multiple instances deployable behind a load balancer; WebSocket connections handled by a dedicated real-time service
- **Data volume:** Hot/archive split ensures live database size stays bounded regardless of historical bill volume
- **Concurrent users per tenant:** Designed for up to 20 concurrent active sessions per tenant
- **Multi-tenant growth:** Architecture supports 100+ tenants without infrastructure re-design
- **Suggestion engine:** Scales independently — separate datastore, separate service, no coupling to billing performance

### Accessibility

| Role Surface | Standard |
|-------------|---------|
| Biller | Full keyboard navigation; no mouse-only actions; `?` overlay for discoverability |
| Kitchen Display | Minimum 56px touch targets; minimum 18px font; high contrast for bright kitchen lighting |
| Waiter Mode | Minimum 44px touch targets; one-handed portrait usability |
| Admin / Manager | WCAG AA contrast ratios; accessible form labels; responsive data tables |
| All surfaces | System dark/light mode preference respected; no time-limited interactions without warning |

### Integration

| Integration | Requirement |
|------------|------------|
| **Telegram Bot API** | Reliable message delivery to group; graceful retry on API failure; no message loss for financial alerts |
| **Print Agent (WebSocket)** | Persistent WSS connection; auto-reconnect with job queue preservation; one-time token authentication |
| **Cloud Storage (Backup)** | Daily encrypted upload; S3-compatible API (AWS S3, Cloudflare R2) |
| **CSV Import/Export** | Standard UTF-8 CSV; consumable by Excel and Google Sheets without formatting issues |
| **TOTP** | Compatible with all standard authenticator apps (Google Authenticator, Authy, Microsoft Authenticator) |
