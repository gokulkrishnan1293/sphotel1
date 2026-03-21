import { apiClient } from '../../../lib/api'
import type { UserRole } from './staff'

export interface MeResponse {
  user_id: string
  tenant_id: string
  name: string
  role: UserRole
  email: string | null
  is_active: boolean
  preferences: Record<string, unknown>
}

export interface AdminLoginPayload {
  email: string
  password: string
  totp_code: string
  tenant_slug?: string
  remember_me?: boolean
}

export interface PinLoginPayload {
  user_id: string
  pin: string
  tenant_slug: string
  remember_me?: boolean
}

export interface TenantPublicInfo {
  id: string
  name: string
  slug: string
}

export interface StaffPublicItem {
  id: string
  name: string
  role: string
}

export interface UpdateCredentialsPayload {
  email?: string
  password?: string
}

export const authApi = {
  adminLogin: (payload: AdminLoginPayload): Promise<{ message: string }> =>
    apiClient.post<{ message: string }>('/api/v1/auth/admin', payload).then((r) => r.data),

  pinLogin: (payload: PinLoginPayload): Promise<{ message: string }> =>
    apiClient.post<{ message: string }>('/api/v1/auth/pin', payload).then((r) => r.data),

  me: (): Promise<MeResponse> =>
    apiClient.get<MeResponse>('/api/v1/auth/me').then((r) => r.data),

  logout: (): Promise<{ message: string }> =>
    apiClient.post<{ message: string }>('/api/v1/auth/logout').then((r) => r.data),

  tenantInfo: (slug: string): Promise<TenantPublicInfo> =>
    apiClient.get<TenantPublicInfo>(`/api/v1/auth/tenant/${slug}`).then((r) => r.data),

  tenantStaff: (slug: string): Promise<StaffPublicItem[]> =>
    apiClient.get<StaffPublicItem[]>(`/api/v1/auth/tenant/${slug}/staff`).then((r) => r.data),

  updateCredentials: (payload: UpdateCredentialsPayload): Promise<MeResponse> =>
    apiClient.patch<MeResponse>('/api/v1/auth/credentials', payload).then((r) => r.data),

  updatePreferences: (theme: 'dark' | 'high_contrast' | 'light'): Promise<MeResponse> =>
    apiClient.patch<MeResponse>('/api/v1/users/me/preferences', { theme }).then((r) => r.data),
}
