import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Plus, ShoppingBag, Laptop, UtensilsCrossed, ChevronDown, ChevronRight, Clock } from 'lucide-react'
import { billsApi } from '../api/bills'
import { useBillingStore } from '../stores/billingStore'
import { tablesApi } from '../../admin/api/tables'
import type { BillSummaryResponse, BillStatus, BillType } from '../types/bills'
import { useShortcutStore, matchKey } from '@/lib/shortcutStore'
import { toast } from '@/lib/toast'
import { PastBillsModal } from './PastBillsModal'

const STATUS_DOT: Record<BillStatus, string> = { draft: 'bg-text-muted', kot_sent: 'bg-status-success', partially_sent: 'bg-amber-400', billed: 'bg-sphotel-accent', void: 'bg-status-error' }
const TYPE_ICON: Record<BillType, React.ElementType> = { table: UtensilsCrossed, parcel: ShoppingBag, online: Laptop }

export function ActiveBillsPanel({ onSelect, canOpenNewBill = true }: { onSelect?: () => void; canOpenNewBill?: boolean }) {
  const { activeBillId, setActiveBill } = useBillingStore()
  const [showPast, setShowPast] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const { data: bills = [], isLoading } = useQuery({ queryKey: ['bills', 'open'], queryFn: billsApi.listOpen, refetchInterval: 15_000 })
  const { data: recentBills = [] } = useQuery({ queryKey: ['bills', 'recent'], queryFn: billsApi.listRecent, enabled: showPast, refetchInterval: 30_000 })
  const { data: sections = [] } = useQuery({ queryKey: ['sections'], queryFn: tablesApi.listSections })
  const tableMap: Record<string, string> = {}
  sections.forEach((s) => s.tables.forEach((t) => (tableMap[t.id] = t.name)))

  function startNewBill() {
    if (!canOpenNewBill) { toast('Printer is offline — cannot open new bills from this device'); return }
    setActiveBill(null)
    onSelect?.()
  }

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const tag = (document.activeElement as HTMLElement)?.tagName
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return
      if (matchKey(e, useShortcutStore.getState().shortcuts.new_bill)) { e.preventDefault(); startNewBill() }
    }
    window.addEventListener('keydown', onKey); return () => window.removeEventListener('keydown', onKey)
  }, [])
  function label(b: BillSummaryResponse) {
    if (b.bill_type === 'table') return b.table_id ? tableMap[b.table_id] ?? 'Table' : 'Table'
    if (b.bill_type === 'parcel') return 'Parcel'
    return b.platform ? b.platform[0].toUpperCase() + b.platform.slice(1) : 'Online'
  }
  function BillRow({ bill, dim }: { bill: BillSummaryResponse; dim?: boolean }) {
    const Icon = TYPE_ICON[bill.bill_type]; const active = activeBillId === bill.id
    const itemText = bill.item_names.length > 0 ? bill.item_names.join(' · ') : null
    return (
      <button onClick={() => { setActiveBill(bill.id); onSelect?.() }} className={`w-full px-3 py-3 md:py-2 rounded-lg text-left transition-colors ${active ? 'bg-sphotel-accent-subtle text-sphotel-accent' : 'hover:bg-bg-base text-text-primary'} ${dim ? 'opacity-60' : ''}`}>
        <div className="flex items-start gap-2">
          <Icon size={13} className="shrink-0 opacity-60 mt-0.5" />
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-1">
              <p className="text-sm font-medium truncate">{label(bill)} <span className="text-xs font-normal opacity-50">#{bill.bill_number}</span></p>
              <div className="flex items-center gap-1.5 shrink-0">
                <span className="text-sm font-semibold">₹{(bill.total_paise / 100).toFixed(0)}</span>
                <span className={`w-2 h-2 rounded-full ${STATUS_DOT[bill.status]}`} />
              </div>
            </div>
            {bill.bill_type === 'table' && bill.waiter_name && <p className="text-xs text-text-muted truncate">Waiter: {bill.waiter_name}</p>}
            {itemText && <p className="text-xs text-text-muted truncate mt-0.5">{itemText}</p>}
          </div>
        </div>
      </button>
    )
  }
  return (
    <aside className="w-full md:w-56 shrink-0 bg-bg-surface border-r border-sphotel-border flex flex-col h-full overflow-hidden">
      <div className="px-3 pt-4 pb-2 flex items-center justify-between shrink-0 gap-2">
        <span className="text-xs font-medium text-text-muted uppercase tracking-wide truncate">Open Bills</span>
        <button onClick={startNewBill} disabled={!canOpenNewBill} className="w-9 h-9 md:w-6 md:h-6 shrink-0 flex items-center justify-center rounded-md bg-sphotel-accent text-sphotel-accent-fg hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed" title={canOpenNewBill ? 'New Bill (N)' : 'Printer offline'}><Plus size={16} /></button>
      </div>
      <div className="flex-1 overflow-y-auto px-2 pb-2 flex flex-col gap-0.5 min-h-0 overflow-x-hidden">
        {isLoading && <p className="text-xs text-text-muted px-2 py-4">Loading…</p>}
        {!isLoading && bills.length === 0 && (
          <div className="text-center py-8 text-text-muted">
            <p className="text-xs">No open bills</p>
            <button onClick={startNewBill} className="mt-2 text-xs text-sphotel-accent hover:opacity-80">Start one <kbd className="ml-1 px-1 py-0.5 text-[10px] bg-sphotel-accent-subtle rounded font-mono">N</kbd></button>
          </div>
        )}
        {bills.map((bill) => <BillRow key={bill.id} bill={bill} />)}
      </div>
      <div className="shrink-0 border-t border-sphotel-border flex flex-col">
        <div className="flex items-center">
          <button onClick={() => setShowPast((v) => !v)} className="flex-1 flex items-center gap-2 px-3 py-3 md:py-2 text-xs font-medium text-text-muted hover:text-text-primary transition-colors">
            {showPast ? <ChevronDown size={12} /> : <ChevronRight size={12} />} Past Bills
          </button>
          <button onClick={() => setShowHistory(true)} className="hidden md:flex items-center px-3 py-2 text-text-muted hover:text-text-primary" title="Browse all history"><Clock size={12} /></button>
        </div>
        {showPast && (
          <div className="px-2 pb-2 flex flex-col gap-0.5 max-h-[40vh] md:max-h-48 overflow-y-auto">
            {recentBills.length === 0 ? <p className="text-xs text-text-muted px-2 py-2">No past bills</p> : recentBills.map((bill) => <BillRow key={bill.id} bill={bill} dim />)}
          </div>
        )}
      </div>
      {showHistory && <PastBillsModal onClose={() => setShowHistory(false)} />}
    </aside>
  )
}
