import { create } from 'zustand'
import type { MeResponse } from '../api/auth'

interface AuthState {
  currentUser: MeResponse | null
  setCurrentUser: (user: MeResponse) => void
  clearCurrentUser: () => void
  selectedTenantSlug: string | null
  setSelectedTenantSlug: (slug: string) => void
  loginTenantSlug: string | null
  setLoginTenantSlug: (slug: string | null) => void
}

export const useAuthStore = create<AuthState>()((set) => ({
  currentUser: null,
  setCurrentUser: (user) => set({ currentUser: user }),
  clearCurrentUser: () => { localStorage.removeItem('selectedTenantSlug'); set({ currentUser: null, loginTenantSlug: null, selectedTenantSlug: null }) },
  selectedTenantSlug: localStorage.getItem('selectedTenantSlug'),
  setSelectedTenantSlug: (slug) => { localStorage.setItem('selectedTenantSlug', slug); set({ selectedTenantSlug: slug }) },
  loginTenantSlug: null,
  setLoginTenantSlug: (slug) => set({ loginTenantSlug: slug }),
}))
