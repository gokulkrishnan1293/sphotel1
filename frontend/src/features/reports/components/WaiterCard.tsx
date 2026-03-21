import { useState } from 'react'
import { Bell, FileText } from 'lucide-react'
import type { WaiterPerf } from '../types'
import type { FixedReportConfig } from '../api/fixedReportConfigs'
import { TelegramScheduleModal } from './TelegramScheduleModal'
import { openPdfPreview } from '../utils/reportPreview'

const fmt = (p: number) => `₹${(p / 100).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`

interface Props {
  data?: WaiterPerf[]
  config?: FixedReportConfig | null
  onUpdateConfig?: (cron: string | null) => void
}

export function WaiterCard({ data, config, onUpdateConfig }: Props) {
  const [q, setQ] = useState('')
  const [showTg, setShowTg] = useState(false)

  if (!data?.length) {
    return (
      <div className="bg-bg-elevated border border-sphotel-border rounded-xl p-5 flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-text-primary">Waiter Performance</h2>
        <p className="text-xs text-text-muted py-4 text-center">No waiter data for this period.</p>
      </div>
    )
  }

  const filtered = data.filter((w) => w.waiter_name.toLowerCase().includes(q.toLowerCase())).slice(0, 10)
  const max = Math.max(...data.map((w) => w.revenue_paise), 1)

  function preview() {
    openPdfPreview('Waiter Performance', 'Today', [{
      title: 'Revenue by Waiter',
      rows: data!.map((w) => ({ label: w.waiter_name, value: fmt(w.revenue_paise) })),
    }])
  }

  return (
    <div className="bg-bg-elevated border border-sphotel-border rounded-xl p-5 flex flex-col gap-1">
      <div className="flex items-center justify-between mb-3 gap-2">
        <h2 className="text-sm font-semibold text-text-primary">
          Waiter Performance <span className="text-xs font-normal text-text-muted ml-1">today</span>
        </h2>
        <div className="flex items-center gap-1.5">
          <button onClick={preview} title="Preview PDF" className="p-1 text-text-muted hover:text-text-primary"><FileText size={13} /></button>
          <button onClick={() => setShowTg(true)} title="Telegram schedule"
            className={`p-1 rounded ${config?.telegram_schedule ? 'text-sphotel-accent' : 'text-text-muted hover:text-sphotel-accent'}`}>
            <Bell size={13} />
          </button>
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter…"
            className="text-xs bg-bg-base border border-sphotel-border rounded px-2 py-0.5 w-20 text-text-primary focus:outline-none focus:ring-1 focus:ring-sphotel-accent" />
        </div>
      </div>
      {filtered.map((w, i) => (
        <div key={i} className="flex items-center gap-3 py-1">
          <span className="text-sm text-text-secondary w-28 truncate shrink-0">{w.waiter_name}</span>
          <div className="flex-1 bg-bg-base rounded-full h-2 overflow-hidden">
            <div className="h-full rounded-full bg-sphotel-accent" style={{ width: `${Math.round((w.revenue_paise / max) * 100)}%` }} />
          </div>
          <span className="text-xs text-text-muted w-16 text-right shrink-0">{fmt(w.revenue_paise)}</span>
        </div>
      ))}
      {filtered.length === 0 && <p className="text-xs text-text-muted py-2 text-center">No waiters match.</p>}
      {showTg && (
        <TelegramScheduleModal current={config?.telegram_schedule ?? null}
          onSave={(cron) => onUpdateConfig?.(cron)} onClose={() => setShowTg(false)} />
      )}
    </div>
  )
}
