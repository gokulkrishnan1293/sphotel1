import { useQuery } from '@tanstack/react-query'
import { Pencil, Trash2, Send, FileText } from 'lucide-react'
import { analyticsApi } from '../api/analytics'
import { REPORT_METRICS, DIMENSIONS, type CustomReport } from '../api/customReports'
import { ReportChart } from './ReportChart'
import { describeCron } from '../utils/cronUtils'
import { openPdfPreview } from '../utils/reportPreview'

interface Props { report: CustomReport; onEdit: () => void; onDelete: () => void }

function periodLabel(days: number) {
  if (days === 1) return 'Today'
  if (days === 7) return 'Last 7 days'
  if (days === 30) return 'Last 30 days'
  return `Last ${days} days`
}

export function CustomReportCard({ report, onEdit, onDelete }: Props) {
  const metricLabel = REPORT_METRICS.find((m) => m.value === report.metric)?.label ?? report.metric
  const dimLabel = DIMENSIONS.find((d) => d.value === report.dimension)?.label ?? report.dimension ?? '—'
  const { data = [], isFetching } = useQuery({
    queryKey: ['custom-report-data', report.id, report.dimension, report.metric, report.days],
    queryFn: () => analyticsApi.customQuery({ dimension: report.dimension!, metric: report.metric, days: report.days }),
    enabled: !!report.dimension,
    staleTime: 5 * 60 * 1000,
  })

  return (
    <div className="bg-bg-elevated border border-sphotel-border rounded-xl p-4 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-sm font-medium text-text-primary">{report.name}</p>
          <p className="text-xs text-text-muted">{dimLabel} · {metricLabel} · {periodLabel(report.days)}</p>
        </div>
        <div className="flex gap-1 shrink-0">
          <button onClick={() => data.length && openPdfPreview(report.name, periodLabel(report.days), [{ title: `${dimLabel} · ${metricLabel}`, rows: data.map((r) => ({ label: r.label, value: r.value.toLocaleString() })) }])}
            title="Preview PDF" className="p-1 text-text-muted hover:text-text-primary"><FileText size={13} /></button>
          <button onClick={onEdit} className="p-1 text-text-muted hover:text-text-primary" title="Edit"><Pencil size={13} /></button>
          <button onClick={onDelete} className="p-1 text-text-muted hover:text-status-error" title="Delete"><Trash2 size={13} /></button>
        </div>
      </div>
      {report.telegram_schedule && (
        <div className="flex items-center gap-1.5 text-xs text-sphotel-accent">
          <Send size={10} />
          <span className="font-mono">{report.telegram_schedule}</span>
          <span className="text-text-muted">· {describeCron(report.telegram_schedule)}</span>
        </div>
      )}
      <div className="overflow-auto max-h-48">
        {isFetching ? <p className="text-xs text-text-muted">Loading…</p> : <ReportChart data={data} chartType={report.chart_type} />}
      </div>
    </div>
  )
}
