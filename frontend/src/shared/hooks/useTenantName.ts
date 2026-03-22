import { useQuery } from '@tanstack/react-query'
import { authApi } from '@/features/auth/api/auth'
import { useAuthStore } from '@/features/auth/stores/authStore'

export function useTenantName(): string {
  const currentUser = useAuthStore((s) => s.currentUser)
  const selectedTenantSlug = useAuthStore((s) => s.selectedTenantSlug)
  const isSuperAdmin = currentUser?.role === 'super_admin'
  const activeSlug = selectedTenantSlug ?? currentUser?.tenant_id

  const { data: tenant } = useQuery({
    queryKey: ['tenantInfo', activeSlug],
    queryFn: () => authApi.tenantInfo(activeSlug!),
    enabled: !!activeSlug && !isSuperAdmin,
  })

  if (!activeSlug) return ''
  return isSuperAdmin ? 'Sphotel Admin' : (tenant?.name ?? '')
}
