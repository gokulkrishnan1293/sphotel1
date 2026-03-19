import type { CustomQueryRow } from '../types'

interface Props { data: CustomQueryRow[]; chartType: string }

function maxVal(data: CustomQueryRow[]) { return Math.max(...data.map((r) => r.value), 1) }

const COLORS = ['#6ee7b7', '#93c5fd', '#fca5a5', '#fde68a', '#c4b5fd', '#fdba74', '#a5f3fc']

function BarChart({ data }: { data: CustomQueryRow[] }) {
  const m = maxVal(data)
  return (
    <div className="flex flex-col gap-1">
      {data.map((r, i) => (
        <div key={i} className="flex items-center gap-2">
          <span className="text-xs text-text-secondary w-24 truncate shrink-0">{r.label}</span>
          <div className="flex-1 bg-bg-base rounded-full h-1.5 overflow-hidden">
            <div className="h-full rounded-full bg-sphotel-accent" style={{ width: `${Math.round((r.value / m) * 100)}%` }} />
          </div>
          <span className="text-xs text-text-muted w-14 text-right shrink-0">{r.value.toLocaleString()}</span>
        </div>
      ))}
    </div>
  )
}

function TableChart({ data }: { data: CustomQueryRow[] }) {
  return (
    <table className="w-full text-xs">
      <thead><tr className="text-text-muted border-b border-sphotel-border"><th className="text-left py-1">Label</th><th className="text-right py-1">Value</th></tr></thead>
      <tbody>
        {data.map((r, i) => (
          <tr key={i} className="border-b border-sphotel-border/50">
            <td className="py-0.5 text-text-secondary truncate max-w-[120px]">{r.label}</td>
            <td className="py-0.5 text-right text-text-primary">{r.value.toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function PieChart({ data }: { data: CustomQueryRow[] }) {
  const total = data.reduce((s, r) => s + r.value, 0) || 1
  let deg = 0
  const segments = data.map((r, i) => {
    const slice = (r.value / total) * 360
    const seg = { color: COLORS[i % COLORS.length], from: deg, to: deg + slice, label: r.label, pct: Math.round((r.value / total) * 100) }
    deg += slice
    return seg
  })
  const gradient = segments.map((s) => `${s.color} ${s.from}deg ${s.to}deg`).join(', ')
  return (
    <div className="flex items-center gap-4">
      <div className="w-20 h-20 rounded-full shrink-0" style={{ background: `conic-gradient(${gradient})` }} />
      <div className="flex flex-col gap-0.5 min-w-0">
        {segments.map((s, i) => (
          <div key={i} className="flex items-center gap-1.5 text-xs text-text-secondary">
            <span className="w-2 h-2 rounded-full shrink-0" style={{ background: s.color }} />
            <span className="truncate">{s.label}</span>
            <span className="text-text-muted ml-auto pl-1">{s.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function LineChart({ data }: { data: CustomQueryRow[] }) {
  const m = maxVal(data)
  const W = 200, H = 50
  const pts = data.map((r, i) => `${(i / Math.max(data.length - 1, 1)) * W},${H - (r.value / m) * H}`).join(' ')
  return (
    <div className="flex flex-col gap-1">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-12" preserveAspectRatio="none">
        <polyline points={pts} fill="none" strokeWidth="1.5" className="stroke-sphotel-accent" />
      </svg>
      <div className="flex justify-between text-xs text-text-muted">
        {data[0] && <span>{data[0].label}</span>}
        {data.length > 1 && <span>{data[data.length - 1].label}</span>}
      </div>
    </div>
  )
}

export function ReportChart({ data, chartType }: Props) {
  if (!data.length) return <p className="text-xs text-text-muted">No data for this period.</p>
  if (chartType === 'table') return <TableChart data={data} />
  if (chartType === 'pie') return <PieChart data={data} />
  if (chartType === 'line') return <LineChart data={data} />
  return <BarChart data={data} />
}
