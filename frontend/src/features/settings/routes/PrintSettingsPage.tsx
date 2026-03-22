import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Save } from 'lucide-react'
import { TenantBadge } from '@/shared/components/layout/TenantBadge'
import { PrintAgentCard } from '../components/PrintAgentCard'
import { PrintTemplateForm } from '../components/PrintTemplateForm'
import { printApi, PrintTemplateConfig } from '../api/printSettings'

export function PrintSettingsPage() {
  const qc = useQueryClient()
  const { data: template, isLoading, isError } = useQuery({ queryKey: ['print-template'], queryFn: printApi.getTemplate })
  const updateMutation = useMutation({ mutationFn: printApi.updateTemplate, onSuccess: (data) => { qc.setQueryData(['print-template'], data) } })
  const [formData, setFormData] = useState<PrintTemplateConfig | null>(null)

  useEffect(() => { if (template && !formData) setFormData(template) }, [template, formData])

  if (isError) return <div className="p-6 text-sm text-red-500">Failed to load print settings.</div>
  if (isLoading || !formData) return <div className="p-6 text-sm text-text-muted">Loading print settings...</div>

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target as HTMLInputElement
    let parsed: unknown = value
    if (type === 'checkbox') parsed = (e.target as HTMLInputElement).checked
    else if (type === 'number' || name.endsWith('_width') || name.endsWith('_size') || name.endsWith('_padding')) parsed = parseInt(value, 10) || 0
    setFormData((prev) => prev ? { ...prev, [name]: parsed } : null)
  }

  return (
    <div className="flex flex-col h-full">
      <header className="px-6 py-4 border-b border-sphotel-border bg-bg-surface shrink-0 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold text-text-primary">Print Settings</h1>
          <TenantBadge />
        </div>
        <button onClick={() => updateMutation.mutate(formData)} disabled={updateMutation.isPending}
          className="flex items-center gap-2 bg-sphotel-accent text-bg-base px-4 py-2 rounded-lg text-sm font-medium hover:opacity-90 disabled:opacity-50">
          <Save size={15} />{updateMutation.isPending ? 'Saving...' : 'Save Changes'}
        </button>
      </header>

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-6xl mx-auto flex flex-col gap-6">
          <PrintAgentCard />
          <PrintTemplateForm formData={formData} onChange={handleChange} />
        </div>
      </div>
    </div>
  )
}
