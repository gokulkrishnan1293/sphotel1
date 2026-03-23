import { useEffect } from 'react'
import { isAxiosError } from 'axios'
import { useAuthStore } from '../stores/authStore'
import { useMe } from '../hooks/useAuth'
import { useNetworkStore } from '../../../lib/networkStatus'

interface Props {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: Props) {
  const currentUser = useAuthStore((s) => s.currentUser)
  const loginTenantSlug = useAuthStore((s) => s.loginTenantSlug)
  const isOnline = useNetworkStore((s) => s.isOnline)
  const { isLoading, isError, error } = useMe()

  useEffect(() => {
    if (!isLoading && isError && isOnline) {
      // A network-level failure (no HTTP response) means we're offline — don't sign out.
      // Only redirect when the server explicitly rejects the session (has an HTTP response).
      const isNetworkError = isAxiosError(error) && !error.response
      if (isNetworkError) return
      window.location.href = loginTenantSlug ? `/t/${loginTenantSlug}` : '/t'
    }
  }, [isLoading, isError, isOnline, loginTenantSlug, error])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg-base">
        <span className="text-sm text-gray-400">Loading…</span>
      </div>
    )
  }

  if (!currentUser) return null

  return <>{children}</>
}
