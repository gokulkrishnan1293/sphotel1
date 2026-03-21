import { apiClient } from '../../../lib/api'

export interface PWASettings {
  app_name?: string
  app_short_name?: string
}

export interface TenantBranding {
  id: string
  name: string
  pwa_settings?: PWASettings
  logo_path?: string
}

export const brandingApi = {
  getBranding: (): Promise<TenantBranding> =>
    apiClient.get<TenantBranding>('/api/v1/tenants/me/branding').then((r) => r.data),
  updateBranding: (pwa_settings: PWASettings): Promise<TenantBranding> =>
    apiClient.patch('/api/v1/tenants/me/branding', { pwa_settings }).then((r) => r.data),

  uploadLogo: (file: File): Promise<TenantBranding> => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/api/v1/tenants/me/logo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then((r) => r.data)
  }
}
