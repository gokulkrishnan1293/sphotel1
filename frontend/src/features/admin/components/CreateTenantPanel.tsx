import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X } from 'lucide-react'
import { tenantsApi } from '../api/tenants'

const INPUT = 'bg-bg-elevated border border-sphotel-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent w-full'

export function CreateTenantPanel({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({ name: '', subdomain: '' })
  const [error, setError] = useState('')

  const createMutation = useMutation({
    mutationFn: () => tenantsApi.create(form),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['tenants'] }); onClose() },
    onError: (err: Error) => setError(err.message),
  })

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-text-primary">New Tenant</h2>
        <button onClick={onClose} className="text-text-muted hover:text-text-primary"><X size={18} /></button>
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-text-secondary">Name</label>
        <input className={INPUT} value={form.name}
          onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          placeholder="Spice Garden" autoFocus />
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-text-secondary">Subdomain</label>
        <input className={INPUT} value={form.subdomain}
          onChange={(e) => setForm((f) => ({ ...f, subdomain: e.target.value.toLowerCase() }))}
          placeholder="spice-garden" />
        <p className="text-xs text-text-muted">Lowercase letters, numbers, hyphens. 3–63 chars.</p>
      </div>
      {error && <p className="text-status-error text-xs">{error}</p>}
      <button
        onClick={() => { setError(''); createMutation.mutate() }}
        disabled={createMutation.isPending || !form.name || !form.subdomain}
        className="bg-sphotel-accent text-sphotel-accent-fg rounded-lg py-2 text-sm font-medium disabled:opacity-50">
        {createMutation.isPending ? 'Creating…' : 'Create Tenant'}
      </button>
      <p className="text-xs text-text-muted">You can add admins from the Staff menu after creation.</p>
    </div>
  )
}
