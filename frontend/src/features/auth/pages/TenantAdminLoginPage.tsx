import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router'
import { authApi } from '../api/auth'
import { useAuthStore } from '../stores/authStore'
import { applyTheme, type Theme } from '@/lib/theme'

export function TenantAdminLoginPage() {
  const { code } = useParams<{ code: string }>()
  const navigate = useNavigate()
  const setCurrentUser = useAuthStore((s) => s.setCurrentUser)
  const setLoginTenantSlug = useAuthStore((s) => s.setLoginTenantSlug)

  const [step, setStep] = useState<'credentials' | 'totp'>('credentials')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [totpCode, setTotpCode] = useState('')
  const [rememberMe, setRememberMe] = useState(false)
  const [error, setError] = useState('')

  const loginMutation = useMutation({
    mutationFn: async () => {
      await authApi.adminLogin({ email: email.trim(), password, totp_code: totpCode, tenant_slug: code, remember_me: rememberMe })
      return authApi.me()
    },
    onSuccess: (user) => {
      setCurrentUser(user)
      setLoginTenantSlug(code ?? null)
      const theme = user.preferences?.theme as Theme | undefined
      if (theme) applyTheme(theme)
      window.location.href = '/admin/menu'
    },
    onError: (err: Error) => {
      setError(err.message || 'Login failed. Check your credentials.')
      setTotpCode('')
    },
  })

  function handleCredentials(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (!email.trim() || !password) return
    setStep('totp')
  }

  function handleTotp(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (totpCode.length !== 6) { setError('Enter the 6-digit code from your authenticator app.'); return }
    loginMutation.mutate()
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-base">
      <div className="w-full max-w-sm bg-bg-surface rounded-xl shadow-lg p-8 flex flex-col gap-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Admin Login</h1>
          <p className="text-sm text-text-muted mt-1">{code}</p>
        </div>
        {step === 'credentials' && (
          <form onSubmit={handleCredentials} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium">Email</label>
              <input type="email" className="border border-sphotel-border bg-bg-elevated rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent"
                value={email} onChange={(e) => setEmail(e.target.value)} autoFocus required />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium">Password</label>
              <input type="password" className="border border-sphotel-border bg-bg-elevated rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent"
                value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" required />
            </div>
            {error && <p className="text-status-error text-xs">{error}</p>}
            <button type="submit" className="bg-sphotel-accent text-white rounded-lg py-2 text-sm font-medium">Continue</button>
            <button type="button" onClick={() => navigate(`/t/${code}`)} className="text-xs text-text-muted underline">Back</button>
          </form>
        )}
        {step === 'totp' && (
          <form onSubmit={handleTotp} className="flex flex-col gap-4">
            <div className="text-center text-sm text-text-secondary">
              <p>Signing in as</p><p className="font-medium text-text-primary">{email}</p>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium">Authenticator Code</label>
              <input type="text" inputMode="numeric"
                className="border border-sphotel-border bg-bg-elevated rounded-lg px-3 py-2 text-sm text-center tracking-widest text-lg font-mono text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent"
                value={totpCode} onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="000000" autoFocus maxLength={6} />
            </div>
            <div className="flex items-center gap-2 mt-1">
              <input 
                type="checkbox" 
                id="remember_admin" 
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 rounded border-sphotel-border text-sphotel-accent focus:ring-sphotel-accent"
              />
              <label htmlFor="remember_admin" className="text-sm text-text-secondary cursor-pointer">
                Remember me on this device
              </label>
            </div>
            {error && <p className="text-status-error text-xs">{error}</p>}
            <button type="submit" disabled={loginMutation.isPending || totpCode.length !== 6}
              className="bg-sphotel-accent text-white rounded-lg py-2 mt-2 text-sm font-medium disabled:opacity-50">
              {loginMutation.isPending ? 'Signing in…' : 'Sign in'}
            </button>
            <button type="button" onClick={() => { setStep('credentials'); setError('') }} className="text-xs text-text-muted underline">Back</button>
          </form>
        )}
      </div>
    </div>
  )
}
