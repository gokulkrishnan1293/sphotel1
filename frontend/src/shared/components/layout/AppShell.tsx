import { type ReactNode } from 'react'
import { Outlet } from 'react-router'
import { Sidebar } from './Sidebar'
import { MainContent } from './MainContent'
import { MobileNav } from './MobileNav'
import { useNetworkWatcher } from '@/lib/networkStatus'
import { OfflineBanner } from './OfflineBanner'
import { RecoveryModal } from '@/features/billing/components/RecoveryModal'

interface AppShellProps {
  children?: ReactNode
}

export function AppShell({ children }: AppShellProps) {
  useNetworkWatcher()
  return (
    <div className="flex h-screen w-full overflow-hidden bg-bg-base">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <OfflineBanner />
        <MainContent>{children ?? <Outlet />}</MainContent>
      </div>
      <MobileNav />
      <RecoveryModal />
    </div>
  )
}
