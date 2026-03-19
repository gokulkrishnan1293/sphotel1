import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { X, Check, Trash2 } from 'lucide-react'
import { tenantsApi, type TenantSummary, type FeatureFlags } from '../api/tenants'
import { Switch } from '@/shared/components/ui/switch'

const INPUT = 'bg-bg-elevated border border-sphotel-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent w-full'
const FLAG_LABELS: Record<keyof FeatureFlags, string> = {
  waiterMode: 'Waiter Mode', suggestionEngine: 'Suggestion Engine', telegramAlerts: 'Telegram Alerts',
  gstModule: 'GST Module', payrollRewards: 'Payroll & Rewards',
  discountComplimentary: 'Discount / Complimentary', waiterTransfer: 'Waiter Transfer', billCloseUx: 'Bill Close Feedback',
}
const IMPLEMENTED_FLAGS = new Set<keyof FeatureFlags>(['telegramAlerts', 'billCloseUx'])

interface Props { tenant: TenantSummary; onClose: () => void; onDeleted: () => void }

export function EditTenantPanel({ tenant, onClose, onDeleted }: Props) {
  const qc = useQueryClient()
  const [name, setName] = useState(tenant.name)
  const [isActive, setIsActive] = useState(tenant.is_active)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [error, setError] = useState('')
  const { data: flags } = useQuery({ queryKey: ['tenant-features', tenant.slug], queryFn: () => tenantsApi.getFeatures(tenant.slug) })
  const inv = () => qc.invalidateQueries({ queryKey: ['tenants'] })
  const updateMutation = useMutation({
    mutationFn: (body: { name?: string; is_active?: boolean }) => tenantsApi.update(tenant.slug, body),
    onSuccess: (u) => { inv(); if (u.is_active !== undefined) setIsActive(u.is_active) },
    onError: (err: Error) => setError(err.message),
  })
  const flagMutation = useMutation({
    mutationFn: (body: Partial<FeatureFlags>) => tenantsApi.updateFeatures(tenant.slug, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tenant-features', tenant.slug] }),
  })
  const deleteMutation = useMutation({
    mutationFn: () => tenantsApi.delete(tenant.slug),
    onSuccess: () => { inv(); onDeleted() },
    onError: (err: Error) => setError(err.message),
  })

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-text-primary">{tenant.name}</h2>
        <button onClick={onClose} className="text-text-muted hover:text-text-primary"><X size={18} /></button>
      </div>
      <section className="flex flex-col gap-3">
        <p className="text-xs font-medium text-text-muted uppercase tracking-wide">Info</p>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-text-secondary">Name</label>
          <div className="flex gap-2">
            <input className={INPUT} value={name} onChange={(e) => setName(e.target.value)} />
            <button onClick={() => { setError(''); updateMutation.mutate({ name }) }}
              disabled={updateMutation.isPending || name === tenant.name || !name.trim()}
              className="bg-sphotel-accent text-sphotel-accent-fg rounded-lg px-3 text-sm font-medium disabled:opacity-50">
              <Check size={16} />
            </button>
          </div>
        </div>
        <p className="text-xs text-text-muted">Slug: <span className="font-mono">{tenant.slug}</span></p>
        <div className="flex items-center justify-between">
          <span className="text-sm text-text-secondary">Active</span>
          <Switch checked={isActive} onCheckedChange={(v) => { setIsActive(v); updateMutation.mutate({ is_active: v }) }} disabled={updateMutation.isPending} />
        </div>
        {error && <p className="text-status-error text-xs">{error}</p>}
      </section>
      <section className="flex flex-col gap-3">
        <p className="text-xs font-medium text-text-muted uppercase tracking-wide">Feature Flags</p>
        {flags ? Object.entries(FLAG_LABELS).map(([key, label]) => {
          const live = IMPLEMENTED_FLAGS.has(key as keyof FeatureFlags)
          return (
            <div key={key} className={`flex items-center justify-between ${live ? '' : 'opacity-40'}`}>
              <span className={`text-sm text-text-secondary ${live ? '' : 'line-through'}`}>{label}</span>
              <Switch checked={flags[key as keyof FeatureFlags]} onCheckedChange={(v) => flagMutation.mutate({ [key]: v })} disabled={flagMutation.isPending || !live} />
            </div>
          )
        }) : <p className="text-xs text-text-muted">Loading…</p>}
      </section>
      <section className="border-t border-sphotel-border pt-4">
        {confirmDelete ? (
          <div className="flex flex-col gap-2">
            <p className="text-sm text-status-error">This will permanently delete the tenant and all data. Are you sure?</p>
            <div className="flex gap-2">
              <button onClick={() => deleteMutation.mutate()} disabled={deleteMutation.isPending} className="flex-1 bg-status-error text-white rounded-lg py-2 text-sm font-medium disabled:opacity-50">{deleteMutation.isPending ? 'Deleting…' : 'Yes, delete'}</button>
              <button onClick={() => setConfirmDelete(false)} className="flex-1 border border-sphotel-border rounded-lg py-2 text-sm text-text-secondary">Cancel</button>
            </div>
          </div>
        ) : (
          <button onClick={() => setConfirmDelete(true)} className="flex items-center gap-2 text-sm text-status-error hover:opacity-80">
            <Trash2 size={15} /> Delete tenant
          </button>
        )}
      </section>
    </div>
  )
}
