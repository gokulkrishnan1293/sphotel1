import { useState, useMemo, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { X } from 'lucide-react'
import { tablesApi } from '../../admin/api/tables'
import { vendorsListWithCache } from '../../../lib/db/vendorsCache'
import { billsApi } from '../api/bills'
import type { BillResponse } from '../types/bills'
import { InlineDropdown } from './InlineDropdown'
import { WaiterSelect, type WaiterSelectHandle } from './WaiterSelect'

type TOption = { label: string; type: 'table' | 'parcel' | 'online'; vendor?: string; shortcut: number }
interface Props { bill: BillResponse; onDone?: () => void; onReset?: () => void }

export function BillContextBar({ bill, onDone, onReset }: Props) {
  const qc = useQueryClient()
  const inv = () => { qc.invalidateQueries({ queryKey: ['bill', bill.id] }); qc.invalidateQueries({ queryKey: ['bills', 'open'] }) }
  const update = useMutation({ mutationFn: (d: Parameters<typeof billsApi.updateBill>[1]) => billsApi.updateBill(bill.id, d), onSuccess: inv })
  const { data: sections = [] } = useQuery({ queryKey: ['sections'], queryFn: tablesApi.listSections })
  const { data: vendors = [] } = useQuery({ queryKey: ['online-vendors'], queryFn: vendorsListWithCache })
  const allTables = useMemo(() => sections.flatMap((s) => s.tables.filter((t) => t.is_active).map((t) => ({ ...t, sectionName: s.name }))), [sections])
  const tableMap = useMemo(() => { const m: Record<string, string> = {}; sections.forEach((s) => s.tables.forEach((t) => (m[t.id] = t.name))); return m }, [sections])
  const typeOpts = useMemo<TOption[]>(() => [{ label: 'Dine In', type: 'table', shortcut: 1 }, { label: 'Parcel', type: 'parcel', shortcut: 2 }, ...(vendors.length === 0 ? [{ label: 'Online', type: 'online' as const, shortcut: 3 }] : vendors.map((v, i) => ({ label: v.name, type: 'online' as const, vendor: v.slug, shortcut: 3 + i })))], [vendors])
  const initLabel = () => bill.bill_type === 'table' ? 'Dine In' : bill.bill_type === 'parcel' ? 'Parcel' : bill.platform ?? 'Online'
  const [typeQ, setTypeQ] = useState(initLabel); const [typeOpen, setTypeOpen] = useState(false); const [typeIdx, setTypeIdx] = useState(0)
  const [tableQ, setTableQ] = useState(''); const [tableOpen, setTableOpen] = useState(false); const [tableIdx, setTableIdx] = useState(0)
  const [refQ, setRefQ] = useState(bill.reference_no ?? '')
  const [showTable, setShowTable] = useState(bill.bill_type === 'table')
  const [showRef, setShowRef] = useState(bill.bill_type === 'online')
  const typeRef = useRef<HTMLInputElement>(null); const tableRef = useRef<HTMLInputElement>(null)
  const refRef = useRef<HTMLInputElement>(null); const waiterRef = useRef<WaiterSelectHandle>(null)
  useEffect(() => { if (bill.table_id && tableMap[bill.table_id]) setTableQ(tableMap[bill.table_id]) }, [tableMap, bill.table_id])
  const filteredTypes = useMemo(() => { const q = typeQ.toLowerCase(); return q ? typeOpts.filter((o) => o.label.toLowerCase().includes(q)) : typeOpts }, [typeOpts, typeQ])
  const filteredTables = useMemo(() => { const q = tableQ.toLowerCase(); return q ? allTables.filter((t) => t.name.toLowerCase().includes(q) || t.sectionName.toLowerCase().includes(q)) : allTables.slice(0, 14) }, [allTables, tableQ])
  const isClosed = bill.status === 'billed' || bill.status === 'void'
  const ic = 'bg-bg-elevated border border-sphotel-border rounded-md px-2 py-1 text-sm text-text-primary placeholder-text-muted outline-none focus:border-sphotel-accent transition-colors w-16 md:w-28'
  const icReq = (empty: boolean) => ic + (empty ? ' border-amber-500/60' : '')
  const waiterIc = 'w-full bg-bg-elevated border border-sphotel-border rounded-md px-2.5 py-1 text-sm text-text-primary placeholder-text-muted outline-none focus:border-sphotel-accent transition-colors'
  function pickType(o: TOption) {
    setTypeQ(o.label); setTypeOpen(false); setShowTable(o.type === 'table'); setShowRef(o.type === 'online')
    const d: Parameters<typeof billsApi.updateBill>[1] = { bill_type: o.type, platform: o.vendor ?? null }
    if (o.type !== 'table') Object.assign(d, { table_id: null, waiter_id: null })
    if (o.type !== 'online') Object.assign(d, { reference_no: null })
    update.mutate(d)
    if (o.type === 'table') setTimeout(() => tableRef.current?.focus(), 50)
    else if (o.type === 'online') setTimeout(() => refRef.current?.focus(), 50)
  }
  function pickTable(t: typeof allTables[0]) { setTableQ(t.name); setTableOpen(false); update.mutate({ table_id: t.id }); waiterRef.current?.focus() }
  return (
    <div className="px-4 py-2 md:px-6 border-b border-sphotel-border flex items-center gap-2 flex-nowrap">
      <span className="text-xs text-text-muted font-mono shrink-0">{bill.bill_number != null ? `#${bill.bill_number}` : 'Draft'}</span>
      {!isClosed ? (
        <>
          <div className="relative">
            <input ref={typeRef} value={typeQ} className={ic} onChange={(e) => { setTypeQ(e.target.value); setTypeOpen(true) }}
              onFocus={() => { if (typeQ) setTypeOpen(true) }} onBlur={() => setTimeout(() => setTypeOpen(false), 120)}
              onKeyDown={(e) => { if (e.key === 'ArrowDown') { e.preventDefault(); setTypeIdx((i) => Math.min(i + 1, filteredTypes.length - 1)) } else if (e.key === 'ArrowUp') { e.preventDefault(); setTypeIdx((i) => Math.max(i - 1, 0)) } else if (e.key === 'Enter') { e.preventDefault(); const o = filteredTypes[typeIdx]; if (o) pickType(o) } }} />
            {typeOpen && filteredTypes.length > 0 && <InlineDropdown activeIdx={typeIdx} onSelect={(k) => { const o = filteredTypes.find((x) => x.label === k); if (o) pickType(o) }} items={filteredTypes.map((o) => ({ key: o.label, label: <><kbd className="text-[10px] font-mono bg-bg-base border border-sphotel-border px-1 rounded opacity-60 shrink-0 mr-2">{o.shortcut}</kbd>{o.label}</> }))} />}
          </div>
          {showRef && <input ref={refRef} value={refQ} placeholder="Ref # *" className={icReq(!refQ)}
            onChange={(e) => setRefQ(e.target.value)}
            onBlur={() => { if (refQ !== (bill.reference_no ?? '')) update.mutate({ reference_no: refQ || null }) }}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); if (refQ !== (bill.reference_no ?? '')) update.mutate({ reference_no: refQ || null }); onDone?.() } }} />}
          {showTable && (
            <div className="relative">
              <input ref={tableRef} value={tableQ} placeholder="Table *" className={icReq(!bill.table_id)}
                onChange={(e) => { setTableQ(e.target.value); setTableOpen(true); setTableIdx(0) }}
                onFocus={() => { if (tableQ) setTableOpen(true) }} onBlur={() => setTimeout(() => setTableOpen(false), 120)}
                onKeyDown={(e) => { if (e.key === 'ArrowDown') { e.preventDefault(); setTableIdx((i) => Math.min(i + 1, filteredTables.length - 1)) } else if (e.key === 'ArrowUp') { e.preventDefault(); setTableIdx((i) => Math.max(i - 1, 0)) } else if (e.key === 'Enter') { e.preventDefault(); const t = filteredTables[tableIdx]; if (t) pickTable(t); else waiterRef.current?.focus() } }} />
              {tableOpen && filteredTables.length > 0 && <InlineDropdown activeIdx={tableIdx} onSelect={(k) => { const t = filteredTables.find((x) => x.name === k); if (t) pickTable(t) }} items={filteredTables.map((t) => ({ key: t.name, label: <>{t.name} <span className="text-xs text-text-muted">· {t.sectionName}</span></> }))} />}
            </div>
          )}
          {showTable && <WaiterSelect ref={waiterRef} required initialName={bill.waiter_name ?? ''} containerClassName="relative w-16 md:w-28" inputClassName={waiterIc + (!bill.waiter_id ? ' border-amber-500/60' : '')} onDone={(wid) => { if (wid) { update.mutate({ waiter_id: wid }); onDone?.() } }} />}
        </>
      ) : (
        [initLabel(), bill.table_id ? tableMap[bill.table_id] : null, bill.waiter_name, bill.reference_no].filter(Boolean).map((label) => (
          <span key={label} className="inline-flex items-center gap-1 px-2.5 py-1 bg-bg-elevated border border-sphotel-border rounded-md text-sm text-text-primary">
            <span className="text-[9px] text-status-success">✓</span> {label}
          </span>
        ))
      )}
      {onReset && !isClosed && (
        <button onClick={onReset} className="ml-auto flex items-center gap-1 px-2.5 py-1 text-xs text-text-muted hover:text-status-error rounded-md transition-colors border border-transparent hover:border-status-error/30">
          <X size={12} /><span className="hidden md:inline">Cancel</span>
        </button>
      )}
    </div>
  )
}
