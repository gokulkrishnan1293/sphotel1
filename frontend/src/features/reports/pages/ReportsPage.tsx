import { useState } from 'react'
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query'
import { analyticsApi } from '../api/analytics'
import { fixedReportConfigsApi } from '../api/fixedReportConfigs'
import { KpiCards } from '../components/KpiCards'
import { TopItemsCard } from '../components/TopItemsCard'
import { PaymentCard } from '../components/PaymentCard'
import { WaiterCard } from '../components/WaiterCard'
import { CustomReportsSection } from '../components/CustomReportsSection'

function today() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function fmtDate(d: string) {
  return new Date(d + 'T00:00:00').toLocaleDateString('en-IN', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  })
}

export function ReportsPage() {
  const qc = useQueryClient()
  const [date, setDate] = useState(today)
  const summary = useQuery({ queryKey: ['analytics', 'summary', date], queryFn: () => analyticsApi.summary(date) })
  const waiter = useQuery({ queryKey: ['analytics', 'waiter'], queryFn: () => analyticsApi.waiterPerformance() })
  const configs = useQuery({ queryKey: ['fixed-report-configs'], queryFn: fixedReportConfigsApi.list })
  const updateConfig = useMutation({
    mutationFn: ({ type, cron }: { type: string; cron: string | null }) =>
      fixedReportConfigsApi.update(type, { telegram_schedule: cron, is_visible: true }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['fixed-report-configs'] }),
  })

  const cfg = (type: string) => configs.data?.find((c) => c.report_type === type)
  const onCfg = (type: string) => (cron: string | null) => updateConfig.mutate({ type, cron })
  const s = summary.data

  return (
    <div className="flex flex-col h-full overflow-auto bg-bg-base">
      <header className="sticky top-0 z-10 bg-bg-surface border-b border-sphotel-border px-6 py-4 shrink-0">
        <h1 className="text-lg font-semibold text-text-primary">Reports</h1>
        <div className="flex items-center gap-3 mt-2">
          <span className="text-xs text-text-muted">{fmtDate(date)}</span>
          <input type="date" value={date} max={today()} onChange={(e) => setDate(e.target.value)}
            className="ml-auto text-sm bg-bg-elevated border border-sphotel-border rounded-lg px-3 py-1.5 text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent" />
        </div>
      </header>

      <div className="p-6 flex flex-col gap-4">
        {summary.isFetching && <p className="text-sm text-text-muted">Loading…</p>}
        {summary.isError && (
          <div className="bg-bg-elevated border border-status-error/30 rounded-xl p-5 flex items-center justify-between gap-4">
            <p className="text-sm text-status-error">Failed to load analytics. Check that you are logged in as admin.</p>
            <button onClick={() => qc.invalidateQueries({ queryKey: ['analytics'] })}
              className="text-xs text-sphotel-accent border border-sphotel-accent/30 rounded-lg px-3 py-1.5 hover:opacity-80 shrink-0">Retry</button>
          </div>
        )}
        {s && (
          <>
            <KpiCards data={s} />
            <div className="grid grid-cols-2 gap-4">
              <TopItemsCard items={s.top_items} config={cfg('top_items')} onUpdateConfig={onCfg('top_items')} />
              <WaiterCard data={waiter.data} config={cfg('waiter_performance')} onUpdateConfig={onCfg('waiter_performance')} />
            </div>
            <PaymentCard breakdown={s.payment_breakdown} config={cfg('payment_breakdown')} onUpdateConfig={onCfg('payment_breakdown')} />
            {s.bill_count === 0 && <p className="text-xs text-text-muted text-center py-4">No billed bills found for {date}.</p>}
            <CustomReportsSection />
          </>
        )}
      </div>
    </div>
  )
}
