import { useTenantName } from '@/shared/hooks/useTenantName'

export function TenantBadge() {
  const tenantName = useTenantName()
  if (!tenantName) return null
  return (
    <div className="hidden md:flex items-center gap-2">
      <span className="w-px h-4 bg-sphotel-border" />
      <span className="relative flex h-2 w-2">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sphotel-accent opacity-60" />
        <span className="relative inline-flex rounded-full h-2 w-2 bg-sphotel-accent" />
      </span>
      <span className="text-sm font-semibold text-sphotel-accent tracking-wide">{tenantName}</span>
    </div>
  )
}
