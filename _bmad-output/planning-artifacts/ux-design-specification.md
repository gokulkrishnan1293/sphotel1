---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-03-core-experience', 'step-04-emotional-response', 'step-05-inspiration', 'step-06-design-system', 'step-07-defining-experience', 'step-08-visual-foundation']
workflowStatus: 'in-progress'
startedAt: '2026-03-13'
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/architecture.md'
  - '_bmad-output/brainstorming/brainstorming-session-2026-03-12-1.md'
project_name: 'sphotel'
user_name: 'Gokul'
date: '2026-03-13'
---

# UX Design Specification - sphotel

**Author:** Gokul
**Date:** 2026-03-13

---

## Executive Summary

### Project Vision

sphotel-billing is a keyboard-first, multi-tenant PWA restaurant billing platform replacing PetPooja. The single governing UX principle: **speed is survival** — every design decision minimises time between an order and a printed token slip. The system is cloud-hosted, offline-resilient, and built around a single unified app shell where role-based access controls what each user sees — not separate applications.

### Target Users

| Role | Primary Job | Device | Access |
|---|---|---|---|
| **Biller** | Full billing lifecycle — items, KOT, payment, print, close. Void request only. | Desktop/laptop (keyboard-first) | PIN login |
| **Manager** | Billing + kitchen oversight + menu management + void approvals + staff/payroll/supplier expenses. No financial reports. | Desktop or tablet | PIN login |
| **Kitchen Staff** | KOT feed, item ready marking, item availability control | Tablet landscape | PIN login |
| **Owner (Admin)** | Everything above + full financial reports, custom report builder, Telegram configuration, void approval, menu, tenant settings | Mobile (monitoring) + Desktop (config) | TOTP + credentials |

### Key Design Challenges

1. **Speed under pressure** — Complete bill lifecycle in under 15 seconds by non-technical staff on 8-hour shifts. Every extra click is a failure.
2. **Role complexity in a single shell** — Four roles with meaningfully different permissions must feel like four focused tools, not one cluttered app with hidden buttons.
3. **Structural fraud prevention without friction** — Post-KOT item lock, manager/owner void approval, and immutable bill numbers must be invisible to good-faith users but airtight against misuse.
4. **Reporting power without reporting complexity** — A Level 3 report builder architecture must ship as a Level 2 experience at MVP — powerful enough to be useful, simple enough to not require training.

### Design Opportunities

1. **Permission-driven sidebar as the entire navigation system** — One app shell. Every role sees only their sidebar items. Biller sees 1 item. Owner sees everything. Same billing screen renders for any role with billing access — zero code duplication, zero role confusion.
2. **Keyboard-first as a market differentiator** — POS systems are uniformly click/touch-first. A keyboard-native billing experience in the Indian market is genuinely novel.
3. **Reports as Telegram alerts** — Each saved report has a per-report Telegram toggle with schedule and threshold configuration. No separate Telegram settings screen — the alert lives on the report. Build a report, schedule it to your phone. No POS in the market does this.
4. **The One Screen Philosophy** — Biller completes their entire job without ever leaving a single screen. Every UI decision must justify itself against this constraint.

---

## Core User Experience

### Defining Experience

The core experience of sphotel-billing is a **single uninterrupted flow**: open bill → add items → fire KOT → collect payment → print token → close. This flow must complete in under 15 seconds for a trained Biller with no mouse required. The entire product is designed around making this loop invisible — staff should feel like the system is reading their intent, not responding to their clicks.

The secondary experience layer — Manager oversight, Owner analytics, Kitchen display — all exist to support and accelerate that core billing loop.

### Platform Strategy

- **PWA (Progressive Web App)** — single installable app, works on any device via browser, no app store dependency
- **Primary Biller surface:** Desktop/laptop, keyboard-first, 1024px+ landscape optimised
- **Kitchen Display:** Tablet landscape, large-card touch UI, min 56px touch targets
- **Manager:** Desktop or tablet, hybrid keyboard/touch
- **Owner:** Mobile for monitoring (remote), desktop for configuration and report building
- **Offline-first:** IndexedDB fallback for all active bills and menu — internet outage is a minor inconvenience, not a business stoppage
- **Single app shell:** One codebase, one URL base, role-driven sidebar controls what each user sees — no separate apps per role

### Effortless Interactions

| Interaction | How it becomes effortless |
|---|---|
| Adding a menu item | Shortcode (CF = Chicken Fried Rice), fuzzy search always active, command palette (Space bar) — zero navigation |
| Switching bills | F1-F10 permanently bound to active bills — one key, zero loading |
| Firing KOT | Ctrl+K — one keystroke, async, never blocks UI |
| Printing token | Async print queue — UI never waits for printer |
| Reprinting | Ctrl+P on any closed bill — no history navigation needed |
| Recovering from crash | Auto-restore on reload — staff never re-enters a bill |
| Menu availability | Kitchen marks item unavailable → grayed out on all terminals within 3 seconds |
| Day close | One-button day close — freezes bills, archives data, sends Telegram summary |

### Critical Success Moments

1. **First item add** — Staff types 2 characters and sees the item appear. This moment defines whether the product feels fast or slow. Must be sub-100ms.
2. **First KOT fire** — Kitchen receives it in real-time. This closes the loop between billing and kitchen and proves the system works as one unit.
3. **First crash recovery** — App reloads after a crash and all open bills are exactly where they were. This is the moment staff stops fearing the system.
4. **First EOD report on Telegram** — Owner sees yesterday's full summary on their phone without logging in. This is the moment the product feels like it's working for them, not the other way around.
5. **First void approval** — Manager approves a Biller's void request from their screen. This is the moment the role system proves its value without feeling bureaucratic.

### Experience Principles

1. **Speed is the only feature that matters** — Every design decision is measured against whether it makes the core billing loop faster or slower. Slower = wrong.
2. **The keyboard is the interface** — Mouse and touch are fallbacks. Every primary action has a keyboard shortcut. New staff learn the system in one shift via the `?` overlay.
3. **One screen, one job** — Each role's primary surface is a single screen. Biller never navigates away from billing. Kitchen never leaves the KOT feed. Navigation complexity is a design failure.
4. **Roles simplify, not restrict** — The permission-driven sidebar should feel like focus, not limitation. Biller sees exactly what they need and nothing they don't.
5. **Intelligence comes to you** — Reports deliver themselves to Telegram. Offline mode activates automatically. Crash recovery is automatic. The system does the work so staff don't have to think about the system.

---

## Desired Emotional Response

### Primary Emotional Goals

| Role | Primary Emotion | What it feels like |
|---|---|---|
| **Biller** | **In control** | A trained pilot running a checklist — fast, precise, zero cognitive load. The system responds before they finish thinking. |
| **Manager** | **Commanding** | Full situational awareness of the floor — knows every table's state, can intervene anywhere in one action. |
| **Kitchen Staff** | **Clear** | No ambiguity. The queue is the truth. Items are either pending or done. Nothing to interpret. |
| **Owner** | **Confident** | The restaurant runs whether they're present or not. Data comes to them. Surprises are eliminated by design. |

### Emotional Journey Mapping

**Biller — During a rush:**
- *Opening a new bill* → Immediate readiness — blank canvas, cursor ready, nothing in the way
- *Adding items* → Fluency — shortcodes and fuzzy search respond so fast it feels like thought
- *Firing KOT* → Relief — kitchen has it, my job here is done
- *Taking payment* → Efficiency — split methods handled cleanly, no awkward moment with the customer
- *Something goes wrong (crash/offline)* → Calm — system restores itself, bills are all there, no panic

**Owner — End of day:**
- *Telegram report arrives* → Satisfaction — numbers in pocket without logging in
- *Checking a custom report* → Clarity — the chart they chose, the metric they care about, nothing else
- *Reviewing voids* → Trust — every void has a name, a reason, a timestamp. Nothing is hidden.

### Micro-Emotions

| Emotion to CREATE | Emotion to AVOID | How |
|---|---|---|
| **Mastery** — staff feel skilled | **Confusion** — staff don't know what to do next | `?` shortcut overlay, role-focused sidebar |
| **Speed** — actions feel instant | **Waiting** — any visible loading state | Sub-100ms search, async print queue, optimistic UI updates |
| **Trust** — numbers are always right | **Doubt** — "did that save?" anxiety | Auto-save every 5s, crash recovery, immutable bill numbers |
| **Calm** — offline/crash doesn't panic | **Fear** — "I lost the bill" | IndexedDB fallback, visible offline indicator, auto-restore |
| **Ownership** — Owner feels in command | **Dependency** — having to log in to know anything | Telegram push, configurable alerts come to them |

### Design Implications

- **Control → Keyboard-first with visible shortcuts** — staff who know the keyboard feel powerful; the `?` overlay makes that power accessible from day one
- **Speed → Optimistic UI** — show the item added immediately, sync in background; never make staff wait for server confirmation on routine actions
- **Trust → Visible state everywhere** — every bill shows its last-saved time; printer status visible; offline indicator clear but not alarming
- **Calm → Graceful degradation** — offline mode activates silently; crash recovery is automatic; the system handles failure so staff don't have to
- **Ownership → Intelligence delivered, not fetched** — reports push to Telegram; threshold alerts fire automatically; Owner never has to go looking for information

### Emotional Design Principles

1. **Competence over delight** — This is a work tool, not a consumer app. The emotional goal is making staff feel skilled and fast, not charmed or entertained.
2. **Silence is a feature** — No unnecessary confirmations, no loading spinners, no success toasts for routine actions. The system works quietly. Noise only when something actually needs attention.
3. **Failure is invisible** — Crashes recover automatically. Offline mode activates silently. The emotional experience of failure should be: nothing happened.
4. **Ownership through transparency** — Every financial action is traceable. Every void has a name. This doesn't create anxiety — it creates the confidence that nothing can be hidden.

---

## UX Pattern Analysis & Inspiration

### Inspiring Products Analysis

| Product | What we borrow | Why it works |
|---|---|---|
| **Bloomberg Terminal** | Keyboard-first everything, watchlist-style active panel, no mouse required | Traders process high-stakes data at speed — identical pressure profile to a rush-hour Biller |
| **VS Code** | Command palette (Space bar), tab-based multi-document navigation, never-lose-your-work auto-save, `?` shortcut overlay | Developers never navigate menus — they type. The entire billing flow follows this model |
| **Chrome** | Browser-tab multi-bill interface (Ctrl+T, Ctrl+W, Ctrl+Tab, F1-F10) | Staff already know this model — zero learning curve for multi-bill navigation |
| **WhatsApp** | KOT thread model — kitchen sees orders like a chat, double-tick = served *(Phase 2)* | Every worker already understands WhatsApp — zero training required for kitchen staff |
| **Airline check-in terminals** | Agent PIN login, shift-based sessions, every action tagged to authenticated user | Accountability at individual level without complex permissions — same two-role clarity |

### Transferable UX Patterns

**Navigation Patterns:**
- **Tab-bar as bill manager** (Chrome) — each open bill is a tab; Ctrl+T opens new, Ctrl+W closes paid, F1-F10 jump to any active bill
- **Sidebar as permission system** (VS Code file explorer) — visible only to the current role, collapsed on small screens, always present on desktop
- **Command palette as primary input** (VS Code) — Space bar opens floating input anywhere; type shortcode or item name; Enter adds to bill

**Interaction Patterns:**
- **Optimistic UI updates** — item appears in bill instantly, server sync happens silently in background (no waiting)
- **Async print queue** — printing is fire-and-forget; UI never blocks on printer; queue indicator shows status
- **Crash-recovery prompt on reload** — "Found 3 unsaved bills from 2 minutes ago — restore?" (VS Code unsaved file recovery)
- **Watchlist sidebar** (Bloomberg) — all open bills visible at a glance: table name, item count, time open, running total

**Visual Patterns:**
- **High-contrast dark UI** — restaurant environments are bright; dark mode reduces eye strain on 8-hour shifts
- **Large-card KOT display** (kitchen tablets) — min 18px font, min 56px touch targets, visible from distance
- **Minimal token slip** — 6 lines max, no logos, no borders; ink-efficient thermal output

### Anti-Patterns to Avoid

| Anti-pattern | Why it fails for sphotel |
|---|---|
| **Modal dialogs for routine actions** | Every confirmation modal adds 2-3 seconds and a click — death by a thousand modals during rush hour |
| **Full-page navigation for subtasks** | Navigating away from the billing screen to do anything breaks the One Screen Philosophy |
| **Synchronous print blocking** | If UI waits for printer, a paper jam stops billing entirely |
| **Complex permission UI** | Role confusion at login costs time; permission-driven sidebar eliminates the problem structurally |
| **Manual report generation** | Owner should never need to click "Generate Report" — reports are scheduled and pushed automatically |
| **Separate Telegram config screen** | Configuration divorced from the report it controls creates cognitive overhead — keep the toggle on the report |

### Design Inspiration Strategy

**Adopt directly:**
- VS Code command palette → Space bar billing input
- Chrome tabs → multi-bill tab bar with F1-F10 binding
- Bloomberg watchlist → active bills sidebar panel
- VS Code crash recovery → bill auto-restore on reload

**Adapt for context:**
- WhatsApp thread → KOT feed (Phase 2) — same visual metaphor, adapted for kitchen-to-billing communication
- Metabase/analytics tools → Owner report builder — Level 3 architecture, Level 2 launch UX; pre-built reports editable by chart type and filters, full builder in Phase 2

**Avoid entirely:**
- Consumer app delight patterns (animations, celebrations, gamification) — this is a work tool; silence and speed are the UX
- Dashboard-first layouts — Biller's first screen is the billing canvas, not a summary dashboard

---

## Design System Foundation

### Design System Choice

**shadcn/ui + Tailwind CSS**

A themeable, copy-paste component system built on Radix UI primitives, styled with Tailwind CSS utility classes.

### Rationale for Selection

- **Keyboard accessibility first-class** — Radix UI primitives (powering shadcn/ui) implement WAI-ARIA keyboard patterns by default; comboboxes, dialogs, tabs, and dropdowns all support full keyboard navigation without custom implementation
- **Dark mode trivial** — Tailwind's `dark:` variant and shadcn's built-in theme system make dark-first UI the default, not an afterthought
- **Component ownership** — shadcn/ui components are copied into your codebase, not imported as a black box; nothing fights keyboard customisation or interaction overrides
- **No visual lock-in** — zero recognisable "library aesthetic"; the UI looks exactly as designed
- **Tailwind for data density** — utility-first CSS handles the compact, information-dense layouts (billing canvas, KOT cards, data tables) without fighting a component library's spacing opinions

### Implementation Approach

- **Base layer:** Tailwind CSS v3+ with custom design tokens (colors, spacing, typography) defined in `tailwind.config`
- **Component layer:** shadcn/ui components copied and customised per surface — Command (command palette), Tabs (bill tabs), Table (reports, menu management), Dialog (void approval flow)
- **Chart layer:** Recharts (already integrated with shadcn/ui patterns) for Owner report builder — supports bar, line, pie, area, heatmap
- **Icon layer:** Lucide React (default shadcn/ui icons) — consistent, minimal, tree-shakeable

### Customization Strategy

| Token | Direction |
|---|---|
| **Color palette** | Dark background primary (`zinc-950`/`zinc-900`), high-contrast accents for status (green = paid, amber = KOT pending, red = overdue) |
| **Typography** | Monospace for bill numbers and amounts (trust signal); sans-serif for all other UI |
| **Spacing** | Compact — data-dense surfaces use tighter padding than shadcn defaults |
| **Border radius** | Minimal — sharp corners for data tables and billing canvas; slight radius for cards and modals |
| **Motion** | Disabled or near-zero — no decorative animation; only functional transitions (panel open/close < 150ms) |

---

## Core User Experience

### 2.1 Defining Experience

**"Type to bill."** — The command palette is always one keystroke away. Press Space anywhere on the billing screen to open it. Type a shortcode (`CF` = Chicken Fried Rice), a partial name (`chick`), or a quantity expression (`CF 2 BT 1`). The system responds in under 100ms. Press Enter. Items are on the bill.

This is the interaction that defines sphotel. Everything else — KOT firing, payment collection, printing — is a consequence of getting items onto a bill fast. Nail this, and the product succeeds.

If a Biller describes sphotel to a colleague, they say: *"You just type and it adds to the bill."*

### 2.2 User Mental Model

**Current mental model (PetPooja):**
- Navigate to category → find item → click quantity → add → repeat
- Multi-step, mouse-dependent, visually noisy
- Each item add takes 5-8 seconds, requires eyes on screen

**Mental model we're creating:**
- The terminal is always listening — one key wakes it up
- Type what you know (shortcode, partial name, or code number from the physical menu board)
- System completes the thought
- Modelled on VS Code command palette and Bloomberg terminal input — staff who learn this never want to go back

**Where confusion will happen:**
- First-time users won't know shortcodes exist — the `?` overlay and onboarding checklist must surface this immediately
- Quantity syntax (`CF 2`) needs a subtle hint in the command palette placeholder text
- Staff transitioning from PetPooja will instinctively reach for the mouse first — the keyboard shortcut overlay (`?` key) is the training tool

### 2.3 Success Criteria

| Criteria | Target |
|---|---|
| Command palette opens | < 50ms after Space keypress |
| Search results appear | < 100ms after first character typed |
| Item added to bill | Instant (optimistic UI) — server sync background |
| Full bill built (5 items) | < 20 seconds for trained staff |
| Zero mouse required | Complete bill lifecycle via keyboard only |
| New staff proficiency | One shift with `?` overlay available |

**"This just works" moment:** Staff types `chick` and sees every chicken item ranked by popularity before finishing the word. They arrow-key to select, Enter to add. They never open a category menu again.

### 2.4 Novel UX Patterns

**Familiar metaphors used:**
- VS Code command palette → Space bar billing input (developers already love this)
- Chrome tabs → bill tabs (everyone knows Ctrl+T, Ctrl+W)
- Physical menu board numbers → numeric item codes (`14x2` = item 14, qty 2)

**Novel combination:**
- The command palette as the *primary* billing input — not a power-user feature, but the default interaction for everyone — is new to POS systems
- Quantity expression parsing in the palette (`CF 2 BT 1` = 2 Chicken Fried Rice + 1 Butter Tea in one input) goes beyond what any comparable system offers

**User education approach:**
- `?` key overlay visible from day one — shows all shortcuts in a semi-transparent panel
- Command palette placeholder text: `Type item name, shortcode, or "CF 2 BT 1"...`
- Admin onboarding checklist includes "teach Biller keyboard shortcuts" as a setup step

### 2.5 Experience Mechanics

**Full billing loop mechanics:**

| Step | Trigger | System Response | Feedback |
|---|---|---|---|
| **Open new bill** | Ctrl+T | New bill tab opens, command palette auto-focuses | Tab appears in bill bar, cursor ready |
| **Add item** | Space → type → Enter | Item appears in bill instantly (optimistic) | Row animates in, running total updates |
| **Add more items** | Space (palette re-opens) | Previous palette cleared, ready for next input | Smooth, no delay |
| **Fire KOT** | Ctrl+K | KOT sent to kitchen async, bill state → KOT-fired | Subtle badge on bill tab, audio tick |
| **Switch bill** | F1-F10 or click tab | Instant switch, no loading | Active tab highlighted |
| **Collect payment** | Ctrl+B (bill) | Payment panel slides in | Amount pre-filled from bill total |
| **Split payment** | Tab between payment method fields | Each method captured separately | Running remainder shown |
| **Print token** | Ctrl+P or auto on close | Print job queued async, UI never waits | Print status indicator in corner |
| **Close bill** | Ctrl+W after payment | Bill archived, tab closes | Next active bill auto-focused |
| **Reprint** | Ctrl+P on closed bill in history | Immediate reprint queued | No navigation needed |

---

## Visual Design Foundation

### Color System

**Base palette — dark-first:**

| Token | Value | Usage |
|---|---|---|
| `--bg-base` | `zinc-950` (#09090b) | App background, sidebar |
| `--bg-surface` | `zinc-900` (#18181b) | Cards, panels, bill canvas |
| `--bg-elevated` | `zinc-800` (#27272a) | Dropdowns, command palette, modals |
| `--border` | `zinc-700` (#3f3f46) | Dividers, input borders |
| `--text-primary` | `white` (#ffffff) | Headings, bill items, primary data |
| `--text-secondary` | `zinc-400` (#a1a1aa) | Labels, metadata, timestamps |
| `--text-muted` | `zinc-600` (#52525b) | Placeholders, disabled states |

**Accent — configurable per tenant:**

| Token | Default Value | Usage |
|---|---|---|
| `--accent` | `violet-500` (#8b5cf6) | Active tabs, primary buttons, focus rings, selected states |
| `--accent-hover` | `violet-400` (#a78bfa) | Button hover, link hover |
| `--accent-subtle` | `violet-950` (#2e1065) | Accent backgrounds (badges, highlights) |
| `--accent-foreground` | `white` | Text on accent backgrounds |

**Configurability:** `--accent`, `--accent-hover`, and `--accent-subtle` are CSS custom properties set at `:root` level. The Owner can pick any accent color from a predefined palette (8-10 curated options) in tenant settings — the entire UI re-themes instantly without a page reload.

**Status colors — fixed, not accent-dependent:**

| State | Color | Token |
|---|---|---|
| Paid / Ready | `emerald-500` | `--status-success` |
| KOT fired / Pending | `amber-400` | `--status-warning` |
| Overdue / Error | `red-500` | `--status-error` |
| Offline mode | `zinc-500` | `--status-offline` |
| Void / Cancelled | `zinc-600` (strikethrough) | `--status-void` |

### Typography System

**Font pairing:**

| Role | Font | Rationale |
|---|---|---|
| **UI / Body** | `Inter` (Google Fonts) | Neutral, highly legible at small sizes, excellent number rendering |
| **Amounts / Bill numbers** | `JetBrains Mono` | Monospace creates trust signal for financial data; columns align perfectly |

**Type scale:**

| Level | Size | Weight | Usage |
|---|---|---|---|
| `display` | 20px | 600 | Bill total, KOT header |
| `heading` | 16px | 600 | Section headers, tab labels |
| `body` | 14px | 400 | Bill items, menu rows, general UI |
| `small` | 12px | 400 | Timestamps, metadata, labels |
| `mono` | 14px | 500 | Amounts, bill numbers, shortcodes |

**Kitchen Display exception:** Minimum 18px body, minimum 20px KOT item names — legible from 1.5m distance in bright kitchen lighting.

### Spacing & Layout Foundation

**Base unit:** 4px. All spacing is multiples of 4.

**Density profile — compact:**

| Context | Padding | Gap |
|---|---|---|
| Bill item rows | 6px 12px | 2px |
| Command palette results | 8px 12px | 0 |
| Sidebar nav items | 10px 16px | 4px |
| Cards / panels | 16px | 12px |
| Modals / dialogs | 24px | 16px |

**Layout grid:**

- **Biller screen:** Fixed sidebar (240px) + flex bill-tab area + fixed active-bills panel (280px)
- **Manager / Owner:** Fixed sidebar (240px) + main content area (fluid)
- **Kitchen Display:** Full-width card grid, 2-col on tablet, 3-col on desktop
- **Mobile (Owner monitoring):** Bottom nav tabs replace sidebar; cards stack single-column

### Accessibility Considerations

| Requirement | Implementation |
|---|---|
| **Contrast** | All text on dark backgrounds meets WCAG AA (4.5:1 minimum); accent on dark bg checked per chosen color |
| **Focus rings** | Visible `--accent` outline on all keyboard-focusable elements; never hidden |
| **Configurable accent safety** | Preset palette of 8-10 accent options pre-checked for WCAG AA contrast on `zinc-950` — Owner can only pick safe colors |
| **Kitchen display** | High-contrast mode: white text on `zinc-900` cards, min 18px, no low-opacity elements |
| **Motion** | `prefers-reduced-motion` respected — all transitions disabled if set |
| **Touch targets** | Min 44px on tablet/mobile surfaces; Biller desktop exempted (keyboard-primary) |
