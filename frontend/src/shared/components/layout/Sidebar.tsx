import { useState } from 'react'
import { Link } from 'react-router'
import { useQuery } from '@tanstack/react-query'
import { UtensilsCrossed, ChevronDown, Building2, Palette, ReceiptText, LayoutGrid, Users, ChefHat, Printer, BarChart3, Send, Keyboard, LogOut, Smartphone } from 'lucide-react'
import { tenantsApi } from '@/features/admin/api/tenants'
import { useAuthStore } from '@/features/auth/stores/authStore'
import { useLogout } from '@/features/auth/hooks/useAuth'
import { AppearancePopover } from './AppearancePopover'
import { useAppearance } from './useAppearance'

export function Sidebar() {
  const currentUser = useAuthStore((s) => s.currentUser)
  const selectedTenantSlug = useAuthStore((s) => s.selectedTenantSlug)
  const setSelectedTenantSlug = useAuthStore((s) => s.setSelectedTenantSlug)
  const { mutate: logout } = useLogout()
  const { activeTheme, activeAccent, handleTheme, handleAccent } = useAppearance()

  const isSuperAdmin = currentUser?.role === 'super_admin'
  const isAdmin = currentUser?.role === 'admin' || isSuperAdmin
  const isBiller = ['biller', 'manager', 'admin', 'super_admin'].includes(currentUser?.role ?? '')

  const [tenantOpen, setTenantOpen] = useState(false)
  const [paletteOpen, setPaletteOpen] = useState(false)

  const { data: tenants } = useQuery({ queryKey: ['tenants'], queryFn: tenantsApi.list, enabled: isSuperAdmin })

  const activeTenantSlug = selectedTenantSlug ?? currentUser?.tenant_id
  const activeTenant = tenants?.find((t) => t.slug === activeTenantSlug)

  const NAV = [
    { label: 'Billing', href: '/billing', Icon: ReceiptText, show: isBiller },
    { label: 'Menu Items', href: '/admin/menu', Icon: UtensilsCrossed, show: isAdmin },
    { label: 'Tables', href: '/admin/tables', Icon: LayoutGrid, show: isAdmin },
    { label: 'Staff', href: '/admin/staff', Icon: Users, show: isAdmin },
    { label: 'Tenants', href: '/admin/tenants', Icon: Building2, show: isSuperAdmin },
    { label: 'Reports', href: '/reports', Icon: BarChart3, show: isAdmin },
    { label: 'Print Settings', href: '/admin/print-settings', Icon: Printer, show: isAdmin },
    { label: 'Telegram', href: '/admin/telegram', Icon: Send, show: isAdmin },
    { label: 'Shortcuts', href: '/admin/shortcuts', Icon: Keyboard, show: isAdmin },
    { label: 'Branding', href: '/admin/branding', Icon: Smartphone, show: isAdmin },
    { label: 'Kitchen', href: '/kitchen', Icon: ChefHat, show: isAdmin || currentUser?.role === 'kitchen_staff' || currentUser?.role === 'biller' },
  ]

  return (
    <aside className="hidden md:flex w-14 shrink-0 bg-bg-surface border-r border-sphotel-border flex-col items-center py-3 gap-1">
      {isSuperAdmin && (
        <div className="relative w-full px-1 mb-2">
          <button onClick={() => { setTenantOpen((o) => !o); setPaletteOpen(false) }} title={activeTenant?.name ?? 'Select tenant'}
            className="w-full flex flex-col items-center gap-0.5 px-1 py-1.5 rounded text-xs text-text-muted hover:bg-bg-base hover:text-text-primary transition-colors">
            <span className="w-7 h-7 rounded-full bg-sphotel-accent-subtle text-sphotel-accent flex items-center justify-center text-xs font-bold uppercase leading-none">
              {(activeTenant?.name ?? '?')[0]}
            </span>
            <ChevronDown size={10} className="opacity-50" />
          </button>
          {tenantOpen && (
            <div className="absolute left-full top-0 ml-2 z-50 bg-bg-elevated border border-sphotel-border rounded-lg shadow-xl min-w-44 py-1">
              <p className="px-3 py-1 text-xs text-text-muted font-medium uppercase tracking-wide">Tenant</p>
              {tenants?.map((t) => (
                <button key={t.slug} onClick={() => { setSelectedTenantSlug(t.slug); setTenantOpen(false) }}
                  className={`w-full text-left px-3 py-2 text-sm hover:bg-bg-base transition-colors ${t.slug === activeTenantSlug ? 'text-sphotel-accent font-medium' : 'text-text-primary'}`}>
                  {t.name}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {NAV.filter((n) => n.show).map(({ label, href, Icon }) => (
        <div key={href} className="relative group flex items-center">
          <Link to={href} className="w-10 h-10 flex items-center justify-center rounded-lg text-text-muted hover:bg-bg-base hover:text-text-primary transition-colors">
            <Icon size={20} />
          </Link>
          <div className="absolute left-full ml-3 px-2 py-1.5 bg-bg-elevated border border-sphotel-border text-text-primary text-xs font-medium rounded shadow-xl opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
            {label}
            <div className="absolute left-0 top-1/2 -ml-1 -mt-1 border-t-4 border-b-4 border-r-4 border-t-transparent border-b-transparent border-r-bg-elevated"></div>
            <div className="absolute left-0 top-1/2 -ml-[5px] -mt-1 border-t-4 border-b-4 border-r-4 border-t-transparent border-b-transparent border-r-sphotel-border -z-10"></div>
          </div>
        </div>
      ))}

      <div className="mt-auto flex flex-col items-center gap-1">
        <div className="relative">
          <button title="Appearance" onClick={() => { setPaletteOpen((o) => !o); setTenantOpen(false) }}
            className={`w-10 h-10 flex items-center justify-center rounded-lg transition-colors ${paletteOpen ? 'bg-sphotel-accent-subtle text-sphotel-accent' : 'text-text-muted hover:bg-bg-base hover:text-text-primary'}`}>
            <Palette size={18} />
          </button>
          {paletteOpen && (
            <AppearancePopover
              activeTheme={activeTheme}
              activeAccent={activeAccent}
              onTheme={handleTheme}
              onAccent={handleAccent}
              onClose={() => setPaletteOpen(false)}
              className="bottom-0 left-full ml-2"
            />
          )}
        </div>
        <button title="Logout" onClick={() => logout()}
          className="w-10 h-10 flex items-center justify-center rounded-lg text-text-muted hover:bg-bg-base hover:text-status-error transition-colors">
          <LogOut size={18} />
        </button>
        <div className="relative group flex items-center">
          <span className="text-[10px] text-text-muted/50 select-none cursor-default">
            v{__APP_VERSION__}
          </span>
          <div className="absolute left-full ml-3 px-2 py-1.5 bg-bg-elevated border border-sphotel-border text-text-primary text-xs font-medium rounded shadow-xl opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
            App version {__APP_VERSION__}
            <div className="absolute left-0 top-1/2 -ml-1 -mt-1 border-t-4 border-b-4 border-r-4 border-t-transparent border-b-transparent border-r-bg-elevated"></div>
            <div className="absolute left-0 top-1/2 -ml-[5px] -mt-1 border-t-4 border-b-4 border-r-4 border-t-transparent border-b-transparent border-r-sphotel-border -z-10"></div>
          </div>
        </div>
      </div>
    </aside>
  )
}
