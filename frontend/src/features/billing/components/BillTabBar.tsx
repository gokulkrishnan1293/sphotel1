import { useEffect, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Plus, ShoppingBag, Laptop, UtensilsCrossed, Clock } from 'lucide-react'
import { PastBillsModal } from './PastBillsModal'
import { billsApi } from '../api/bills'
import { tablesApi } from '../../admin/api/tables'
import { useBillingStore } from '../stores/billingStore'
import { useShortcutStore, matchKey } from '@/lib/shortcutStore'
import { toast } from '@/lib/toast'
import type { BillSummaryResponse, BillType } from '../types/bills'

const TYPE_ICON: Record<BillType, React.ElementType> = { table: UtensilsCrossed, parcel: ShoppingBag, online: Laptop }

interface Props { canOpenNewBill: boolean; onNewBill: () => void }

export function BillTabBar({ canOpenNewBill, onNewBill }: Props) {
  const { activeBillId, setActiveBill } = useBillingStore()
  const [showHistory, setShowHistory] = useState(false)
  const { data: bills = [] } = useQuery({ queryKey: ['bills', 'open'], queryFn: billsApi.listOpen, refetchInterval: 15_000 })
  const { data: sections = [] } = useQuery({ queryKey: ['sections'], queryFn: tablesApi.listSections })
  const tableMap = useMemo(() => { const m: Record<string, string> = {}; sections.forEach((s) => s.tables.forEach((t) => (m[t.id] = t.name))); return m }, [sections])

  function startNew() { if (!canOpenNewBill) { toast('Printer offline — cannot open new bills from this device'); return }; onNewBill() }

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const tag = (document.activeElement as HTMLElement)?.tagName
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return
      if (matchKey(e, useShortcutStore.getState().shortcuts.new_bill)) { e.preventDefault(); startNew() }
    }
    window.addEventListener('keydown', onKey); return () => window.removeEventListener('keydown', onKey)
  }, [canOpenNewBill]) // eslint-disable-line react-hooks/exhaustive-deps

  function label(b: BillSummaryResponse) {
    if (b.bill_type === 'table') return b.table_id ? tableMap[b.table_id] ?? 'Table' : 'Table'
    if (b.bill_type === 'parcel') return 'Parcel'
    return b.platform ? b.platform[0].toUpperCase() + b.platform.slice(1) : 'Online'
  }

  return (
    <>
    <div className="flex items-center gap-1 px-3 py-2 border-b border-sphotel-border bg-bg-surface overflow-x-auto shrink-0 w-full min-w-0 flex-nowrap">
      <button onClick={startNew}
        className="flex items-center gap-1 px-3 py-1.5 rounded-md text-xs font-medium bg-sphotel-accent text-sphotel-accent-fg hover:opacity-90 shrink-0">
        <Plus size={12} /> New <kbd className="hidden md:inline opacity-60 font-mono ml-0.5">N</kbd>
      </button>
      <button onClick={() => setShowHistory(true)} title="Past bills"
        className="flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs text-text-muted hover:text-text-primary hover:bg-bg-elevated shrink-0">
        <Clock size={12} /> <span className="hidden md:inline">History</span>
      </button>
      <span className="w-px h-4 bg-sphotel-border shrink-0 mx-1" />
      {bills.length === 0 && <span className="text-xs text-text-muted px-2 italic">No open bills</span>}
      {bills.map((b) => {
        const Icon = TYPE_ICON[b.bill_type]; const active = b.id === activeBillId
        return (
          <button key={b.id} onClick={() => setActiveBill(b.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-colors shrink-0 ${active ? 'bg-sphotel-accent-subtle text-sphotel-accent border border-sphotel-accent/30' : 'text-text-muted hover:text-text-primary hover:bg-bg-elevated'}`}>
            <Icon size={11} />
            {label(b)}
            {b.total_paise > 0 && <span className={`font-normal ${active ? 'text-sphotel-accent/70' : 'text-text-muted'}`}>₹{(b.total_paise / 100).toFixed(0)}</span>}
          </button>
        )
      })}
    </div>
    {showHistory && <PastBillsModal onClose={() => setShowHistory(false)} />}
    </>
  )
}
