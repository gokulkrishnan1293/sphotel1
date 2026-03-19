import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Copy, Check } from 'lucide-react'
import { QrCode } from '@/shared/components/QrCode'
import { tenantsApi } from '../api/tenants'
import type { AdminCreatedResponse, CreateAdminRequest } from '../types/staff'

interface Props {
  onSubmit: (data: CreateAdminRequest) => void
  onCancel: () => void
  isPending: boolean
  result: AdminCreatedResponse | null
}

const INPUT = 'border border-sphotel-border bg-bg-elevated rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent w-full'

export function CreateAdminPanel({ onSubmit, onCancel, isPending, result }: Props) {
  const [tenantSlug, setTenantSlug] = useState('')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [copied, setCopied] = useState(false)

  const { data: tenants = [] } = useQuery({ queryKey: ['tenants'], queryFn: tenantsApi.list })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!tenantSlug || !name.trim() || !email.trim() || password.length < 8) return
    onSubmit({ tenant_slug: tenantSlug, name: name.trim(), email: email.trim(), password })
  }

  function copyUri() {
    if (!result) return
    navigator.clipboard.writeText(result.totp_uri)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-bg-surface rounded-xl shadow-xl w-full max-w-md flex flex-col gap-5 p-6">
        <h2 className="text-base font-semibold text-text-primary">
          {result ? 'Admin Created' : 'Create Admin Account'}
        </h2>

        {!result ? (
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium">Tenant</label>
              <select className={INPUT} value={tenantSlug} onChange={(e) => setTenantSlug(e.target.value)} required>
                <option value="">Select tenant…</option>
                {tenants.map((t) => (
                  <option key={t.slug} value={t.slug}>{t.name}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium">Name</label>
              <input className={INPUT} value={name} onChange={(e) => setName(e.target.value)} autoFocus required />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium">Email</label>
              <input type="email" className={INPUT} value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium">Password</label>
              <input type="password" className={INPUT} value={password} onChange={(e) => setPassword(e.target.value)}
                placeholder="Min 8 characters" required minLength={8} />
            </div>
            <div className="flex gap-2 pt-1">
              <button type="submit" disabled={isPending}
                className="flex-1 bg-sphotel-accent text-sphotel-accent-fg rounded-lg py-2 text-sm font-medium disabled:opacity-50">
                {isPending ? 'Creating…' : 'Create Admin'}
              </button>
              <button type="button" onClick={onCancel}
                className="flex-1 border border-sphotel-border rounded-lg py-2 text-sm text-text-secondary">
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <div className="flex flex-col gap-4">
            <p className="text-sm text-text-secondary">
              <span className="font-medium text-text-primary">{result.name}</span> created.
              Ask them to scan this QR code with Google Authenticator or Authy.
            </p>
            <div className="flex justify-center bg-white rounded-xl p-4">
              <QrCode value={result.totp_uri} size={180} />
            </div>
            <button onClick={copyUri}
              className="flex items-center justify-center gap-1.5 text-xs text-sphotel-accent border border-sphotel-border rounded-lg py-2">
              {copied ? <Check size={12} /> : <Copy size={12} />}
              {copied ? 'Copied!' : 'Copy setup URI instead'}
            </button>
            <p className="text-xs text-status-warning text-center">⚠ Save this now — it cannot be retrieved again.</p>
            <button onClick={onCancel}
              className="w-full bg-sphotel-accent text-sphotel-accent-fg rounded-lg py-2 text-sm font-medium">
              Done
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
