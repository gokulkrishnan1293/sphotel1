import type { VelocityItem } from '../types'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

function Trend({ pct }: { pct: number | null }) {
  if (pct === null) return <span className="text-text-muted text-xs">new</span>
  if (pct > 0) return <span className="flex items-center gap-0.5 text-emerald-500 text-xs font-medium"><TrendingUp size={12} />+{pct}%</span>
  if (pct < 0) return <span className="flex items-center gap-0.5 text-status-error text-xs font-medium"><TrendingDown size={12} />{pct}%</span>
  return <span className="flex items-center gap-0.5 text-text-muted text-xs"><Minus size={12} />0%</span>
}

export function ItemVelocity({ data }: { data: VelocityItem[] }) {
  if (!data.length) return <p className="text-sm text-text-muted text-center py-8">No data for this period.</p>
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-sphotel-border text-xs text-text-muted text-left">
            <th className="pb-2 font-medium">Item</th>
            <th className="pb-2 font-medium text-right">This Week</th>
            <th className="pb-2 font-medium text-right">Last Week</th>
            <th className="pb-2 font-medium text-right">Trend</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, i) => (
            <tr key={i} className="border-b border-sphotel-border/50 hover:bg-bg-elevated transition-colors">
              <td className="py-2.5 text-text-primary">{item.name}</td>
              <td className="py-2.5 text-right font-medium text-text-primary">{item.this_week}</td>
              <td className="py-2.5 text-right text-text-secondary">{item.last_week}</td>
              <td className="py-2.5 text-right"><Trend pct={item.change_pct} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
