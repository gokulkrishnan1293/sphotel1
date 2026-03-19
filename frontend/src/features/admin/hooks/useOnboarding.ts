import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '../../auth/stores/authStore'
import { onboardingApi } from '../api/onboarding'

const ONBOARDING_KEY = ['onboarding'] as const

export function useOnboarding() {
  const role = useAuthStore((s) => s.currentUser?.role)
  return useQuery({
    queryKey: ONBOARDING_KEY,
    queryFn: onboardingApi.getStatus,
    enabled: role === 'admin',
    staleTime: 60_000,
  })
}

export function useCompleteOnboarding() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: onboardingApi.complete,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ONBOARDING_KEY })
    },
  })
}
