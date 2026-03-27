import { useState, useMemo, useRef, forwardRef, useImperativeHandle } from 'react'
import { useQuery } from '@tanstack/react-query'
import { waitersListWithCache } from '../../../lib/db/waitersCache'
import { InlineDropdown } from './InlineDropdown'

interface Props { onDone: (waiterId: string | null) => void; initialName?: string; containerClassName?: string; inputClassName?: string; required?: boolean }
export interface WaiterSelectHandle { focus: () => void }

const DEFAULT_INPUT = 'w-full bg-bg-elevated border border-sphotel-border rounded-lg px-3 py-3 md:py-2.5 text-sm text-text-primary placeholder-text-muted outline-none focus:border-sphotel-accent transition-colors'
export const WaiterSelect = forwardRef<WaiterSelectHandle, Props>(({ onDone, initialName = '', containerClassName = 'relative w-full md:flex-1', inputClassName = DEFAULT_INPUT, required = false }, ref) => {
  const { data: waiters = [] } = useQuery({ queryKey: ['waiters'], queryFn: waitersListWithCache })
  const [q, setQ] = useState(initialName); const [open, setOpen] = useState(false); const [idx, setIdx] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  useImperativeHandle(ref, () => ({ focus: () => { inputRef.current?.focus(); setOpen(true) } }))

  const filtered = useMemo(() => {
    if (!q.trim()) return waiters.slice(0, 14)
    const lq = q.toLowerCase(); const num = Number(q)
    return waiters.filter((w) => w.name.toLowerCase().includes(lq) || (!isNaN(num) && w.short_code === num))
  }, [waiters, q])

  function pick(w: typeof waiters[0]) { setQ(w.name); setOpen(false); onDone(w.id) }

  return (
    <div className={containerClassName}>
      <input ref={inputRef} value={q} placeholder={required ? 'Waiter *' : 'Waiter… (Enter to skip)'}
        onChange={(e) => { setQ(e.target.value); setOpen(true); setIdx(0) }}
        onFocus={() => setOpen(true)} onBlur={() => setTimeout(() => setOpen(false), 120)}
        onKeyDown={(e) => {
          if (e.key === 'ArrowDown') { e.preventDefault(); setIdx((i) => Math.min(i + 1, filtered.length - 1)) }
          else if (e.key === 'ArrowUp') { e.preventDefault(); setIdx((i) => Math.max(i - 1, 0)) }
          else if (e.key === 'Enter') { e.preventDefault(); if (filtered[idx]) pick(filtered[idx]); else if (!required) onDone(null) }
        }}
        className={inputClassName} />
      {open && filtered.length > 0 && <InlineDropdown activeIdx={idx} onSelect={(k) => { const w = filtered.find((x) => x.name === k); if (w) pick(w) }}
        items={filtered.map((w) => ({ key: w.name, label: <>{w.name}{w.short_code != null && <span className="text-xs text-text-muted ml-1.5">#{w.short_code}</span>}</> }))} />}
    </div>
  )
})
WaiterSelect.displayName = 'WaiterSelect'
