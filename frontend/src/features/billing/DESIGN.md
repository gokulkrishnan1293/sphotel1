# Billing Canvas — Design Notes

## What changed and why

The original design used two modals that interrupted the keyboard flow:
- **`QuickBillBar`** — modal for creating a new bill (type / table / waiter)
- **`CommandPalette`** — modal overlay for searching and adding menu items

Users were not picking them up. The new design removes both modals and embeds everything inline in the canvas area, so the operator never leaves the keyboard flow.

---

## New component map

```
BillingPage
├── ActiveBillsPanel          ← unchanged (open bills list, + button)
└── BillCanvas
    ├── [no activeBillId]  → InlineBillCreator   (replaces QuickBillBar modal)
    └── [activeBillId set]
        ├── BillHeader                            ← unchanged
        ├── InlineSearch                          (replaces CommandPalette modal)
        ├── ItemRow[]                             ← unchanged
        ├── BillFooter                            ← unchanged
        └── SettleDialog                          ← unchanged (opened by G shortcut or Generate Bill button)
```

---

## InlineBillCreator

**File:** `components/InlineBillCreator.tsx`

**Purpose:** Shown in the canvas whenever `activeBillId` is null. Replaces the QuickBillBar modal entirely.

**Layout:**
```
[ Order type… ]  [ Table… / Order ref… ]  [ Waiter… ]
[ Open Bill button ]
```
- On **desktop**: 3 inputs in a horizontal row
- On **mobile**: 3 inputs stacked vertically (full width)

**Keyboard flow:**
1. Type `1` → auto-selects "Dine In" → focus jumps to Table box
2. Type `2` → auto-selects "Parcel" → skips Table box, focus jumps to Waiter
3. Type `3`, `4`… → selects vendor (Swiggy, Zomato etc.) → focus jumps to Ref box
4. In each box: ↑↓ navigate dropdown, Enter selects
5. Enter in Waiter box (when waiter is selected or box is empty) → submits / opens bill

**Number shortcuts for order type:**
- Numbers are assigned in order: 1=Dine In, 2=Parcel, 3+=vendors
- Typing the exact number immediately auto-selects and moves focus (no Enter needed)
- Numbers are shown as `kbd` badges in the dropdown

**State owned here:**
- All 3 input values and their selected states
- `openBill` mutation (was previously in `ActiveBillsPanel`)
- On success: calls `setActiveBill(bill.id)` → BillCanvas switches to bill view

**To add a new order type:** Add an entry to `typeOptions` in the `useMemo` block with a `label`, `type` ('table'|'parcel'|'online'), optional `vendor` slug, and a `shortcut` number.

**To change the flow between boxes:** Edit the `pickType`, `pickTable`, `pickWaiter` functions and the `onKeyDown` handlers.

---

## InlineSearch

**File:** `components/InlineSearch.tsx`

**Purpose:** Always-visible search bar inside the canvas when a bill is open. Replaces the CommandPalette modal.

**Layout:**
```
🔍 [ Search items… or 412 2 453 1 (batch) ]   ×qty   F8 quick bill
   ┌─ dropdown results (shows on focus / typing) ─────────────────┐
   │  • Butter Chicken    Main   #412    ₹280                     │
   │  • Paneer Tikka      Starter #453   ₹220                     │
   └──────────────────────────────────────────────────────────────┘
```

**All CommandPalette functionality is preserved:**
- Short code search (`412`)
- Name / category search
- Quantity suffix (`butter chicken 2` → adds 2)
- Batch mode (`412 2 453 1` → adds item #412 qty 2 and #453 qty 1)
- Variant picker (same `VariantPicker` component)
- Batch queue processing (processes one item at a time if variants involved)

**New behaviour vs CommandPalette:**
- Not a modal — no backdrop, no Escape to close, no fixed overlay
- Results appear as an inline dropdown below the bar (only when focused or has text)
- `onBlur` with 150ms delay hides results (allows clicking a result)
- Exposed via `forwardRef` with a `focus()` handle — "Add Item" button in BillFooter calls this instead of opening a modal

**Keyboard shortcuts (desktop only, hidden on mobile):**
- `F8` → **one-click bill close** (default payment method, no dialog, works even while typing)
- `Enter` → add highlighted item
- `↑↓` → navigate results

**To extend search filtering:** Edit the `filtered` useMemo (scoring logic kept from CommandPalette).

**To add a new keyboard shortcut inside search:** Add a branch to the `onKey` function.

---

## BillCanvas changes

**File:** `components/BillCanvas.tsx`

**Key changes:**
- Removed `commandPaletteOpen` usage (cleaned from store too)
- When `!activeBillId` → renders `<InlineBillCreator canOpen={canOpenNewBill} />`
- When bill is open and not closed → renders `<InlineSearch ref={searchRef} … />`
- `onAddItem` prop to BillFooter now calls `searchRef.current?.focus()` instead of opening a modal
- New `canOpenNewBill` prop (passed from BillingPage, same logic as before)

**Shortcut map (current):**
| Key | Action |
|-----|--------|
| `F8` | One-click close bill (default method, no dialog) — works even in inputs |
| `Space` / configured `open_search` | Focus inline search bar |
| `G` / configured `generate_bill` | Open SettleDialog (choose method + discount) |
| `⌘K` / configured `fire_kot` | Fire KOT |
| configured `close_bill` | One-click close (same as F8, configurable) |

---

## ActiveBillsPanel changes

**File:** `components/ActiveBillsPanel.tsx`

**What was removed:**
- `showNew` state
- `openBill` mutation (moved into InlineBillCreator)
- `QuickBillBar` import and render

**What changed:**
- `+` button and `N` shortcut now call `startNewBill()` which does:
  1. `setActiveBill(null)` → canvas switches to InlineBillCreator
  2. `onSelect?.()` → on mobile, switches to canvas view

---

## billingStore changes

**File:** `stores/billingStore.ts`

Removed `commandPaletteOpen`, `openCommandPalette`, `closeCommandPalette` — no longer needed.

Current shape:
```ts
{
  activeBillId: string | null
  setActiveBill: (id: string | null) => void
}
```

---

## Mobile behaviour

On mobile, `BillingPage` uses a two-view switcher (`mobileView: 'panel' | 'canvas'`):
- Panel = ActiveBillsPanel (bill list)
- Canvas = BillCanvas (creator or bill view)

Flow:
1. Tap `+` → `startNewBill()` → `setActiveBill(null)` + `onSelect()` → switches to canvas → shows InlineBillCreator (stacked inputs)
2. Tap "Open Bill" → bill created → `activeBillId` set → `useEffect` in BillingPage auto-keeps canvas view → shows bill + InlineSearch
3. Keyboard shortcuts (`N`, `F8`) don't apply on mobile. Users tap `+` and the footer "Generate Bill" button instead.

---

## Files NOT changed

These are untouched and safe to modify independently:
- `BillHeader.tsx` — bill metadata display
- `BillFooter.tsx` — action buttons (Add Item, Fire KOT, Generate Bill, Void, Reprint)
- `ItemRow.tsx` — individual line item
- `SettleDialog.tsx` — payment method + discount dialog
- `VariantPicker.tsx` — variant selection (used inside InlineSearch)
- `PastBillsModal.tsx` — historical bills browser
- `api/bills.ts` — all API calls, offline queue logic
- `hooks/useAutoSave.ts`, `hooks/useOfflineSync.ts`

---

## Offline support

All operations work offline. `billsApi.open()` creates a temp bill (`id: 'offline_TIMESTAMP'`), queues the operation, and writes to IndexedDB. The rest of the app treats it like a real bill. When back online, `useOfflineSync` replays the queue.

The `canOpenNewBill` guard (printer check) is separate from network offline — it only blocks non-local devices when the printer agent is down.
