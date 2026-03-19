import { useState } from 'react'
import { Bell, FileText } from 'lucide-react'
import type { FixedReportConfig } from '../api/fixedReportConfigs'
import { TelegramScheduleModal } from './TelegramScheduleModal'
import { openPdfPreview } from '../utils/reportPreview'

interface Props {
  items: { name: string; qty: number }[]
  config?: FixedReportConfig | null
  onUpdateConfig?: (cron: string | null) => void
}

export function TopItemsCard({ items, config, onUpdateConfig }: Props) {
  const [q, setQ] = useState('')
  const [showTg, setShowTg] = useState(false)
  if (!items.length) return null

  const filtered = items.filter((i) => i.name.toLowerCase().includes(q.toLowerCase())).slice(0, 10)
  const max = Math.max(...items.map((i) => i.qty), 1)

  function preview() {
    openPdfPreview('Top Items Today', 'Today', [{
      title: 'Items Sold',
      rows: items.slice(0, 10).map((i) => ({ label: i.name, value: `×${i.qty}` })),
    }])
  }

  return (
    <div className="bg-bg-elevated border border-sphotel-border rounded-xl p-5 flex flex-col gap-1">
      <div className="flex items-center justify-between mb-3 gap-2">
        <h2 className="text-sm font-semibold text-text-primary">Top Items Today</h2>
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
      {filtered.map((item, i) => (
        <div key={i} className="flex items-center gap-3 py-1">
          <span className="text-sm text-text-secondary w-40 truncate shrink-0">{item.name}</span>
          <div className="flex-1 bg-bg-base rounded-full h-2 overflow-hidden">
            <div className="h-full rounded-full bg-sphotel-accent transition-all" style={{ width: `${Math.round((item.qty / max) * 100)}%` }} />
          </div>
          <span className="text-xs text-text-muted w-10 text-right shrink-0">×{item.qty}</span>
        </div>
      ))}
      {filtered.length === 0 && <p className="text-xs text-text-muted py-2 text-center">No items match.</p>}
      {showTg && (
        <TelegramScheduleModal current={config?.telegram_schedule ?? null}
          onSave={(cron) => onUpdateConfig?.(cron)} onClose={() => setShowTg(false)} />
      )}
    </div>
  )
}
