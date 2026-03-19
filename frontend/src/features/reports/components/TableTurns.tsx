import type { TableTurn } from '../types'
import { Clock } from 'lucide-react'

function fmtMins(m: number) {
  if (m < 60) return `${m}m`
  return `${Math.floor(m / 60)}h ${m % 60}m`
}

function TurnBar({ minutes, max }: { minutes: number; max: number }) {
  const pct = Math.round((minutes / max) * 100)
  const color = minutes > 90 ? 'bg-status-error' : minutes > 60 ? 'bg-yellow-400' : 'bg-emerald-500'
  return (
    <div className="flex items-center gap-2 flex-1">
      <div className="flex-1 bg-bg-base rounded-full h-1.5 overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-text-secondary w-12 text-right">{fmtMins(minutes)}</span>
    </div>
  )
}

export function TableTurns({ data }: { data: TableTurn[] }) {
  if (!data.length) return <p className="text-sm text-text-muted text-center py-8">No table billing data for this period.</p>
  const max = Math.max(...data.map((t) => t.avg_minutes))
  const overall = Math.round(data.reduce((s, t) => s + t.avg_minutes * t.turn_count, 0) / data.reduce((s, t) => s + t.turn_count, 0))

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2 text-sm text-text-secondary bg-bg-elevated border border-sphotel-border rounded-lg px-4 py-3">
        <Clock size={14} />
        <span>Overall avg turn time: <span className="font-semibold text-text-primary">{fmtMins(overall)}</span></span>
        <span className="text-text-muted ml-1">· {data.reduce((s, t) => s + t.turn_count, 0)} tables billed</span>
      </div>

      <div className="flex flex-col gap-2">
        {data.map((t, i) => (
          <div key={i} className="flex items-center gap-3">
            <span className="text-sm text-text-secondary w-20 shrink-0 truncate">{t.table_name}</span>
            <TurnBar minutes={t.avg_minutes} max={max} />
            <span className="text-xs text-text-muted w-14 text-right shrink-0">{t.turn_count} turns</span>
          </div>
        ))}
      </div>
    </div>
  )
}
