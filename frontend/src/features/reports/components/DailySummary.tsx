import type { DailySummary } from '../types'

const fmt = (p: number) => `₹${(p / 100).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`
const CARD = 'bg-bg-elevated border border-sphotel-border rounded-xl p-4 flex flex-col gap-1'

export function DailySummaryCards({ data }: { data: DailySummary }) {
  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div className={CARD}>
          <span className="text-xs text-text-muted">Revenue</span>
          <span className="text-xl font-bold text-text-primary">{fmt(data.total_paise)}</span>
        </div>
        <div className={CARD}>
          <span className="text-xs text-text-muted">Bills</span>
          <span className="text-xl font-bold text-text-primary">{data.bill_count}</span>
        </div>
        <div className={CARD}>
          <span className="text-xs text-text-muted">Avg Bill</span>
          <span className="text-xl font-bold text-text-primary">{fmt(data.avg_paise)}</span>
        </div>
        <div className={CARD}>
          <span className="text-xs text-text-muted">Voids</span>
          <span className="text-xl font-bold text-status-error">{data.void_count}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {Object.keys(data.payment_breakdown).length > 0 && (
          <div className={CARD}>
            <span className="text-xs font-medium text-text-secondary mb-2">Payment Breakdown</span>
            {Object.entries(data.payment_breakdown).map(([method, amt]) => (
              <div key={method} className="flex justify-between text-sm">
                <span className="text-text-secondary capitalize">{method}</span>
                <span className="font-medium text-text-primary">{fmt(amt)}</span>
              </div>
            ))}
          </div>
        )}
        {data.top_items.length > 0 && (
          <div className={CARD}>
            <span className="text-xs font-medium text-text-secondary mb-2">Top Items</span>
            {data.top_items.map((item, i) => (
              <div key={i} className="flex justify-between text-sm">
                <span className="text-text-secondary truncate">{item.name}</span>
                <span className="font-medium text-text-primary ml-2">×{item.qty}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
