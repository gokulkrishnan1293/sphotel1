import { useLocation, Link } from 'react-router'
import { ReceiptText, UtensilsCrossed, Users, BarChart3, ChefHat } from 'lucide-react'
import { useAuthStore } from '@/features/auth/stores/authStore'

export function MobileNav() {
  const currentUser = useAuthStore((s) => s.currentUser)
  const { pathname } = useLocation()

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

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-bg-surface border-t border-sphotel-border">
      <div className="flex items-center justify-around h-14 px-1">
        {items.map(({ label, href, Icon }) => (
          <Link key={href} to={href}
            className={`flex flex-col items-center gap-0.5 flex-1 py-1.5 transition-colors ${pathname.startsWith(href) ? 'text-sphotel-accent' : 'text-text-muted'}`}>
            <Icon size={22} />
            <span className="text-[10px] font-medium">{label}</span>
          </Link>
        ))}
      </div>
    </nav>
  )
}
