import type { HeatmapCell } from '../types'

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const HOURS = Array.from({ length: 24 }, (_, i) => i)

export function HourlyHeatmap({ data }: { data: HeatmapCell[] }) {
  const map = new Map(data.map((c) => [`${c.dow}-${c.hour}`, c.total_paise]))
  const max = Math.max(...data.map((c) => c.total_paise), 1)

  return (
    <div className="overflow-x-auto">
      <div className="min-w-[640px]">
        {/* Hour labels */}
        <div className="flex ml-10 mb-1">
          {HOURS.map((h) => (
            <div key={h} className="flex-1 text-center text-[10px] text-text-muted">
              {h % 3 === 0 ? `${h}h` : ''}
            </div>
          ))}
        </div>

        {DAYS.map((day, dow) => (
          <div key={dow} className="flex items-center gap-1 mb-1">
            <span className="w-9 text-xs text-text-muted text-right shrink-0">{day}</span>
            <div className="flex flex-1 gap-[2px]">
              {HOURS.map((h) => {
                const val = map.get(`${dow}-${h}`) ?? 0
                const intensity = val / max
                return (
                  <div
                    key={h}
                    title={val ? `₹${(val / 100).toFixed(0)}` : ''}
                    className="flex-1 h-6 rounded-sm transition-colors"
                    style={{
                      backgroundColor: val
                        ? `rgba(16, 185, 129, ${0.1 + intensity * 0.9})`
                        : 'var(--color-bg-elevated)',
                      border: '1px solid var(--color-sphotel-border)',
                    }}
                  />
                )
              })}
            </div>
          </div>
        ))}

        <div className="flex items-center gap-2 mt-3 ml-10">
          <span className="text-xs text-text-muted">Low</span>
          {[0.1, 0.3, 0.5, 0.7, 0.9].map((v) => (
            <div key={v} className="w-5 h-3 rounded-sm" style={{ backgroundColor: `rgba(16,185,129,${v})` }} />
          ))}
          <span className="text-xs text-text-muted">High</span>
        </div>
      </div>
    </div>
  )
}
