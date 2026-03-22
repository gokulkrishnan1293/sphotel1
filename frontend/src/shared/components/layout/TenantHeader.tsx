import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { authApi } from '@/features/auth/api/auth'
import { useAuthStore } from '@/features/auth/stores/authStore'
import { Building2, Palette, LogOut } from 'lucide-react'
import { useAppearance } from './useAppearance'
import { AppearancePopover } from './AppearancePopover'
import { useLogout } from '@/features/auth/hooks/useAuth'

export function TenantHeader() {
  const currentUser = useAuthStore((s) => s.currentUser)
  const selectedTenantSlug = useAuthStore((s) => s.selectedTenantSlug)
  const { activeTheme, activeAccent, handleTheme, handleAccent } = useAppearance()
  const { mutate: logout } = useLogout()
  const [paletteOpen, setPaletteOpen] = useState(false)
  
  const isSuperAdmin = currentUser?.role === 'super_admin'
  const activeSlug = selectedTenantSlug ?? currentUser?.tenant_id
  
  const { data: tenant } = useQuery({
    queryKey: ['tenantInfo', activeSlug],
    queryFn: () => authApi.tenantInfo(activeSlug!),
    enabled: !!activeSlug && !isSuperAdmin
  })

  // Always hidden on desktop — each page shows tenant name inline in its own header.
  // On mobile this bar provides navigation, logout, and appearance controls.
  const hiddenOnDesktop = true

  if (!activeSlug && !isSuperAdmin) return null

  return (
    <div className={`h-12 border-b border-sphotel-border bg-bg-surface flex items-center justify-between px-4 md:px-6 shrink-0 z-10 ${hiddenOnDesktop ? 'md:hidden' : ''}`}>
      <div className="flex items-center gap-2.5 text-text-primary overflow-hidden">
        <div className="w-6 h-6 rounded shadow-sm bg-sphotel-accent-subtle text-sphotel-accent flex items-center justify-center shrink-0">
          <Building2 size={13} strokeWidth={2.5} />
        </div>
        <span className="font-semibold text-sm tracking-wide truncate">
          {isSuperAdmin ? (activeSlug ? (tenant?.name ?? activeSlug) : 'Sphotel Admin') : (tenant?.name ?? 'Loading...')}
        </span>
      </div>

      <div className="flex items-center gap-1 md:hidden">
        <div className="relative">
          <button onClick={() => setPaletteOpen((o) => !o)} title="Appearance"
            className={`w-9 h-9 flex items-center justify-center rounded-lg transition-colors ${paletteOpen ? 'bg-sphotel-accent-subtle text-sphotel-accent' : 'text-text-muted active:bg-bg-base'}`}>
            <Palette size={18} />
          </button>
          {paletteOpen && (
            <AppearancePopover
              activeTheme={activeTheme}
              activeAccent={activeAccent}
              onTheme={handleTheme}
              onAccent={handleAccent}
              onClose={() => setPaletteOpen(false)}
              className="top-full right-0 mt-2 origin-top-right scale-95 animate-in fade-in zoom-in duration-150"
            />
          )}
        </div>
        <button onClick={() => logout()} title="Logout"
          className="w-9 h-9 flex items-center justify-center rounded-lg text-text-muted active:bg-bg-base active:text-status-error transition-colors">
          <LogOut size={18} />
        </button>
      </div>
    </div>
  )
}
