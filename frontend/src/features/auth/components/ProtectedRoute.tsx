import { useEffect } from 'react'
import { useAuthStore } from '../stores/authStore'
import { useMe } from '../hooks/useAuth'

interface Props {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: Props) {
  const currentUser = useAuthStore((s) => s.currentUser)
  const loginTenantSlug = useAuthStore((s) => s.loginTenantSlug)
  const { isLoading, isError } = useMe()

  useEffect(() => {
    if (!isLoading && isError) {
      window.location.href = loginTenantSlug ? `/t/${loginTenantSlug}` : '/t'
    }
  }, [isLoading, isError, loginTenantSlug])

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
