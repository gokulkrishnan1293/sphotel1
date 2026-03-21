import { useQuery } from '@tanstack/react-query'
import { authApi } from '@/features/auth/api/auth'
import { useAuthStore } from '@/features/auth/stores/authStore'
import { Building2 } from 'lucide-react'

export function TenantHeader() {
  const currentUser = useAuthStore((s) => s.currentUser)
  const selectedTenantSlug = useAuthStore((s) => s.selectedTenantSlug)
  
  const isSuperAdmin = currentUser?.role === 'super_admin'
  const activeSlug = selectedTenantSlug ?? currentUser?.tenant_id
  
  const { data: tenant } = useQuery({
    queryKey: ['tenantInfo', activeSlug],
    queryFn: () => authApi.tenantInfo(activeSlug!),
    enabled: !!activeSlug && !isSuperAdmin
  })

  // SuperAdmins already see the chosen tenant in the sidebar toggle,
  // but showing it here is also okay. If we only want it strictly in "tenant mode" (non-super):
  if (isSuperAdmin) return null

  if (!activeSlug) return null

  return (
    <div className="h-12 border-b border-sphotel-border bg-bg-surface flex items-center px-6 shrink-0 z-10">
      <div className="flex items-center gap-2.5 text-text-primary">
        <div className="w-6 h-6 rounded shadow-sm bg-sphotel-accent-subtle text-sphotel-accent flex items-center justify-center">
          <Building2 size={13} strokeWidth={2.5} />
        </div>
        <span className="font-semibold text-sm tracking-wide">
          {tenant?.name ?? 'Loading...'}
        </span>
      </div>
    </div>
  )
}
