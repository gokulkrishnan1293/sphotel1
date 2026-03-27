import { useEffect } from 'react'
import { useShortcutStore, matchKey } from '@/lib/shortcutStore'
import type { BillResponse, PaymentMethod } from '../types/bills'

export function useBillCanvasShortcuts(
  activeBillId: string | null,
  bill: BillResponse | undefined,
  focusSearch: () => void,
  fireKot: () => void,
  closeBill: (method: PaymentMethod) => void,
  closePending: boolean,
  setSettleOpen: (v: boolean) => void,
  defaultMethod: (t: string) => PaymentMethod,
) {
  useEffect(() => {
    if (!activeBillId) return
    const handle = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement).tagName
      const sc = useShortcutStore.getState().shortcuts
      if (matchKey(e, sc.close_bill)) { e.preventDefault(); if (bill && bill.status !== 'billed' && bill.status !== 'void' && bill.items.some((i) => i.status !== 'voided') && !closePending) closeBill(defaultMethod(bill.bill_type)); return }
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(tag)) return
      if (matchKey(e, sc.open_search)) { e.preventDefault(); focusSearch() }
      if (matchKey(e, sc.fire_kot)) { e.preventDefault(); if (bill?.items.some((i) => i.status === 'pending')) fireKot() }
      if (matchKey(e, sc.generate_bill)) { e.preventDefault(); if (bill && bill.status !== 'billed' && bill.status !== 'void') setSettleOpen(true) }
    }
    window.addEventListener('keydown', handle)
    return () => window.removeEventListener('keydown', handle)
  }, [activeBillId, bill, closePending]) // eslint-disable-line react-hooks/exhaustive-deps
}
