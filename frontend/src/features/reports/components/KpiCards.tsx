import type { DailySummary } from '../types'

const fmt = (p: number) => `₹${(p / 100).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`

function KpiCard({ label, value, sub, danger }: { label: string; value: string; sub?: string; danger?: boolean }) {
  return (
    <div className="bg-bg-elevated border border-sphotel-border rounded-xl p-5 flex flex-col gap-2">
      <span className="text-xs uppercase tracking-wider text-text-muted font-medium">{label}</span>
      <span className={`text-3xl font-bold ${danger ? 'text-status-error' : 'text-text-primary'}`}>{value}</span>
      {sub && <span className="text-xs text-text-muted">{sub}</span>}
    </div>
  )
}

export function KpiCards({ data }: { data: DailySummary }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
      <KpiCard label="Today's Revenue" value={fmt(data.total_paise)} />
      <KpiCard label="Bills Closed" value={String(data.bill_count)} />
      <KpiCard label="Avg Bill Value" value={fmt(data.avg_paise)} />
    </div>
  )
}
