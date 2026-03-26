/**
 * Offline print fallback — POSTs directly to the print agent's local HTTP
 * server (http://127.0.0.1:8766/print) when the cloud backend is unreachable.
 * The agent formats the receipt from raw bill data.
 */
import type { BillResponse } from '../features/billing/types/bills'
import type { PrintTemplateConfig } from '../features/settings/api/printSettings'

const LOCAL_PRINT_URL = 'http://127.0.0.1:8766/print'
const TEMPLATE_KEY = 'sphotel:print_template'
const DAILY_BILL_NUM_KEY = 'sphotel:daily_bill_number'

export function cachePrintTemplate(tmpl: PrintTemplateConfig): void {
  try { localStorage.setItem(TEMPLATE_KEY, JSON.stringify(tmpl)) } catch { /* ignore */ }
}

/** Call after a bill is successfully created on the server to track today's max bill number. */
export function cacheDailyBillNumber(billNumber: number): void {
  try {
    const today = new Date().toISOString().slice(0, 10)
    localStorage.setItem(DAILY_BILL_NUM_KEY, JSON.stringify({ date: today, max: billNumber }))
  } catch { /* ignore */ }
}

/** Returns today's max bill number (0 if none recorded or date has changed). */
export function loadDailyBillNumber(): number {
  try {
    const raw = localStorage.getItem(DAILY_BILL_NUM_KEY)
    if (!raw) return 0
    const { date, max } = JSON.parse(raw) as { date: string; max: number }
    const today = new Date().toISOString().slice(0, 10)
    return date === today ? max : 0
  } catch { return 0 }
}

function loadTemplate(): PrintTemplateConfig | null {
  try {
    const raw = localStorage.getItem(TEMPLATE_KEY)
    return raw ? (JSON.parse(raw) as PrintTemplateConfig) : null
  } catch { return null }
}

function buildPayload(bill: BillResponse, tmpl: PrintTemplateConfig | null) {
  return {
    job_type: 'receipt',
    bill_type: bill.bill_type,
    bill_number: bill.bill_number,
    token_number: bill.bill_number,
    subtotal_paise: bill.subtotal_paise,
    discount_paise: bill.discount_paise,
    total_paise: bill.total_paise,
    waiter_name: bill.waiter_name,
    cashier: bill.created_by_name,
    printed_at: new Date().toISOString(),
    print_template: tmpl ?? {},
    items: bill.items
      .filter((i) => i.status !== 'voided')
      .map((i) => ({
        name: i.name,
        qty: i.quantity,
        price_paise: i.override_price_paise ?? i.price_paise,
      })),
  }
}

export async function localPrintKot(bill: BillResponse, pendingItemIds: string[]): Promise<void> {
  const kotItems = bill.items.filter((i) => pendingItemIds.includes(i.id))
  const payload = {
    job_type: 'kot',
    bill_number: bill.bill_number,
    bill_type: bill.bill_type,
    kot_number: bill.kot_tickets.length + 1,
    printed_at: new Date().toISOString(),
    print_template: loadTemplate() ?? {},
    items: kotItems.map((i) => ({ name: i.name, qty: i.quantity })),
  }
  const res = await fetch(LOCAL_PRINT_URL, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
  if (!res.ok) throw new Error('Local KOT print failed')
}

export async function localPrint(bill: BillResponse): Promise<void> {
  const res = await fetch(LOCAL_PRINT_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(buildPayload(bill, loadTemplate())),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { error?: string }
    throw new Error(err.error ?? 'Local print failed')
  }
}
