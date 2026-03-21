import { useState } from 'react'
import { Bell, FileText } from 'lucide-react'
import type { FixedReportConfig } from '../api/fixedReportConfigs'
import { TelegramScheduleModal } from './TelegramScheduleModal'
import { openPdfPreview } from '../utils/reportPreview'

const fmt = (p: number) => `₹${(p / 100).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`

interface Props {
  breakdown: Record<string, number>
  config?: FixedReportConfig | null
  onUpdateConfig?: (cron: string | null) => void
}

export function PaymentCard({ breakdown, config, onUpdateConfig }: Props) {
  const [showTg, setShowTg] = useState(false)
  const entries = Object.entries(breakdown)
  if (!entries.length) {
    return (
      <div className="bg-bg-elevated border border-sphotel-border rounded-xl p-5 flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-text-primary">Payment Breakdown</h2>
        <p className="text-xs text-text-muted py-4 text-center">No payment data today.</p>
      </div>
    )
  }
  const total = entries.reduce((s, [, v]) => s + v, 0)

  function preview() {
    const rows = entries.map(([m, a]) => ({
      label: m.charAt(0).toUpperCase() + m.slice(1),
      value: `${fmt(a)} (${total > 0 ? Math.round((a / total) * 100) : 0}%)`,
    }))
    rows.push({ label: 'Total', value: fmt(total) })
    openPdfPreview('Payment Breakdown', 'Today', [{ title: 'Payment Methods', rows }])
  }

  return (
    <div className="bg-bg-elevated border border-sphotel-border rounded-xl p-5 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-text-primary">Payment Breakdown</h2>
          <p className="text-xs text-text-muted">
            Total: <span className="font-semibold text-text-primary">{fmt(total)}</span>
          </p>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={preview} title="Preview PDF" className="p-1 text-text-muted hover:text-text-primary"><FileText size={13} /></button>
          <button onClick={() => setShowTg(true)} title="Telegram schedule"
            className={`p-1 rounded ${config?.telegram_schedule ? 'text-sphotel-accent' : 'text-text-muted hover:text-sphotel-accent'}`}>
            <Bell size={13} />
          </button>
        </div>
      </div>
      <div className="grid gap-3" style={{ gridTemplateColumns: `repeat(${entries.length}, 1fr)` }}>
        {entries.map(([method, amt]) => (
          <div key={method} className="bg-bg-base rounded-xl p-4 flex flex-col gap-1">
            <span className="text-xs text-text-muted capitalize tracking-wide">{method}</span>
            <span className="text-xl font-bold text-text-primary">{fmt(amt)}</span>
            <span className="text-xs text-text-muted">{total > 0 ? Math.round((amt / total) * 100) : 0}%</span>
          </div>
        ))}
      </div>
      {showTg && (
        <TelegramScheduleModal current={config?.telegram_schedule ?? null}
          onSave={(cron) => onUpdateConfig?.(cron)} onClose={() => setShowTg(false)} />
      )}
    </div>
  )
}
