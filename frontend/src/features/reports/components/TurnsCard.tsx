import { useState } from 'react'
import type { TableTurn } from '../types'

function fmtMins(m: number) { return m < 60 ? `${m}m` : `${Math.floor(m / 60)}h ${m % 60}m` }

export function TurnsCard({ data }: { data?: TableTurn[] }) {
  const [q, setQ] = useState('')

  if (!data?.length) {
    return (
      <div className="bg-bg-elevated border border-sphotel-border rounded-xl p-5 flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-text-primary">Table Turns</h2>
        <p className="text-xs text-text-muted py-4 text-center">No turn data for this period.</p>
      </div>
    )
  }

  const filtered = data.filter((t) => t.table_name.toLowerCase().includes(q.toLowerCase())).slice(0, 10)
  const max = Math.max(...data.map((t) => t.avg_minutes), 1)

  return (
    <div className="bg-bg-elevated border border-sphotel-border rounded-xl p-5 flex flex-col gap-1">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-text-primary">
          Table Turns <span className="text-xs font-normal text-text-muted ml-1">avg time · last 7 days</span>
        </h2>
        <input
          value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter…"
          className="text-xs bg-bg-base border border-sphotel-border rounded px-2 py-0.5 w-24 text-text-primary focus:outline-none focus:ring-1 focus:ring-sphotel-accent"
        />
      </div>
      {filtered.map((t, i) => {
        const pct = Math.round((t.avg_minutes / max) * 100)
        const color = t.avg_minutes > 90 ? 'bg-status-error' : t.avg_minutes > 60 ? 'bg-yellow-400' : 'bg-emerald-500'
        return (
          <div key={i} className="flex items-center gap-3 py-1">
            <span className="text-sm text-text-secondary w-20 truncate shrink-0">{t.table_name}</span>
            <div className="flex-1 bg-bg-base rounded-full h-2 overflow-hidden">
              <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
            </div>
            <span className="text-xs text-text-muted w-10 text-right shrink-0">{fmtMins(t.avg_minutes)}</span>
          </div>
        )
      })}
      {filtered.length === 0 && <p className="text-xs text-text-muted py-2 text-center">No tables match.</p>}
    </div>
  )
}
