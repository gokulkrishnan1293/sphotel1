import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { CheckCircle2, Circle, CheckCheck, Clock } from 'lucide-react'
import { kotApi } from '../api/kot'
import type { ActiveKot } from '../types/kot'

const FOOD_DOT: Record<string, string> = { veg: 'bg-emerald-500', egg: 'bg-yellow-400', non_veg: 'bg-red-500' }
const URGENT_MS = 15 * 60 * 1000

function useElapsed(iso: string) {
  const [now, setNow] = useState(Date.now())
  useEffect(() => { const t = setInterval(() => setNow(Date.now()), 10_000); return () => clearInterval(t) }, [])
  const ms = now - new Date(iso).getTime()
  const m = Math.floor(ms / 60_000)
  return { label: m < 1 ? '<1m' : `${m}m`, urgent: ms > URGENT_MS }
}

interface Props { kot: ActiveKot; onMarkReady: (id: string) => void; isMarking: boolean }

export function KotCard({ kot, onMarkReady, isMarking }: Props) {
  const qc = useQueryClient()
  const [checked, setChecked] = useState<Set<string>>(() => new Set(kot.ready_item_ids))
  const { label, urgent } = useElapsed(kot.fired_at)
  const allChecked = checked.size === kot.items.length

  // Sync from server refetch (without losing optimistic state mid-flight)
  useEffect(() => { setChecked(new Set(kot.ready_item_ids)) }, [kot.ready_item_ids.join(',')])  // eslint-disable-line react-hooks/exhaustive-deps

  const toggleMutation = useMutation({
    mutationFn: ({ itemId }: { itemId: string }) => kotApi.toggleItemReady(kot.id, itemId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['kot', 'active'] }),
  })

  function toggle(itemId: string) {
    setChecked((prev) => { const s = new Set(prev); s.has(itemId) ? s.delete(itemId) : s.add(itemId); return s })
    toggleMutation.mutate({ itemId })
  }

  return (
    <div className="bg-bg-elevated border border-sphotel-border rounded-xl p-4 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <span className="text-base font-bold text-text-primary">KOT #{kot.ticket_number}</span>
          <p className="text-xs text-text-muted mt-0.5">{kot.bill_label}</p>
        </div>
        <div className={`flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full ${urgent ? 'bg-status-warning/15 text-status-warning' : 'bg-bg-base text-text-muted'}`}>
          <Clock size={11} />{label}
        </div>
      </div>

      <ul className="flex flex-col gap-2">
        {kot.items.map((item) => (
          <li key={item.item_id} className="flex items-center gap-2.5 cursor-pointer" onClick={() => toggle(item.item_id)}>
            {checked.has(item.item_id)
              ? <CheckCircle2 size={17} className="text-status-success shrink-0" />
              : <Circle size={17} className="text-text-muted shrink-0" />}
            <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${FOOD_DOT[item.food_type]}`} />
            <span className={`flex-1 text-sm ${checked.has(item.item_id) ? 'line-through text-text-muted' : 'text-text-primary'}`}>{item.name}</span>
            <span className="text-sm font-bold text-text-secondary">×{item.quantity}</span>
          </li>
        ))}
      </ul>

      <button onClick={() => onMarkReady(kot.id)} disabled={isMarking}
        className={`w-full flex items-center justify-center gap-2 py-2 rounded-xl text-sm font-semibold transition-colors ${allChecked ? 'bg-status-success/15 text-status-success border border-status-success/30' : 'bg-bg-base text-text-secondary hover:bg-bg-elevated border border-sphotel-border'} disabled:opacity-50`}>
        <CheckCheck size={15} />
        {isMarking ? 'Marking…' : 'Mark All Ready'}
      </button>
    </div>
  )
}
