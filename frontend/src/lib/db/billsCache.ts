import { getDb } from './schema'
import type { BillResponse, BillSummaryResponse, BillItemResponse } from '../../features/billing/types/bills'

export async function writeBill(bill: BillResponse): Promise<void> {
  const db = await getDb()
  await db.put('bills', { id: bill.id, data: bill, updatedAt: Date.now() })
}

/** Write summaries from listOpen so panel shows bills offline. */
export async function writeBillSummaries(summaries: BillSummaryResponse[]): Promise<void> {
  const db = await getDb()
  const tx = db.transaction('bills', 'readwrite')
  await Promise.all(summaries.map((s) =>
    tx.store.put({ id: s.id, data: s, updatedAt: Date.now() })
  ))
  await tx.done
}

export async function readBill(id: string): Promise<BillResponse | null> {
  const db = await getDb()
  const rec = await db.get('bills', id)
  return rec ? (rec.data as BillResponse) : null
}

export async function optimisticAddItem(billId: string, item: BillItemResponse): Promise<void> {
  const bill = await readBill(billId)
  if (!bill) return
  const amt = item.price_paise * item.quantity
  await writeBill({ ...bill, items: [...bill.items, item], subtotal_paise: bill.subtotal_paise + amt, total_paise: bill.total_paise + amt, updated_at: new Date().toISOString() })
}

export async function optimisticRemoveItem(billId: string, itemId: string): Promise<void> {
  const bill = await readBill(billId)
  if (!bill) return
  const item = bill.items.find((i) => i.id === itemId)
  const amt = item ? (item.override_price_paise ?? item.price_paise) * item.quantity : 0
  await writeBill({ ...bill, items: bill.items.filter((i) => i.id !== itemId), subtotal_paise: Math.max(0, bill.subtotal_paise - amt), total_paise: Math.max(0, bill.total_paise - amt), updated_at: new Date().toISOString() })
}

export async function optimisticUpdateItem(billId: string, itemId: string, patch: { quantity?: number; override_price_paise?: number | null }): Promise<BillItemResponse | null> {
  const bill = await readBill(billId)
  if (!bill) return null
  const items = bill.items.map((i) => i.id === itemId ? { ...i, ...patch } : i)
  const subtotal = items.filter((i) => i.status !== 'voided').reduce((s, i) => s + (i.override_price_paise ?? i.price_paise) * i.quantity, 0)
  await writeBill({ ...bill, items, subtotal_paise: subtotal, total_paise: subtotal, updated_at: new Date().toISOString() })
  return items.find((i) => i.id === itemId) ?? null
}

export async function optimisticFireKot(billId: string): Promise<string[]> {
  const bill = await readBill(billId)
  if (!bill) return []
  const pendingIds = bill.items.filter((i) => i.status === 'pending').map((i) => i.id)
  const items = bill.items.map((i) => i.status === 'pending' ? { ...i, status: 'sent' as const } : i)
  await writeBill({ ...bill, items, status: 'kot_sent', updated_at: new Date().toISOString() })
  return pendingIds
}

export async function readOpenBills(): Promise<BillSummaryResponse[]> {
  const db = await getDb()
  const all = await db.getAll('bills')
  return all
    .map((r) => r.data as BillSummaryResponse)
    .filter((b) => b.status !== 'billed' && b.status !== 'void')
    .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
}
