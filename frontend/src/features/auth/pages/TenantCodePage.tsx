import { useState } from 'react'
import { useNavigate } from 'react-router'
import { authApi } from '../api/auth'

export function TenantCodePage() {
  const navigate = useNavigate()
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const slug = code.trim().toLowerCase()
    if (!slug) return
    setError('')
    setLoading(true)
    try {
      await authApi.tenantInfo(slug)
      navigate(`/t/${slug}`)
    } catch {
      setError('Tenant not found. Check your code and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-base">
      <div className="w-full max-w-sm bg-bg-surface rounded-xl shadow-lg p-8 flex flex-col gap-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Restaurant</h1>
          <p className="text-sm text-text-muted mt-1">Enter your restaurant code</p>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium">Tenant Code</label>
            <input
              type="text"
              className="border border-sphotel-border bg-bg-elevated rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent lowercase"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="my-restaurant"
              autoFocus
              required
            />
          </div>
          {error && <p className="text-status-error text-xs">{error}</p>}
          <button
            type="submit"
            disabled={loading || !code.trim()}
            className="bg-sphotel-accent text-white rounded-lg py-2 text-sm font-medium disabled:opacity-50"
          >
            {loading ? 'Checking…' : 'Continue'}
          </button>
        </form>
      </div>
    </div>
  )
}
