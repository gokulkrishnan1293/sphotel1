import { useEffect, type ReactNode } from 'react'
import { QueryClientProvider, useQuery } from '@tanstack/react-query'
import { queryClient } from '@/lib/queryClient'
import { apiClient } from '@/lib/api'
import { useFeatureFlagStore } from '@/lib/featureFlagStore'
import { useAuthStore } from '@/features/auth/stores/authStore'
import { applyTheme, type Theme } from '@/lib/theme'

interface ProvidersProps {
  children: ReactNode
}

interface FeatureFlagsResponse {
  waiterMode: boolean
  suggestionEngine: boolean
  telegramAlerts: boolean
  gstModule: boolean
  payrollRewards: boolean
  discountComplimentary: boolean
  waiterTransfer: boolean
  billCloseUx: boolean
}

/**
 * Fetches feature flags on mount and hydrates the Zustand store.
 * tenantId is null until Epic 2 auth is wired — query stays disabled,
 * leaving all flags at their default (false) values.
 */
function FeatureFlagHydrator({
  tenantId,
}: {
  tenantId: string | null
}): null {
  const setFlags = useFeatureFlagStore((s) => s.setFlags)

  const { data } = useQuery<FeatureFlagsResponse>({
    queryKey: ['featureFlags', tenantId],
    queryFn: () =>
      apiClient
        .get<FeatureFlagsResponse>(`/api/v1/tenants/${tenantId}/features`)
        .then((r) => r.data as FeatureFlagsResponse),
    enabled: tenantId !== null,
    staleTime: 55_000, // 55s — slightly under the Valkey 60s TTL
  })

  useEffect(() => {
    if (data) {
      setFlags(data)
    }
  }, [data, setFlags])

  return null
}

function ThemeHydrator(): null {
  const preferences = useAuthStore((s) => s.currentUser?.preferences)

  useEffect(() => {
    const storedTheme = preferences?.theme as Theme | undefined
    if (storedTheme) {
      applyTheme(storedTheme)
    }
    // If no user preference, FOUC script already applied system default
  }, [preferences])

  return null
}

export function Providers({ children }: ProvidersProps) {
  const tenantId = useAuthStore((s) => s.currentUser?.tenant_id ?? null)

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeHydrator />
      <FeatureFlagHydrator tenantId={tenantId} />
      {children}
    </QueryClientProvider>
  )
}
