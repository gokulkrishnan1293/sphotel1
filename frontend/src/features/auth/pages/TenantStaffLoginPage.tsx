import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router'
import { authApi, type StaffPublicItem } from '../api/auth'
import { useAuthStore } from '../stores/authStore'

const STAFF_ROLES = ['waiter', 'kitchen_staff', 'manager', 'biller']

const ROLE_LABEL: Record<string, string> = {
  waiter: 'Waiter',
  kitchen_staff: 'Kitchen',
  manager: 'Manager',
  biller: 'Biller',
}

const ROLE_REDIRECT: Record<string, string> = {
  kitchen_staff: '/kitchen',
  manager: '/admin/menu',
  waiter: '/billing',
  biller: '/billing',
}

export function TenantStaffLoginPage() {
  const { code } = useParams<{ code: string }>()
  const navigate = useNavigate()
  const setCurrentUser = useAuthStore((s) => s.setCurrentUser)
  const setLoginTenantSlug = useAuthStore((s) => s.setLoginTenantSlug)

  const [selected, setSelected] = useState<StaffPublicItem | null>(null)
  const [pin, setPin] = useState('')
  const [rememberMe, setRememberMe] = useState(false)
  const [error, setError] = useState('')

  const { data: staff, isLoading } = useQuery({
    queryKey: ['tenant-staff-all', code],
    queryFn: () => authApi.tenantStaff(code!).then((s) => s.filter((u) => STAFF_ROLES.includes(u.role))),
    enabled: !!code,
  })

  const loginMutation = useMutation({
    mutationFn: async () => {
      await authApi.pinLogin({ user_id: selected!.id, pin, tenant_slug: code!, remember_me: rememberMe })
      return authApi.me()
    },
    onSuccess: (user) => {
      setCurrentUser(user)
      setLoginTenantSlug(code ?? null)
      window.location.href = ROLE_REDIRECT[user.role] ?? '/billing'
    },
    onError: (err: Error) => {
      setError(err.message || 'Invalid PIN. Try again.')
      setPin('')
    },
  })

  function handlePinSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (!selected || pin.length < 4) return
    loginMutation.mutate()
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-base">
      <div className="w-full max-w-sm bg-bg-surface rounded-xl shadow-lg p-8 flex flex-col gap-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Staff Login</h1>
          <p className="text-sm text-text-muted mt-1">{code}</p>
        </div>

        {!selected ? (
          <div className="flex flex-col gap-2">
            <p className="text-sm font-medium text-text-secondary">Select your name</p>
            {isLoading && <p className="text-sm text-text-muted text-center py-4">Loading…</p>}
            {staff?.map((u) => (
              <button key={u.id} onClick={() => setSelected(u)}
                className="w-full text-left border border-sphotel-border rounded-lg px-4 py-3 flex items-center justify-between hover:bg-bg-elevated transition-colors">
                <span className="text-sm font-medium text-text-primary">{u.name}</span>
                <span className="text-xs text-text-muted">{ROLE_LABEL[u.role] ?? u.role}</span>
              </button>
            ))}
            {staff?.length === 0 && <p className="text-sm text-text-muted text-center py-4">No staff found for this tenant.</p>}
            <button onClick={() => navigate(`/t/${code}`)} className="text-xs text-text-muted underline mt-2">Back</button>
          </div>
        ) : (
          <form onSubmit={handlePinSubmit} className="flex flex-col gap-4">
            <div className="text-center text-sm text-text-secondary">
              <p>Signing in as</p>
              <p className="font-medium text-text-primary">{selected.name}</p>
              <p className="text-xs text-text-muted">{ROLE_LABEL[selected.role] ?? selected.role}</p>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium">PIN</label>
              <input type="password" inputMode="numeric"
                className="border border-sphotel-border bg-bg-elevated rounded-lg px-3 py-2 text-sm text-center tracking-widest text-lg font-mono text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent"
                value={pin} onChange={(e) => setPin(e.target.value.replace(/\D/g, '').slice(0, 8))}
                placeholder="••••" autoFocus maxLength={8} />
            </div>
            <div className="flex items-center gap-2 mt-1">
              <input 
                type="checkbox" 
                id="remember" 
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 rounded border-sphotel-border text-sphotel-accent focus:ring-sphotel-accent"
              />
              <label htmlFor="remember" className="text-sm text-text-secondary cursor-pointer">
                Remember me on this device
              </label>
            </div>
            {error && <p className="text-status-error text-xs">{error}</p>}
            <button type="submit" disabled={loginMutation.isPending || pin.length < 4}
              className="bg-sphotel-accent text-white rounded-lg py-2 mt-2 text-sm font-medium disabled:opacity-50">
              {loginMutation.isPending ? 'Signing in…' : 'Sign in'}
            </button>
            <button type="button" onClick={() => { setSelected(null); setPin(''); setError('') }}
              className="text-xs text-text-muted underline">Back</button>
          </form>
        )}
      </div>
    </div>
  )
}
