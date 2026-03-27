import { useState, useDeferredValue } from 'react'
import { useQuery } from '@tanstack/react-query'
import { X, Search, ShoppingBag, Laptop, UtensilsCrossed } from 'lucide-react'
import { billsApi } from '../api/bills'
import { BillDetailModal } from './BillDetailModal'
import type { BillStatus, BillType } from '../types/bills'

const DOT: Record<BillStatus, string> = { draft: 'bg-text-muted', kot_sent: 'bg-status-success', partially_sent: 'bg-amber-400', billed: 'bg-sphotel-accent', void: 'bg-status-error', cancelled: 'bg-text-muted/50' }
const ICON: Record<BillType, React.ElementType> = { table: UtensilsCrossed, parcel: ShoppingBag, online: Laptop }

export function PastBillsModal({ onClose }: { onClose: () => void }) {
  const [q, setQ] = useState('')
  const [detailBillId, setDetailBillId] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string | undefined>()
  const dq = useDeferredValue(q)
  const { data: bills = [], isFetching } = useQuery({
    queryKey: ['bills', 'history', dq, statusFilter],
    queryFn: () => billsApi.listHistory(dq || undefined, statusFilter),
    staleTime: 15_000,
  })
  return (
    <>
    <div className="fixed inset-0 z-50 flex items-end md:items-center justify-center bg-black/50" onClick={onClose}>
      <div className="w-full md:w-[480px] bg-bg-surface rounded-t-2xl md:rounded-2xl flex flex-col max-h-[85vh] md:max-h-[75vh]" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-4 py-3 border-b border-sphotel-border shrink-0">
          <h2 className="text-sm font-semibold text-text-primary">Bill History</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary"><X size={16} /></button>
        </div>
        <div className="px-4 pt-3 pb-2 flex flex-col gap-2 shrink-0">
          <div className="flex items-center gap-2 bg-bg-elevated border border-sphotel-border rounded-xl px-3 py-2">
            <Search size={13} className="text-text-muted shrink-0" />
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search by bill number…" className="flex-1 bg-transparent text-sm text-text-primary placeholder-text-muted outline-none" autoFocus />
          </div>
          <div className="flex gap-1.5">
            {([undefined, 'billed', 'void', 'cancelled'] as const).map((s) => (
              <button key={s ?? 'all'} onClick={() => setStatusFilter(s)} className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${statusFilter === s ? 'bg-sphotel-accent text-sphotel-accent-fg' : 'bg-bg-elevated text-text-muted hover:text-text-primary'}`}>
                {s == null ? 'All' : s === 'billed' ? 'Settled' : s === 'void' ? 'Void' : 'Cancelled'}
              </button>
            ))}
          </div>
        </div>
        <div className="flex-1 overflow-y-auto px-2 pb-4 min-h-0">
          {isFetching && <p className="text-xs text-text-muted px-3 py-3">Loading…</p>}
          {!isFetching && bills.length === 0 && <p className="text-xs text-text-muted px-3 py-3">No bills found</p>}
          {bills.map((bill) => {
            const Icon = ICON[bill.bill_type]
            return (
              <button key={bill.id} onClick={() => setDetailBillId(bill.id)} className="w-full px-3 py-2.5 rounded-lg hover:bg-bg-base text-left transition-colors">
                <div className="flex items-start gap-2">
                  <Icon size={13} className="shrink-0 opacity-60 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-1">
                      <p className="text-sm font-medium truncate capitalize">{bill.bill_type} <span className="text-xs font-normal opacity-50">#{bill.bill_number}</span></p>
                      <div className="flex items-center gap-1.5 shrink-0">
                        <span className="text-sm font-semibold">₹{(bill.total_paise / 100).toFixed(0)}</span>
                        <span className={`w-2 h-2 rounded-full ${DOT[bill.status]}`} />
                      </div>
                    </div>
                    {bill.waiter_name && <p className="text-xs text-text-muted truncate">Waiter: {bill.waiter_name}</p>}
                    {bill.item_names.length > 0 && <p className="text-xs text-text-muted truncate mt-0.5">{bill.item_names.join(' · ')}</p>}
                  </div>
                </div>
              </button>
            )
          })}
        </div>
      </div>
    </div>
    {detailBillId && <BillDetailModal billId={detailBillId} onClose={() => setDetailBillId(null)} />}
    </>
  )
}
