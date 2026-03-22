import type { DailySummary, WaiterPerf } from '../types'

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

export function KpiCards({ data, waiterData }: { data: DailySummary; waiterData?: WaiterPerf[] }) {
  const noWaiter = waiterData?.find((w) => w.waiter_name === 'No Waiter')
  return (
    <div className={`grid gap-3 grid-cols-2 ${noWaiter ? 'sm:grid-cols-4' : 'sm:grid-cols-3'}`}>
      <KpiCard label="Today's Revenue" value={fmt(data.total_paise)} />
      <KpiCard label="Bills Closed" value={String(data.bill_count)} />
      <KpiCard label="Avg Bill Value" value={fmt(data.avg_paise)} />
      {noWaiter && (
        <KpiCard
          label="Online / Parcel"
          value={fmt(noWaiter.revenue_paise)}
          sub={`${noWaiter.bill_count} bill${noWaiter.bill_count !== 1 ? 's' : ''}`}
        />
      )}
    </div>
  )
}
