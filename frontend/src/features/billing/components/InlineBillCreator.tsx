import { useState, useRef, useMemo, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Check } from 'lucide-react'
import { tablesApi } from '../../admin/api/tables'
import { vendorsListWithCache } from '../../../lib/db/vendorsCache'
import { billsApi } from '../api/bills'
import { useBillingStore } from '../stores/billingStore'
import { toast } from '@/lib/toast'
import { InlineDropdown } from './InlineDropdown'
import { WaiterSelect, type WaiterSelectHandle } from './WaiterSelect'
import type { OpenBillRequest } from '../types/bills'

type TypeOpt = { label: string; type: 'table' | 'parcel' | 'online'; vendor?: string; shortcut: number }
interface Props { canOpen: boolean; onCreated?: () => void }

export function InlineBillCreator({ canOpen, onCreated }: Props) {
  const qc = useQueryClient()
  const { setActiveBill } = useBillingStore()
  const { data: sections = [] } = useQuery({ queryKey: ['sections'], queryFn: tablesApi.listSections })
  const { data: vendors = [] } = useQuery({ queryKey: ['online-vendors'], queryFn: vendorsListWithCache })

  const openBill = useMutation({
    mutationFn: (d: OpenBillRequest) => billsApi.open(d),
    onSuccess: (bill) => { qc.setQueryData(['bill', bill.id], bill); qc.invalidateQueries({ queryKey: ['bills', 'open'] }); setActiveBill(bill.id); onCreated?.() },
    onError: (err) => { if ((err as any).offline) toast('Cannot open a new bill while offline') },
  })

  const allTables = useMemo(() => sections.flatMap((s) => s.tables.filter((t) => t.is_active).map((t) => ({ ...t, sectionName: s.name }))), [sections])
  const typeOptions = useMemo<TypeOpt[]>(() => [{ label: 'Dine In', type: 'table', shortcut: 1 }, { label: 'Parcel', type: 'parcel', shortcut: 2 },
    ...(vendors.length === 0 ? [{ label: 'Online', type: 'online' as const, shortcut: 3 }] : vendors.map((v, i) => ({ label: v.name, type: 'online' as const, vendor: v.slug, shortcut: 3 + i })))], [vendors])

  const [typeQ, setTypeQ] = useState(''); const [selType, setSelType] = useState<TypeOpt | null>(null)
  const [typeOpen, setTypeOpen] = useState(false); const [typeIdx, setTypeIdx] = useState(0)
  const typeRef = useRef<HTMLInputElement>(null)
  const [ctxQ, setCtxQ] = useState(''); const [selTable, setSelTable] = useState<typeof allTables[0] | null>(null)
  const [ctxOpen, setCtxOpen] = useState(false); const [ctxIdx, setCtxIdx] = useState(0)
  const ctxRef = useRef<HTMLInputElement>(null)
  const waiterRef = useRef<WaiterSelectHandle>(null)

  useEffect(() => { typeRef.current?.focus() }, [])

  const filteredTypes = useMemo(() => { const q = typeQ.trim().toLowerCase(); return q ? typeOptions.filter((o) => o.label.toLowerCase().includes(q) || String(o.shortcut) === q) : typeOptions }, [typeOptions, typeQ])
  const filteredTables = useMemo(() => { const q = ctxQ.toLowerCase(); return q ? allTables.filter((t) => t.name.toLowerCase().includes(q) || t.sectionName.toLowerCase().includes(q)) : allTables.slice(0, 14) }, [allTables, ctxQ])

  function submit(req: OpenBillRequest) {
    if (openBill.isPending) return
    if (!canOpen) { toast('Printer is offline — cannot open new bills from this device'); return }
    openBill.mutate(req)
  }
  function pickType(opt: TypeOpt) {
    setSelType(opt); setTypeQ(opt.label); setTypeOpen(false); setTypeIdx(0)
    if (opt.type === 'parcel') submit({ bill_type: 'parcel' })
    else { ctxRef.current?.focus(); setCtxOpen(true) }
  }
  function pickTable(t: typeof allTables[0]) {
    setSelTable(t); setCtxQ(t.name); setCtxOpen(false); setCtxIdx(0)
    waiterRef.current?.focus()
  }

  const inputCls = 'w-full bg-bg-elevated border border-sphotel-border rounded-lg px-3 py-3 md:py-2.5 text-sm text-text-primary placeholder-text-muted outline-none focus:border-sphotel-accent transition-colors pr-7'
  return (
    <div className="flex flex-col p-4 md:p-4 border-b border-sphotel-border">
      <div className="flex flex-col md:flex-row gap-2">
        <div className="relative w-full md:flex-1">
          <input ref={typeRef} value={typeQ} placeholder="1 Dine In · 2 Parcel · 3…" className={inputCls}
            onChange={(e) => { const v = e.target.value; setTypeQ(v); setSelType(null); setTypeOpen(true); setTypeIdx(0); const x = typeOptions.find((o) => String(o.shortcut) === v.trim()); if (x) pickType(x) }}
            onFocus={() => setTypeOpen(true)} onBlur={() => setTimeout(() => setTypeOpen(false), 120)}
            onKeyDown={(e) => { if (e.key === 'ArrowDown') { e.preventDefault(); setTypeIdx((i) => Math.min(i + 1, filteredTypes.length - 1)) } else if (e.key === 'ArrowUp') { e.preventDefault(); setTypeIdx((i) => Math.max(i - 1, 0)) } else if (e.key === 'Enter') { e.preventDefault(); const o = filteredTypes[typeIdx]; if (o) pickType(o) } }} />
          {selType && <Check size={12} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-status-success pointer-events-none" />}
          {typeOpen && filteredTypes.length > 0 && <InlineDropdown activeIdx={typeIdx} onSelect={(k) => { const o = filteredTypes.find((t) => t.label === k); if (o) pickType(o) }}
            items={filteredTypes.map((o) => ({ key: o.label, label: <><kbd className="text-[10px] font-mono bg-bg-base border border-sphotel-border px-1 rounded opacity-60 shrink-0 mr-2">{o.shortcut}</kbd>{o.label}</> }))} />}
        </div>

        {selType && selType.type === 'table' && (
          <div className="relative w-full md:flex-1">
            <input ref={ctxRef} value={ctxQ} placeholder="Table…" className={inputCls}
              onChange={(e) => { setCtxQ(e.target.value); setSelTable(null); setCtxOpen(true); setCtxIdx(0) }}
              onFocus={() => setCtxOpen(true)} onBlur={() => setTimeout(() => setCtxOpen(false), 120)}
              onKeyDown={(e) => { if (e.key === 'ArrowDown') { e.preventDefault(); setCtxIdx((i) => Math.min(i + 1, filteredTables.length - 1)) } else if (e.key === 'ArrowUp') { e.preventDefault(); setCtxIdx((i) => Math.max(i - 1, 0)) } else if (e.key === 'Enter') { e.preventDefault(); const t = filteredTables[ctxIdx]; if (t) pickTable(t) } }} />
            {selTable && <Check size={12} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-status-success pointer-events-none" />}
            {ctxOpen && filteredTables.length > 0 && <InlineDropdown activeIdx={ctxIdx} onSelect={(k) => { const t = filteredTables.find((x) => x.name === k); if (t) pickTable(t) }}
              items={filteredTables.map((t) => ({ key: t.name, label: <>{t.name} <span className="text-xs text-text-muted">· {t.sectionName}</span></> }))} />}
          </div>
        )}

        {selType && selType.type === 'table' && selTable && (
          <WaiterSelect ref={waiterRef} required onDone={(wid) => wid && submit({ bill_type: 'table', table_id: selTable.id, waiter_id: wid })} />
        )}

        {selType?.type === 'online' && <div className="w-full md:flex-1">
          <input ref={ctxRef} value={ctxQ} placeholder="Order ref… (Enter to open)" className={inputCls} onChange={(e) => setCtxQ(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); submit({ bill_type: 'online', platform: selType.vendor ?? null, reference_no: ctxQ || null }) } }} /></div>}
      </div>
      <span className="mt-3 hidden md:inline text-xs text-text-muted">↑↓ navigate · Enter select · Parcel opens instantly · Dine In: table then waiter (required)</span>
    </div>
  )
}
