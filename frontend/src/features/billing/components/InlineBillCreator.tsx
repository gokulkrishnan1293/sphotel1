import { useState, useEffect, useRef, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Check } from 'lucide-react'
import { tablesApi } from '../../admin/api/tables'
import { waitersListWithCache } from '../../../lib/db/waitersCache'
import { vendorsListWithCache } from '../../../lib/db/vendorsCache'
import { billsApi } from '../api/bills'
import { useBillingStore } from '../stores/billingStore'
import { toast } from '@/lib/toast'
import type { OpenBillRequest } from '../types/bills'

type TypeOpt = { label: string; type: 'table' | 'parcel' | 'online'; vendor?: string; shortcut: number }

interface Props {
  canOpen: boolean
  onCreated?: () => void
}

export function InlineBillCreator({ canOpen, onCreated }: Props) {
  const qc = useQueryClient()
  const { setActiveBill } = useBillingStore()

  const { data: sections = [] } = useQuery({ queryKey: ['sections'], queryFn: tablesApi.listSections })
  const { data: waiters = [] } = useQuery({ queryKey: ['waiters'], queryFn: waitersListWithCache })
  const { data: vendors = [] } = useQuery({ queryKey: ['online-vendors'], queryFn: vendorsListWithCache })

  const openBill = useMutation({
    mutationFn: (data: OpenBillRequest) => billsApi.open(data),
    onSuccess: (bill) => {
      qc.invalidateQueries({ queryKey: ['bills', 'open'] })
      setActiveBill(bill.id)
      onCreated?.()
    },
    onError: (err) => {
      if ((err as any).offline) toast('Cannot open a new bill while offline')
    },
  })

  const allTables = useMemo(
    () => sections.flatMap((s) => s.tables.filter((t) => t.is_active).map((t) => ({ ...t, sectionName: s.name }))),
    [sections]
  )

  const typeOptions = useMemo<TypeOpt[]>(() => {
    const vendorOpts = vendors.map((v, i) => ({ label: v.name, type: 'online' as const, vendor: v.slug, shortcut: 3 + i }))
    return [
      { label: 'Dine In', type: 'table', shortcut: 1 },
      { label: 'Parcel', type: 'parcel', shortcut: 2 },
      ...(vendors.length === 0 ? [{ label: 'Online', type: 'online' as const, shortcut: 3 }] : vendorOpts),
    ]
  }, [vendors])

  // Box 1: Type
  const [typeQ, setTypeQ] = useState('')
  const [selType, setSelType] = useState<TypeOpt | null>(null)
  const [typeOpen, setTypeOpen] = useState(false)
  const [typeIdx, setTypeIdx] = useState(0)
  const typeRef = useRef<HTMLInputElement>(null)

  // Box 2: Table or order ref
  const [ctxQ, setCtxQ] = useState('')
  const [selTable, setSelTable] = useState<typeof allTables[0] | null>(null)
  const [ctxOpen, setCtxOpen] = useState(false)
  const [ctxIdx, setCtxIdx] = useState(0)
  const ctxRef = useRef<HTMLInputElement>(null)

  // Box 3: Waiter
  const [waiterQ, setWaiterQ] = useState('')
  const [selWaiter, setSelWaiter] = useState<typeof waiters[0] | null>(null)
  const [waiterOpen, setWaiterOpen] = useState(false)
  const [waiterIdx, setWaiterIdx] = useState(0)
  const waiterRef = useRef<HTMLInputElement>(null)

  useEffect(() => { typeRef.current?.focus() }, [])

  const filteredTypes = useMemo(() => {
    if (!typeQ.trim()) return typeOptions
    const q = typeQ.trim().toLowerCase()
    return typeOptions.filter((o) => o.label.toLowerCase().includes(q) || String(o.shortcut) === q)
  }, [typeOptions, typeQ])

  const filteredTables = useMemo(() => {
    if (!ctxQ.trim()) return allTables.slice(0, 14)
    const q = ctxQ.toLowerCase()
    return allTables.filter((t) => t.name.toLowerCase().includes(q) || t.sectionName.toLowerCase().includes(q))
  }, [allTables, ctxQ])

  const filteredWaiters = useMemo(() => {
    if (!waiterQ.trim()) return waiters.slice(0, 14)
    const q = waiterQ.toLowerCase()
    const num = Number(waiterQ)
    return waiters.filter((w) => w.name.toLowerCase().includes(q) || (!isNaN(num) && w.short_code === num))
  }, [waiters, waiterQ])

  function pickType(opt: TypeOpt) {
    setSelType(opt)
    setTypeQ(opt.label)
    setTypeOpen(false)
    setTypeIdx(0)
    if (opt.type === 'parcel') {
      waiterRef.current?.focus()
      setWaiterOpen(true)
    } else {
      ctxRef.current?.focus()
      setCtxOpen(true)
    }
  }

  function pickTable(t: typeof allTables[0]) {
    setSelTable(t)
    setCtxQ(t.name)
    setCtxOpen(false)
    setCtxIdx(0)
    waiterRef.current?.focus()
    setWaiterOpen(true)
  }

  function pickWaiter(w: typeof waiters[0]) {
    setSelWaiter(w)
    setWaiterQ(w.name)
    setWaiterOpen(false)
    setWaiterIdx(0)
  }

  function submit() {
    if (!selType || openBill.isPending) return
    if (!canOpen) { toast('Printer is offline — cannot open new bills from this device'); return }
    const waiterId = selWaiter?.id ?? null
    if (selType.type === 'parcel') {
      openBill.mutate({ bill_type: 'parcel', waiter_id: waiterId })
    } else if (selType.type === 'online') {
      openBill.mutate({ bill_type: 'online', platform: selType.vendor ?? null, reference_no: ctxQ || null, waiter_id: waiterId })
    } else {
      if (!selTable) { ctxRef.current?.focus(); return }
      openBill.mutate({ bill_type: 'table', table_id: selTable.id, waiter_id: waiterId })
    }
  }

  return (
    <div className="flex-1 flex flex-col p-4 md:p-6">
      <p className="text-xs font-medium text-text-muted uppercase tracking-wide mb-4">New Bill</p>
      <div className="flex flex-col md:flex-row gap-2">

        {/* Box 1: Order type */}
        <div className="relative w-full md:flex-1">
          <input
            ref={typeRef}
            value={typeQ}
            onChange={(e) => {
              const v = e.target.value
              setTypeQ(v); setSelType(null); setTypeOpen(true); setTypeIdx(0)
              // Auto-select when user types the shortcut number (e.g. "1" → Dine In)
              const exact = typeOptions.find((o) => String(o.shortcut) === v.trim())
              if (exact) { pickType(exact) }
            }}
            onFocus={() => setTypeOpen(true)}
            onBlur={() => setTimeout(() => setTypeOpen(false), 120)}
            onKeyDown={(e) => {
              if (e.key === 'ArrowDown') { e.preventDefault(); setTypeIdx((i) => Math.min(i + 1, filteredTypes.length - 1)) }
              else if (e.key === 'ArrowUp') { e.preventDefault(); setTypeIdx((i) => Math.max(i - 1, 0)) }
              else if (e.key === 'Enter') { e.preventDefault(); const o = filteredTypes[typeIdx]; if (o) pickType(o) }
            }}
            placeholder="1 Dine In · 2 Parcel · 3…"
            className="w-full bg-bg-elevated border border-sphotel-border rounded-lg px-3 py-3 md:py-2.5 text-sm text-text-primary placeholder-text-muted outline-none focus:border-sphotel-accent transition-colors pr-7"
          />
          {selType && <Check size={12} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-status-success pointer-events-none" />}
          {typeOpen && filteredTypes.length > 0 && (
            <div className="absolute top-full mt-1 left-0 right-0 bg-bg-elevated border border-sphotel-border rounded-lg shadow-xl z-20 overflow-hidden max-h-52 overflow-y-auto">
              {filteredTypes.map((o, i) => (
                <button key={o.label} type="button" onMouseDown={() => pickType(o)}
                  className={`w-full text-left px-3 py-2 text-sm transition-colors flex items-center gap-2 ${i === typeIdx ? 'bg-sphotel-accent-subtle text-sphotel-accent' : 'hover:bg-bg-base text-text-primary'}`}>
                  <kbd className="text-[10px] font-mono bg-bg-base border border-sphotel-border px-1 rounded opacity-60 shrink-0">{o.shortcut}</kbd>
                  {o.label}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Box 2: Table (dine-in) or order ref (online) */}
        {selType && selType.type !== 'parcel' && (
          <div className="relative w-full md:flex-1">
            <input
              ref={ctxRef}
              value={ctxQ}
              onChange={(e) => { setCtxQ(e.target.value); setSelTable(null); setCtxOpen(true); setCtxIdx(0) }}
              onFocus={() => setCtxOpen(true)}
              onBlur={() => setTimeout(() => setCtxOpen(false), 120)}
              onKeyDown={(e) => {
                if (selType.type === 'table') {
                  if (e.key === 'ArrowDown') { e.preventDefault(); setCtxIdx((i) => Math.min(i + 1, filteredTables.length - 1)) }
                  else if (e.key === 'ArrowUp') { e.preventDefault(); setCtxIdx((i) => Math.max(i - 1, 0)) }
                  else if (e.key === 'Enter') { e.preventDefault(); const t = filteredTables[ctxIdx]; if (t) pickTable(t) }
                } else if (e.key === 'Enter') {
                  e.preventDefault()
                  setCtxOpen(false)
                  waiterRef.current?.focus()
                  setWaiterOpen(true)
                }
              }}
              placeholder={selType.type === 'table' ? 'Table…' : 'Order ref…'}
              className="w-full bg-bg-elevated border border-sphotel-border rounded-lg px-3 py-3 md:py-2.5 text-sm text-text-primary placeholder-text-muted outline-none focus:border-sphotel-accent transition-colors pr-7"
            />
            {selTable && <Check size={12} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-status-success pointer-events-none" />}
            {ctxOpen && selType.type === 'table' && filteredTables.length > 0 && (
              <div className="absolute top-full mt-1 left-0 right-0 bg-bg-elevated border border-sphotel-border rounded-lg shadow-xl z-20 overflow-hidden max-h-52 overflow-y-auto">
                {filteredTables.map((t, i) => (
                  <button key={t.id} type="button" onMouseDown={() => pickTable(t)}
                    className={`w-full text-left px-3 py-2 text-sm transition-colors ${i === ctxIdx ? 'bg-sphotel-accent-subtle text-sphotel-accent' : 'hover:bg-bg-base text-text-primary'}`}>
                    {t.name} <span className="text-xs text-text-muted">· {t.sectionName}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Box 3: Waiter */}
        <div className="relative w-full md:flex-1">
          <input
            ref={waiterRef}
            value={waiterQ}
            onChange={(e) => { setWaiterQ(e.target.value); setSelWaiter(null); setWaiterOpen(true); setWaiterIdx(0) }}
            onFocus={() => setWaiterOpen(true)}
            onBlur={() => setTimeout(() => setWaiterOpen(false), 120)}
            onKeyDown={(e) => {
              if (e.key === 'ArrowDown') { e.preventDefault(); setWaiterIdx((i) => Math.min(i + 1, filteredWaiters.length - 1)) }
              else if (e.key === 'ArrowUp') { e.preventDefault(); setWaiterIdx((i) => Math.max(i - 1, 0)) }
              else if (e.key === 'Enter') {
                e.preventDefault()
                if (!selWaiter && waiterQ && filteredWaiters.length > 0) {
                  pickWaiter(filteredWaiters[waiterIdx])
                } else {
                  submit()
                }
              }
            }}
            placeholder="Waiter…"
            className="w-full bg-bg-elevated border border-sphotel-border rounded-lg px-3 py-3 md:py-2.5 text-sm text-text-primary placeholder-text-muted outline-none focus:border-sphotel-accent transition-colors pr-7"
          />
          {selWaiter && <Check size={12} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-status-success pointer-events-none" />}
          {waiterOpen && filteredWaiters.length > 0 && (
            <div className="absolute top-full mt-1 left-0 right-0 bg-bg-elevated border border-sphotel-border rounded-lg shadow-xl z-20 overflow-hidden max-h-52 overflow-y-auto">
              {filteredWaiters.map((w, i) => (
                <button key={w.id} type="button" onMouseDown={() => pickWaiter(w)}
                  className={`w-full text-left px-3 py-2 text-sm transition-colors ${i === waiterIdx ? 'bg-sphotel-accent-subtle text-sphotel-accent' : 'hover:bg-bg-base text-text-primary'}`}>
                  {w.name}{w.short_code != null && <span className="text-xs text-text-muted ml-1.5">#{w.short_code}</span>}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="mt-4 flex items-center gap-4">
        <button
          onClick={submit}
          disabled={openBill.isPending || !selType || (selType.type === 'table' && !selTable)}
          className="px-5 py-3 md:py-2 bg-sphotel-accent text-sphotel-accent-fg rounded-lg text-sm font-medium hover:opacity-90 disabled:opacity-40 transition-opacity"
        >
          {openBill.isPending ? 'Opening…' : 'Open Bill'}
        </button>
        <span className="hidden md:inline text-xs text-text-muted">↑↓ navigate · Enter select · Enter on waiter opens bill</span>
      </div>
    </div>
  )
}
