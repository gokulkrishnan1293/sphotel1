import { useState } from 'react'
import { X } from 'lucide-react'
import { DIMENSIONS, REPORT_METRICS, CHART_TYPES, type CustomReport, type ReportBody } from '../api/customReports'
import { describeCron } from '../utils/cronUtils'

const SEL = 'bg-bg-base border border-sphotel-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent w-full'
const INP = 'bg-bg-base border border-sphotel-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent w-full'
const PERIOD_PRESETS = [{ label: 'Today', days: 1 }, { label: 'Week', days: 7 }, { label: 'Month', days: 30 }]

interface Props { initial?: CustomReport; onSave: (body: ReportBody) => void; onClose: () => void; isPending: boolean }

export function ReportBuilderModal({ initial, onSave, onClose, isPending }: Props) {
  const [name, setName] = useState(initial?.name ?? '')
  const [dimension, setDimension] = useState(initial?.dimension ?? 'waiter')
  const [metric, setMetric] = useState(initial?.metric ?? 'revenue')
  const [days, setDays] = useState(initial?.days ?? 7)
  const [chartType, setChartType] = useState(initial?.chart_type ?? 'bar')
  const [cron, setCron] = useState(initial?.telegram_schedule ?? '')
  const isCustom = ![1, 7, 30].includes(days)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-bg-elevated border border-sphotel-border rounded-2xl w-full max-w-md p-6 flex flex-col gap-4 shadow-2xl">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-text-primary">{initial ? 'Edit Report' : 'New Custom Report'}</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary"><X size={18} /></button>
        </div>
        <div className="flex flex-col gap-3 overflow-y-auto max-h-[60vh] pr-0.5">
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-text-secondary">Report Name</label>
            <input className={INP} placeholder="e.g. Weekly Top Waiters" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-text-secondary">Dimension (Group By)</label>
            <select className={SEL} value={dimension} onChange={(e) => setDimension(e.target.value)}>
              {DIMENSIONS.map((d) => <option key={d.value} value={d.value}>{d.label}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-text-secondary">Metric</label>
            <select className={SEL} value={metric} onChange={(e) => setMetric(e.target.value)}>
              {REPORT_METRICS.map((m) => <option key={m.value} value={m.value}>{m.label}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-text-secondary">Period</label>
            <div className="flex gap-2">
              {PERIOD_PRESETS.map((p) => (
                <button key={p.days} onClick={() => setDays(p.days)}
                  className={`flex-1 py-1.5 text-xs rounded-lg border transition-colors ${days === p.days ? 'border-sphotel-accent text-sphotel-accent' : 'border-sphotel-border text-text-secondary hover:border-sphotel-accent/50'}`}>
                  {p.label}
                </button>
              ))}
              <button onClick={() => { if (!isCustom) setDays(14) }}
                className={`flex-1 py-1.5 text-xs rounded-lg border transition-colors ${isCustom ? 'border-sphotel-accent text-sphotel-accent' : 'border-sphotel-border text-text-secondary hover:border-sphotel-accent/50'}`}>
                Custom
              </button>
            </div>
            {isCustom && (
              <input type="number" min={1} max={365} value={days}
                onChange={(e) => setDays(Math.max(1, parseInt(e.target.value) || 1))}
                placeholder="Days (e.g. 45)" className={INP + ' mt-1'} />
            )}
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-text-secondary">Chart Type</label>
            <select className={SEL} value={chartType} onChange={(e) => setChartType(e.target.value)}>
              {CHART_TYPES.map((c) => <option key={c} value={c} className="capitalize">{c}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-text-secondary">Telegram Schedule (cron)</label>
            <input value={cron} onChange={(e) => setCron(e.target.value)} placeholder="e.g. 0 9 * * 1"
              className={INP + ' font-mono'} />
            {cron && <p className="text-xs text-sphotel-accent mt-0.5">{describeCron(cron)}</p>}
          </div>
        </div>
        <div className="flex gap-2 pt-1">
          <button onClick={onClose} className="flex-1 border border-sphotel-border rounded-lg py-2 text-sm text-text-secondary hover:bg-bg-base">Cancel</button>
          <button onClick={() => { if (name.trim()) onSave({ name: name.trim(), metric, chart_type: chartType, telegram_schedule: cron || null, dimension, days }) }}
            disabled={isPending || !name.trim()}
            className="flex-1 bg-sphotel-accent text-sphotel-accent-fg rounded-lg py-2 text-sm font-medium disabled:opacity-50">
            {isPending ? 'Saving…' : 'Save Report'}
          </button>
        </div>
      </div>
    </div>
  )
}
