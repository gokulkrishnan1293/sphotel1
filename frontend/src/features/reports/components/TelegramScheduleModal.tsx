import { useState } from 'react'
import { X, Send } from 'lucide-react'
import { describeCron } from '../utils/cronUtils'

const PRESETS = [
  { label: 'Daily 9 AM', value: '0 9 * * *' },
  { label: 'Daily EOD', value: '0 23 * * *' },
  { label: 'Mon 9 AM', value: '0 9 * * 1' },
  { label: 'Monthly 1st', value: '0 9 1 * *' },
]

interface Props {
  current: string | null
  onSave: (cron: string | null) => void
  onClose: () => void
}

export function TelegramScheduleModal({ current, onSave, onClose }: Props) {
  const [cron, setCron] = useState(current ?? '')
  const desc = describeCron(cron)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-bg-elevated border border-sphotel-border rounded-2xl w-full max-w-sm p-6 flex flex-col gap-4 shadow-2xl">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-text-primary flex items-center gap-2">
            <Send size={14} /> Telegram Schedule
          </h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary"><X size={16} /></button>
        </div>
        <div className="flex flex-wrap gap-1.5">
          <button onClick={() => setCron('')}
            className={`text-xs px-2.5 py-1 rounded-full border ${!cron ? 'border-sphotel-accent text-sphotel-accent' : 'border-sphotel-border text-text-muted hover:border-sphotel-accent/50'}`}>
            None
          </button>
          {PRESETS.map((p) => (
            <button key={p.value} onClick={() => setCron(p.value)}
              className={`text-xs px-2.5 py-1 rounded-full border ${cron === p.value ? 'border-sphotel-accent text-sphotel-accent' : 'border-sphotel-border text-text-muted hover:border-sphotel-accent/50'}`}>
              {p.label}
            </button>
          ))}
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-text-secondary">Custom cron expression</label>
          <input value={cron} onChange={(e) => setCron(e.target.value)} placeholder="e.g. 0 9 * * 1"
            className="bg-bg-base border border-sphotel-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent font-mono" />
          {desc && <p className="text-xs text-sphotel-accent mt-0.5">{desc}</p>}
        </div>
        <div className="flex gap-2">
          <button onClick={onClose} className="flex-1 border border-sphotel-border rounded-lg py-2 text-sm text-text-secondary hover:bg-bg-base">Cancel</button>
          <button onClick={() => { onSave(cron || null); onClose() }}
            className="flex-1 bg-sphotel-accent text-sphotel-accent-fg rounded-lg py-2 text-sm font-medium">Save</button>
        </div>
      </div>
    </div>
  )
}
