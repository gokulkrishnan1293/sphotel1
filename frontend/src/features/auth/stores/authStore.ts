import { create } from 'zustand'
import type { MeResponse } from '../api/auth'

const USER_KEY = 'currentUser'

function loadUser(): MeResponse | null {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? (JSON.parse(raw) as MeResponse) : null
  } catch {
    return null
  }
}

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
  currentUser: loadUser(),
  setCurrentUser: (user) => { localStorage.setItem(USER_KEY, JSON.stringify(user)); set({ currentUser: user }) },
  clearCurrentUser: () => {
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem('selectedTenantSlug')
    set({ currentUser: null, loginTenantSlug: null, selectedTenantSlug: null })
  },
  selectedTenantSlug: localStorage.getItem('selectedTenantSlug'),
  setSelectedTenantSlug: (slug) => { localStorage.setItem('selectedTenantSlug', slug); set({ selectedTenantSlug: slug }) },
  loginTenantSlug: null,
  setLoginTenantSlug: (slug) => set({ loginTenantSlug: slug }),
}))
