import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { customReportsApi, type CustomReport, type ReportBody } from '../api/customReports'
import { ReportBuilderModal } from './ReportBuilderModal'
import { CustomReportCard } from './CustomReportCard'

export function CustomReportsSection() {
  const qc = useQueryClient()
  const [editing, setEditing] = useState<CustomReport | null | 'new'>(null)
  const { data: reports = [] } = useQuery({ queryKey: ['custom-reports'], queryFn: customReportsApi.list })
  const create = useMutation({ mutationFn: customReportsApi.create, onSuccess: () => { qc.invalidateQueries({ queryKey: ['custom-reports'] }); setEditing(null) } })
  const update = useMutation({ mutationFn: ({ id, body }: { id: string; body: ReportBody }) => customReportsApi.update(id, body), onSuccess: () => { qc.invalidateQueries({ queryKey: ['custom-reports'] }); setEditing(null) } })
  const remove = useMutation({ mutationFn: customReportsApi.remove, onSuccess: () => qc.invalidateQueries({ queryKey: ['custom-reports'] }) })

  function handleSave(body: ReportBody) {
    if (editing === 'new') { create.mutate(body) }
    else if (editing) { update.mutate({ id: editing.id, body }) }
  }

  return (
    <>
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-text-primary">Custom Reports</h2>
          <button onClick={() => setEditing('new')}
            className="flex items-center gap-1.5 text-xs text-sphotel-accent hover:opacity-80 border border-sphotel-accent/30 rounded-lg px-2.5 py-1.5">
            <Plus size={12} /> Add Report
          </button>
        </div>
        <div className="grid grid-cols-3 gap-3">
          {reports.map((r) => (
            <CustomReportCard key={r.id} report={r} onEdit={() => setEditing(r)} onDelete={() => remove.mutate(r.id)} />
          ))}
          {reports.length === 0 && (
            <button onClick={() => setEditing('new')}
              className="col-span-3 border-2 border-dashed border-sphotel-border rounded-xl p-8 flex flex-col items-center gap-2 text-text-muted hover:border-sphotel-accent hover:text-sphotel-accent transition-colors">
              <Plus size={20} />
              <span className="text-sm">Add your first custom report</span>
              <span className="text-xs">Choose dimension, metric, period, and Telegram schedule</span>
            </button>
          )}
        </div>
      </div>

      {editing && (
        <ReportBuilderModal
          initial={editing === 'new' ? undefined : editing}
          onSave={handleSave}
          onClose={() => setEditing(null)}
          isPending={create.isPending || update.isPending}
        />
      )}
    </>
  )
}
