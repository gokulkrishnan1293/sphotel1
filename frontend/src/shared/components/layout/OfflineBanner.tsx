import { useNetworkStore } from '@/lib/networkStatus'

export function OfflineBanner() {
  const isOnline = useNetworkStore((s) => s.isOnline)

  if (isOnline) return null

  return (
    <div className="sticky top-0 z-50 w-full bg-amber-500 px-4 py-2 text-center text-sm font-medium text-white">
      You&apos;re offline — changes will sync when reconnected.
    </div>
  )
}
