import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { authApi } from '../api/auth'
import { useAuthStore } from '../stores/authStore'

export function useMe() {
  const setCurrentUser = useAuthStore((s) => s.setCurrentUser)
  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      const user = await authApi.me()
      setCurrentUser(user)
      return user
    },
    retry: false,
    staleTime: 5 * 60 * 1000,
  })
}

export function useLogout() {
  const clearCurrentUser = useAuthStore((s) => s.clearCurrentUser)
  const loginTenantSlug = useAuthStore((s) => s.loginTenantSlug)
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      clearCurrentUser()
      queryClient.clear()
      window.location.href = loginTenantSlug ? `/t/${loginTenantSlug}` : '/login'
    },
  })
}
