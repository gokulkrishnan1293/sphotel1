import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import { ShieldCheck, Users } from 'lucide-react'
import { authApi, type TenantPublicInfo } from '../api/auth'

export function TenantRolePage() {
  const { code } = useParams<{ code: string }>()
  const navigate = useNavigate()
  const [tenant, setTenant] = useState<TenantPublicInfo | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!code) return
    authApi.tenantInfo(code).then(setTenant).catch(() => {
      setError('Invalid tenant code.')
    })
  }, [code])

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg-base">
        <div className="text-center">
          <p className="text-status-error text-sm mb-4">{error}</p>
          <a href="/t" className="text-sphotel-accent text-sm underline">Go back</a>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-base">
      <div className="w-full max-w-sm bg-bg-surface rounded-xl shadow-lg p-8 flex flex-col gap-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">
            {tenant?.name ?? '…'}
          </h1>
          <p className="text-sm text-text-muted mt-1">Who are you signing in as?</p>
        </div>
        <div className="flex flex-col gap-3">
          <button
            onClick={() => navigate(`/t/${code}/admin`)}
            className="flex items-center gap-3 w-full border border-sphotel-border rounded-lg px-4 py-3 text-left hover:bg-bg-elevated transition-colors"
          >
            <ShieldCheck size={20} className="text-sphotel-accent shrink-0" />
            <div>
              <p className="text-sm font-medium text-text-primary">Admin</p>
              <p className="text-xs text-text-muted">Manage menu, staff & reports</p>
            </div>
          </button>
          <button
            onClick={() => navigate(`/t/${code}/staff`)}
            className="flex items-center gap-3 w-full border border-sphotel-border rounded-lg px-4 py-3 text-left hover:bg-bg-elevated transition-colors"
          >
            <Users size={20} className="text-sphotel-accent shrink-0" />
            <div>
              <p className="text-sm font-medium text-text-primary">Staff</p>
              <p className="text-xs text-text-muted">Billers, waiters, kitchen & managers</p>
            </div>
          </button>
        </div>
        <p className="text-center text-xs text-text-muted">
          Wrong restaurant?{' '}
          <a href="/t" className="underline">Change code</a>
        </p>
      </div>
    </div>
  )
}
