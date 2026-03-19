import { useState, useEffect, useRef, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Check, UtensilsCrossed, ShoppingBag, Laptop } from 'lucide-react'
import { tablesApi } from '../../admin/api/tables'
import { staffApi } from '../../admin/api/staff'
import type { OpenBillRequest } from '../types/bills'

function parse(raw: string) {
  const s = raw.trim()
  if (!s) return { type: 'table' as const, tq: '', wq: '' }
  if (/^p(arcel)?$/i.test(s)) return { type: 'parcel' as const, tq: '', wq: '' }
  if (/^o\b/i.test(s)) return { type: 'online' as const, tq: '', wq: '', ref: s.replace(/^o\w*\s*/i, '').trim() }
  const wm = s.match(/^(.+?)\s+w\s+(.*)$/i)
  if (wm) return { type: 'table' as const, tq: wm[1].replace(/^t/i, '').trim(), wq: wm[2].trim() }
  const parts = s.split(/\s+/)
  const last = parts[parts.length - 1]
  if (parts.length >= 2 && /^\d+$/.test(last))
    return { type: 'table' as const, tq: parts.slice(0, -1).join(' ').replace(/^t/i, '').trim(), wq: last }
  return { type: 'table' as const, tq: s.replace(/^t/i, '').trim(), wq: '' }
}

interface Props { onOpen: (data: OpenBillRequest) => void; onClose: () => void; isLoading: boolean }

export function QuickBillBar({ onOpen, onClose, isLoading }: Props) {
  const [input, setInput] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const { data: sections = [] } = useQuery({ queryKey: ['sections'], queryFn: tablesApi.listSections })
  const { data: waiters = [] } = useQuery({ queryKey: ['waiters'], queryFn: staffApi.listWaiters })

  const allTables = useMemo(
    () => sections.flatMap((s) => s.tables.filter((t) => t.is_active).map((t) => ({ ...t, sectionName: s.name }))),
    [sections]
  )

  const parsed = useMemo(() => parse(input), [input])
  const { type, tq, wq } = parsed
  const ref = (parsed as { ref?: string }).ref ?? ''

  const matchedTable = useMemo(() => {
    if (type !== 'table' || !tq) return null
    const q = tq.toLowerCase()
    return allTables.find((t) => t.name.toLowerCase().includes(q)) ?? null
  }, [allTables, type, tq])

  const matchedWaiter = useMemo(() => {
    if (!wq) return null
    const num = Number(wq)
    if (/^\d+$/.test(wq)) return waiters.find((w) => w.short_code === num) ?? null
    const q = wq.toLowerCase()
    return waiters.find((w) => w.name.toLowerCase().includes(q)) ?? null
  }, [waiters, wq])

  useEffect(() => { inputRef.current?.focus() }, [])

  function submit() {
    const wid = matchedWaiter?.id ?? null
    if (type === 'parcel') { onOpen({ bill_type: 'parcel', waiter_id: wid }); return }
    if (type === 'online') { onOpen({ bill_type: 'online', reference_no: ref || null, waiter_id: wid }); return }
    onOpen({ bill_type: 'table', table_id: matchedTable?.id ?? null, waiter_id: wid })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative w-full max-w-md bg-bg-elevated border border-sphotel-border rounded-2xl shadow-2xl overflow-hidden">
        <div className="flex items-center gap-3 px-4 py-3 border-b border-sphotel-border">
          <kbd className="text-xs bg-sphotel-accent-subtle text-sphotel-accent px-1.5 py-0.5 rounded font-mono shrink-0">N</kbd>
          <input ref={inputRef} value={input} onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') submit(); else if (e.key === 'Escape') onClose() }}
            placeholder="t3  ·  t3 w priya  ·  p  ·  o sw123"
            className="flex-1 bg-transparent text-sm text-text-primary placeholder-text-muted outline-none" />
        </div>
        <div className="px-4 py-3 flex flex-col gap-2 min-h-[56px]">
          {type === 'parcel' && <Row icon={<ShoppingBag size={13} />} text="Parcel bill" ok />}
          {type === 'online' && <Row icon={<Laptop size={13} />} text={`Online · ref: ${ref || '—'}`} ok={!!ref} />}
          {type === 'table' && (
            <Row icon={<UtensilsCrossed size={13} />} ok={!!matchedTable}
              text={tq ? (matchedTable ? `${matchedTable.name} · ${matchedTable.sectionName} · ${matchedTable.capacity} seats` : `No table matching "${tq}"`) : 'Type a table name or number'} />
          )}
          {wq && <Row ok={!!matchedWaiter} text={matchedWaiter ? `Waiter: ${matchedWaiter.name}` : `No waiter matching "${wq}"`} />}
        </div>
        <div className="px-4 py-2 border-t border-sphotel-border flex items-center gap-4 text-xs text-text-muted">
          <span>Enter open</span><span>Esc cancel</span>
          <span className="ml-auto opacity-50">t3 · t3 w name · p · o ref</span>
        </div>
        <div className="px-4 pb-3">
          <button onClick={submit} disabled={isLoading}
            className="w-full bg-sphotel-accent text-sphotel-accent-fg rounded-lg py-2 text-sm font-medium disabled:opacity-50">
            {isLoading ? 'Opening…' : 'Open Bill'}
          </button>
        </div>
      </div>
    </div>
  )
}

function Row({ icon, text, ok }: { icon?: React.ReactNode; text: string; ok: boolean }) {
  return (
    <div className="flex items-center gap-2 text-sm">
      {icon && <span className="text-text-muted">{icon}</span>}
      {ok ? <Check size={13} className="text-status-success shrink-0" /> : <span className="w-[13px]" />}
      <span className={ok ? 'text-text-primary' : 'text-text-muted'}>{text}</span>
    </div>
  )
}
