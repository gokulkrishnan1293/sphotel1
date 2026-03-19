import type { ReactNode } from 'react'
import { type FeatureFlagKey } from '@/lib/featureFlagStore'
import { useFeatureFlag } from '@/shared/hooks/useFeatureFlag'

interface FeatureGateProps {
  flag: FeatureFlagKey
  children: ReactNode
  fallback?: ReactNode
}

/**
 * Renders children only when the given feature flag is enabled.
 * Renders fallback (default: null) when the flag is disabled or not yet loaded.
 *
 * Usage: <FeatureGate flag="waiterMode"><WaiterSurface /></FeatureGate>
 */
export function FeatureGate({
  flag,
  children,
  fallback = null,
}: FeatureGateProps): ReactNode {
  const enabled = useFeatureFlag(flag)
  return enabled ? children : fallback
}
