import {
  type FeatureFlagKey,
  useFeatureFlagStore,
} from '@/lib/featureFlagStore'

/**
 * Returns the current value of a feature flag from the Zustand store.
 * Defaults to false before flags are hydrated from the API.
 */
export function useFeatureFlag(flag: FeatureFlagKey): boolean {
  return useFeatureFlagStore((state) => state[flag])
}
