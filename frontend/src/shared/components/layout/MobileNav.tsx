import { useState } from 'react'
import { useLocation, Link } from 'react-router'
import { ReceiptText, UtensilsCrossed, Users, BarChart3, ChefHat, MoreHorizontal, Send, Printer, Keyboard } from 'lucide-react'
import { useAuthStore } from '@/features/auth/stores/authStore'

export function MobileNav() {
  const currentUser = useAuthStore((s) => s.currentUser)
  const { pathname } = useLocation()
  const [moreOpen, setMoreOpen] = useState(false)

  const isAdmin = ['admin', 'super_admin'].includes(currentUser?.role ?? '')
  const isBiller = ['biller', 'manager', 'admin', 'super_admin'].includes(currentUser?.role ?? '')
  const isKitchen = currentUser?.role === 'kitchen_staff'

  const items = [
    { label: 'Billing', href: '/billing', Icon: ReceiptText, show: isBiller },
    { label: 'Menu', href: '/admin/menu', Icon: UtensilsCrossed, show: isAdmin },
    { label: 'Staff', href: '/admin/staff', Icon: Users, show: isAdmin },
    { label: 'Reports', href: '/reports', Icon: BarChart3, show: isAdmin },
    { label: 'Kitchen', href: '/kitchen', Icon: ChefHat, show: isAdmin || isKitchen || isBiller },
  ].filter((n) => n.show)

  const moreItems = [
    { label: 'Telegram', href: '/admin/telegram', Icon: Send, show: isAdmin },
    { label: 'Printer', href: '/admin/print-settings', Icon: Printer, show: isAdmin },
    { label: 'Shortcuts', href: '/admin/shortcuts', Icon: Keyboard, show: isAdmin },
  ].filter((n) => n.show)

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-bg-surface border-t border-sphotel-border pb-safe">
      <div className="flex items-center justify-around h-14 px-1">
        {items.map(({ label, href, Icon }) => (
          <Link key={href} to={href}
            className={`flex flex-col items-center gap-0.5 flex-1 py-1.5 transition-colors ${pathname.startsWith(href) ? 'text-sphotel-accent' : 'text-text-muted'}`}>
            <Icon size={22} />
            <span className="text-[10px] font-medium">{label}</span>
          </Link>
        ))}
        
        {moreItems.length > 0 && (
          <div className="relative flex-1 flex flex-col items-center">
            <button onClick={() => setMoreOpen(!moreOpen)}
              className={`flex flex-col items-center gap-0.5 w-full py-1.5 transition-colors ${moreOpen ? 'text-sphotel-accent' : 'text-text-muted'}`}>
              <MoreHorizontal size={22} />
              <span className="text-[10px] font-medium">More</span>
            </button>
            
            {moreOpen && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setMoreOpen(false)} />
                <div className="absolute bottom-full mb-2 right-0 bg-bg-elevated border border-sphotel-border rounded-xl shadow-xl min-w-[160px] py-2 z-50 animate-in fade-in slide-in-from-bottom-2 duration-150">
                  <p className="px-4 py-1.5 text-xs text-text-muted font-medium uppercase tracking-wide">Settings</p>
                  {moreItems.map(({ label, href, Icon }) => (
                    <Link key={href} to={href} onClick={() => setMoreOpen(false)}
                      className={`flex items-center gap-3 px-4 py-2.5 text-sm transition-colors hover:bg-bg-base ${pathname.startsWith(href) ? 'text-sphotel-accent font-medium' : 'text-text-primary'}`}>
                      <Icon size={18} className="opacity-70" />
                      {label}
                    </Link>
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  )
}
