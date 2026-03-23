import { useEffect } from 'react'
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
  const { isLoading, isError } = useMe()

  useEffect(() => {
    // Only redirect when the server explicitly rejects (online + error).
    // A network failure while offline is not a sign-out event.
    if (!isLoading && isError && isOnline) {
      window.location.href = loginTenantSlug ? `/t/${loginTenantSlug}` : '/t'
    }
  }, [isLoading, isError, isOnline, loginTenantSlug])

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
