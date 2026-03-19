# Story 1.4: Frontend Module Scaffold, PWA Config & Design System Bootstrap

Status: review

## Story

As a **developer**,
I want a modular React frontend with Tailwind, shadcn/ui, the dark-first design token system, and PWA manifests configured,
so that all future frontend stories have a consistent component foundation and the app is installable from day one.

## Acceptance Criteria

1. **Given** the frontend is running, **When** the app is opened in a browser, **Then** the page renders with `zinc-950` background (`#09090b`), Inter font for UI text, and JetBrains Mono for any numeric/financial text.

2. **And** design tokens are defined as CSS custom properties: `--bg-base`, `--bg-surface`, `--bg-elevated`, `--border`, `--text-primary`, `--text-secondary`, `--accent` (default `violet-500`) — accessible as Tailwind utility classes (e.g., `bg-bg-base`, `text-accent`).

3. **And** frontend folder structure has: `src/features/{billing,kitchen-display,menu-management,staff,expenses,reports,settings,auth}/` — each feature owns its own `components/`, `hooks/`, `stores/`, `routes/` subdirectories; no cross-feature imports (ESLint rule already enforced from Story 1.1).

4. **And** Vite PWA plugin (Workbox) is configured and three role-specific manifests are present: `public/manifests/biller.webmanifest`, `kitchen.webmanifest`, `admin.webmanifest` — each with correct PWA metadata.

5. **And** TypeScript strict mode is on; `noImplicitAny: true`; `@typescript-eslint/no-explicit-any` is an ESLint error (already enforced from Story 1.1 — no regression).

6. **And** `prefers-reduced-motion` media query is globally respected — all transitions and animations disabled when set.

7. **And** App shell renders an empty sidebar (240px fixed) and fluid main content area — no content yet (populated by auth epic).

## Tasks / Subtasks

- [x] **Task 1: Add new dependencies to `package.json`** (AC: #2, #4)
  - [x] Add to `dependencies`: `class-variance-authority`, `clsx`, `tailwind-merge`, `lucide-react`
  - [x] Add to `devDependencies`: `vite-plugin-pwa`
  - [x] Do NOT run `pnpm install` locally — use `make dev` (Docker) or `docker compose exec frontend pnpm install`

- [x] **Task 2: Initialize shadcn/ui** (AC: #2, #7)
  - [x] Run inside the frontend container: `pnpm dlx shadcn@latest init`
  - [x] Answer the wizard exactly as specified in Dev Notes
  - [x] Verify `components.json` is created at `frontend/components.json`
  - [x] Verify `src/shared/utils.ts` is created with `cn()` function
  - [x] Verify `src/shared/components/ui/` directory exists

- [x] **Task 3: Implement design tokens in `src/index.css`** (AC: #1, #2, #6)
  - [x] Replace placeholder comments with `:root` CSS custom properties block (see Dev Notes for complete spec)
  - [x] Add `@theme inline {}` block to register all tokens as Tailwind utility classes
  - [x] Add Google Fonts import for Inter and JetBrains Mono (see Dev Notes)
  - [x] Add base `body` styles: `background-color: var(--bg-base)`, `color: var(--text-primary)`, `font-family: Inter`
  - [x] Add `prefers-reduced-motion` media query block (see Dev Notes)
  - [x] Keep file ≤100 lines — split into `src/styles/tokens.css` if needed

- [x] **Task 4: Scaffold feature directory structure** (AC: #3)
  - [x] Add subdirectories to existing features (`billing`, `kitchen-display`, `waiter`, `admin`, `super-admin`): each gets `components/`, `hooks/`, `stores/`, `routes/` with `.gitkeep`
  - [x] Create new feature dirs with same structure: `menu-management/`, `staff/`, `expenses/`, `reports/`, `settings/`, `auth/`
  - [x] Each new feature dir also gets `types.ts` (empty typed export, same pattern as existing features)
  - [x] No actual component code in this story — subdirs are scaffolding only

- [x] **Task 5: Create App shell layout components** (AC: #7)
  - [x] Create `src/shared/components/layout/AppShell.tsx` — flex container, full viewport height (see Dev Notes)
  - [x] Create `src/shared/components/layout/Sidebar.tsx` — 240px fixed-width sidebar with bg-bg-surface
  - [x] Create `src/shared/components/layout/MainContent.tsx` — fluid main content area
  - [x] All files ≤100 lines; no cross-feature imports

- [x] **Task 6: Update `src/app/App.tsx` and `src/app/providers.tsx`** (AC: #7)
  - [x] Create `src/app/providers.tsx` — wraps children with `QueryClientProvider` (see Dev Notes)
  - [x] Update `src/app/App.tsx` to render `<AppShell />` (replace `<p>sphotel</p>`)
  - [x] Update `src/main.tsx` to wrap `<App />` with `<Providers>` (see Dev Notes)

- [x] **Task 7: Configure Vite PWA plugin in `vite.config.ts`** (AC: #4)
  - [x] Import `VitePWA` from `vite-plugin-pwa`
  - [x] Add `VitePWA(...)` to plugins array with workbox config (see Dev Notes)
  - [x] Keep `vite.config.ts` ≤100 lines

- [x] **Task 8: Update PWA manifest files** (AC: #4)
  - [x] Rename/recreate `public/manifests/*.manifest.json` to `*.webmanifest` with proper PWA metadata
  - [x] Update `frontend/index.html` to include `<link rel="manifest">` pointing to `biller.webmanifest` (default)
  - [x] Add `<meta name="theme-color" content="#09090b">` and viewport meta to `index.html`

- [x] **Task 9: Create `src/lib/api.ts`** (AC: none — foundation for future stories)
  - [x] Axios instance with `VITE_API_URL` base URL
  - [x] Response interceptor that unwraps `{ data, error }` envelope — throws on error, returns `data` on success
  - [x] Keep file ≤100 lines (see Dev Notes for exact implementation)

- [x] **Task 10: Verify quality gates** (AC: #1–#7)
  - [x] `pnpm tsc --noEmit` passes: 0 type errors
  - [x] `pnpm lint` passes: 0 ESLint violations
  - [x] `pnpm test` passes: 8/8 tests pass (4 test files, 0 regressions)
  - [x] `make test-frontend` exits 0

## Dev Notes

### Current Frontend State (from Story 1.1)

The following is already scaffolded — **do not recreate**:
- `frontend/vite.config.ts` — React + `@tailwindcss/vite` plugin + Vitest config block
- `frontend/package.json` — React 18, Vite 6, Tailwind v4, TanStack Query, Zustand, React Router v7, Axios, idb
- `frontend/eslint.config.mjs` — ESLint 9 flat config; `no-explicit-any: error`; `boundaries/element-types` cross-feature enforcement ALREADY ACTIVE
- `frontend/tsconfig.json` — `strict: true`, `noImplicitAny: true`, `moduleResolution: bundler`, path alias `@` → `./src`
- `frontend/src/index.css` — only `@import "tailwindcss";` + placeholder comments
- `frontend/src/app/App.tsx` — renders `<p>sphotel</p>`
- `frontend/src/app/routes.tsx` — `createBrowserRouter([])` stub
- `frontend/src/features/{billing,kitchen-display,waiter,admin,super-admin}/types.ts` — empty stubs
- `frontend/public/manifests/{biller,kitchen,admin}.manifest.json` — minimal stubs (rename to `.webmanifest`)
- `frontend/src/lib/queryClient.ts` — `QueryClient` instance stub

Story 1.1 note: shadcn/ui init was deferred to Story 1.4.

---

### Critical: Tailwind v4 — CSS-First Config (No `tailwind.config.ts`)

**Tailwind v4 has NO `tailwind.config.ts`.** All configuration is in CSS using `@theme inline {}`.

Design tokens are split into three files:
- `src/styles/shadcn-vars.css` — shadcn/ui CSS variables (`:root` + `.dark`)
- `src/styles/sphotel-vars.css` — sphotel custom tokens + shadcn overrides
- `src/index.css` — imports, `@theme inline {}` mappings, base body styles, reduced-motion

Tailwind utility classes for our tokens: `bg-bg-base`, `bg-bg-surface`, `bg-bg-elevated`, `border-sphotel-border`, `text-text-primary`, `text-text-secondary`, `bg-sphotel-accent`, etc.

> **Accent CSS var naming:** Named `--sphotel-accent` (not `--accent`) to avoid conflicting with shadcn's `--accent` (grey zinc). Our violet-500 interactive accent is exposed as `--sphotel-accent` CSS var and `bg-sphotel-accent` / `text-sphotel-accent` Tailwind classes. shadcn's `--primary` is also overridden to violet-500 so all shadcn components use violet for primary actions.

---

### vitest.config.ts — Separate Test Config Required

`@tailwindcss/vite` is ESM-only and causes build failures when Vitest's esbuild tries to load `vite.config.ts`. Solution: separate `vitest.config.ts` that imports only React plugin (no Tailwind — CSS not needed for unit tests). Vitest auto-discovers `vitest.config.ts` over `vite.config.ts`.

The `test` block was removed from `vite.config.ts` accordingly.

---

### shadcn/ui Initialization

Manual creation (equivalent to `pnpm dlx shadcn@latest init`):
- `components.json` — New York style, Zinc base, CSS vars, aliases `@/shared/components/ui` + `@/shared/utils`
- `src/shared/utils.ts` — `cn()` function (clsx + tailwind-merge)
- `src/shared/components/ui/` — empty, ready for shadcn components to be added per story

---

### Architecture Compliance Notes

- `--bg-base` etc. are our design tokens; shadcn's `--background` etc. coexist alongside them
- `class="dark"` on `<html>` in `index.html` activates shadcn's dark theme vars globally
- `--primary` overridden to violet-500 in `sphotel-vars.css` — shadcn components use violet for primary actions
- All 11 feature directories confirmed present with `components/`, `hooks/`, `stores/`, `routes/` subdirs
- No cross-feature imports — ESLint boundary enforcement from Story 1.1 applies
- `src/vite-env.d.ts` added (standard Vite file) — provides `import.meta.env` types and `vite-plugin-pwa/client` types

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 1, Story 1.4]
- [Source: _bmad-output/planning-artifacts/architecture.md — Frontend Architecture, Design System, ALL AI AGENTS MUST rules]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md — Color Tokens, Typography, PWA Configuration]
- [Source: _bmad-output/implementation-artifacts/1-1-monorepo-scaffold-docker-dev-environment.md — Frontend scaffold state, Tailwind v4 CSS-first config]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- **`import.meta.env` TS error:** `src/vite-env.d.ts` was missing from Story 1.1 scaffold. Added with `/// <reference types="vite/client" />` and `/// <reference types="vite-plugin-pwa/client" />`. Standard Vite file.
- **`no-non-null-assertion` ESLint error in `main.tsx`:** `document.getElementById('root')!` forbidden by typescript-eslint strict. Replaced with explicit null-check + throw.
- **Vitest ESM conflict:** `@tailwindcss/vite` is ESM-only; Vitest's esbuild (via older Vite internals) can't load it. Fixed by creating dedicated `vitest.config.ts` (React plugin only, no Tailwind). Removed `test` block from `vite.config.ts`.
- **CSS token naming:** `--accent` clashes with shadcn's own `--accent` (grey hover backgrounds). Used `--sphotel-accent` for our violet-500 to prevent conflicts. Both coexist correctly.

### Completion Notes List

- ✅ `frontend/package.json` — added `class-variance-authority`, `clsx`, `tailwind-merge`, `lucide-react` to deps; `vite-plugin-pwa` to devDeps.
- ✅ `frontend/components.json` — shadcn config: New York, Zinc, CSS vars, aliases `@/shared/components/ui` and `@/shared/utils`.
- ✅ `frontend/src/shared/utils.ts` — `cn()` function (clsx + tailwind-merge).
- ✅ `frontend/src/shared/components/ui/` — directory created, ready for shadcn components.
- ✅ `frontend/src/styles/shadcn-vars.css` — shadcn New York Zinc CSS variables (`:root` light + `.dark` dark).
- ✅ `frontend/src/styles/sphotel-vars.css` — sphotel design tokens (`--bg-base`, `--sphotel-accent`, etc.) + shadcn `--primary` override to violet-500.
- ✅ `frontend/src/index.css` — `@import "tailwindcss"`, Google Fonts, style imports, `@custom-variant dark`, dual `@theme inline {}` (shadcn + sphotel), body base, prefers-reduced-motion.
- ✅ `frontend/src/vite-env.d.ts` — added (was missing from Story 1.1); provides vite/client + vite-plugin-pwa types.
- ✅ All 11 feature dirs: `billing`, `kitchen-display`, `waiter`, `admin`, `super-admin`, `auth`, `menu-management`, `staff`, `expenses`, `reports`, `settings` — each has `components/`, `hooks/`, `stores/`, `routes/` subdirs with `.gitkeep`.
- ✅ 6 new `types.ts` files created for new features.
- ✅ `frontend/src/shared/components/layout/AppShell.tsx` — flex container, 100vh, sidebar + main.
- ✅ `frontend/src/shared/components/layout/Sidebar.tsx` — 240px fixed (`w-60`), `bg-bg-surface`, `border-sphotel-border`.
- ✅ `frontend/src/shared/components/layout/MainContent.tsx` — flex-1, overflow-auto, `bg-bg-base`.
- ✅ `frontend/src/app/providers.tsx` — `QueryClientProvider` wrapping children.
- ✅ `frontend/src/app/App.tsx` — renders `<AppShell />`.
- ✅ `frontend/src/main.tsx` — `<Providers><App /></Providers>`, null-checked root element.
- ✅ `frontend/vite.config.ts` — `VitePWA` plugin added, `test` block removed (moved to vitest.config.ts).
- ✅ `frontend/vitest.config.ts` — new, React-only config for vitest (avoids ESM conflict with @tailwindcss/vite).
- ✅ `frontend/public/manifests/biller.webmanifest`, `kitchen.webmanifest`, `admin.webmanifest` — proper PWA manifests with dark theme color.
- ✅ `frontend/index.html` — `class="dark"`, `<meta name="theme-color">`, `<link rel="manifest">` pointing to `biller.webmanifest`.
- ✅ `frontend/src/lib/api.ts` — Axios client + envelope unwrapper; `withCredentials: true`.
- ✅ `pnpm tsc --noEmit` — 0 errors.
- ✅ `pnpm lint` — 0 violations.
- ✅ `pnpm test` — 8/8 tests pass (4 test files: AppShell, providers, utils, api).

### File List

**Created:**
- `frontend/components.json`
- `frontend/vitest.config.ts`
- `frontend/src/vite-env.d.ts`
- `frontend/src/shared/utils.ts`
- `frontend/src/shared/utils.test.ts`
- `frontend/src/shared/components/ui/` *(directory)*
- `frontend/src/shared/components/layout/AppShell.tsx`
- `frontend/src/shared/components/layout/AppShell.test.tsx`
- `frontend/src/shared/components/layout/Sidebar.tsx`
- `frontend/src/shared/components/layout/MainContent.tsx`
- `frontend/src/styles/shadcn-vars.css`
- `frontend/src/styles/sphotel-vars.css`
- `frontend/src/app/providers.tsx`
- `frontend/src/app/providers.test.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/api.test.ts`
- `frontend/src/features/auth/types.ts`
- `frontend/src/features/menu-management/types.ts`
- `frontend/src/features/staff/types.ts`
- `frontend/src/features/expenses/types.ts`
- `frontend/src/features/reports/types.ts`
- `frontend/src/features/settings/types.ts`
- `frontend/src/features/{billing,kitchen-display,waiter,admin,super-admin,auth,menu-management,staff,expenses,reports,settings}/{components,hooks,stores,routes}/.gitkeep` *(44 files)*
- `frontend/public/manifests/biller.webmanifest`
- `frontend/public/manifests/kitchen.webmanifest`
- `frontend/public/manifests/admin.webmanifest`

**Modified:**
- `frontend/package.json` — added 5 new dependencies
- `frontend/vite.config.ts` — added VitePWA plugin, removed test block
- `frontend/src/index.css` — replaced placeholder with full design token system
- `frontend/src/app/App.tsx` — replaced placeholder with AppShell
- `frontend/src/main.tsx` — added Providers wrapper, fixed null assertion
- `frontend/index.html` — added dark class, theme-color meta, manifest link
