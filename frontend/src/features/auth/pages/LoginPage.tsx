import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { authApi } from '../api/auth'
import { useAuthStore } from '../stores/authStore'
import { applyTheme, type Theme } from '@/lib/theme'
import {  Link } from 'react-router'

export function LoginPage() {
  const setCurrentUser = useAuthStore((s) => s.setCurrentUser)

  const [step, setStep] = useState<'credentials' | 'totp'>('credentials')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [totpCode, setTotpCode] = useState('')
  const [error, setError] = useState('')

  const loginMutation = useMutation({
    mutationFn: async (payload: Parameters<typeof authApi.adminLogin>[0]) => {
      await authApi.adminLogin(payload)
      return authApi.me()
    },
    onSuccess: (user) => {
      setCurrentUser(user)
      const theme = user.preferences?.theme as Theme | undefined
      if (theme) applyTheme(theme)
      window.location.href = '/admin/menu'
    },
    onError: (err: Error) => {
      setError(err.message || 'Login failed. Check your credentials and try again.')
      setTotpCode('')
    },
  })

  function handleCredentialsSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (!email.trim() || !password) return
    setStep('totp')
  }

  function handleTotpSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (totpCode.length !== 6) {
      setError('Enter the 6-digit code from your authenticator app.')
      return
    }
    loginMutation.mutate({ email: email.trim(), password, totp_code: totpCode })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-base">
      <div className="w-full max-w-sm bg-bg-surface rounded-xl shadow-lg p-8 flex flex-col gap-6">
        {/* Logo / Title */}
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Nive's Chain</h1>
          <p className="text-sm text-text-muted mt-1">Admin Portal</p>
        </div>

        {/* Step 1: Email + Password */}
        {step === 'credentials' && (
          <form onSubmit={handleCredentialsSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium">Email</label>
              <input
                type="email"
                className="border border-sphotel-border bg-bg-elevated rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@restaurant.com"
                autoFocus
                required
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium">Password</label>
              <input
                type="password"
                className="border border-sphotel-border bg-bg-elevated rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>
            {error && <p className="text-status-error text-xs">{error}</p>}
            <button
              type="submit"
              className="bg-sphotel-accent text-white rounded-lg py-2 text-sm font-medium"
            >
              Continue
            </button>
            <p className="text-center text-xs text-text-muted">
            restaurant login?{' '}
            <Link key="t" to="/t" className="underline">Sign in here</Link>
          </p>
          </form>
          
        )}

        {/* Step 2: TOTP */}
        {step === 'totp' && (
          <form onSubmit={handleTotpSubmit} className="flex flex-col gap-4">
            <div className="text-center text-sm text-text-secondary">
              <p>Signing in as</p>
              <p className="font-medium text-text-primary">{email}</p>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium">Authenticator Code</label>
              <input
                type="text"
                inputMode="numeric"
                className="border border-sphotel-border bg-bg-elevated rounded-lg px-3 py-2 text-sm text-center tracking-widest text-lg font-mono text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent"
                value={totpCode}
                onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="000000"
                autoFocus
                maxLength={6}
              />
              <p className="text-xs text-text-muted">
                Enter the 6-digit code from Google Authenticator / Authy
              </p>
            </div>
            {error && <p className="text-status-error text-xs">{error}</p>}
            <button
              type="submit"
              disabled={loginMutation.isPending || totpCode.length !== 6}
              className="bg-sphotel-accent text-white rounded-lg py-2 text-sm font-medium disabled:opacity-50"
            >
              {loginMutation.isPending ? 'Signing in…' : 'Sign in'}
            </button>
            <button
              type="button"
              onClick={() => { setStep('credentials'); setError('') }}
              className="text-xs text-text-muted underline"
            >
              Back
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
