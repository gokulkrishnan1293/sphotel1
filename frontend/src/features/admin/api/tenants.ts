import { apiClient } from '../../../lib/api'

export interface TenantSummary {
  id: string
  name: string
  slug: string
  is_active: boolean
  onboarding_completed: boolean
  created_at: string
}

export interface FeatureFlags {
  waiterMode: boolean
  suggestionEngine: boolean
  telegramAlerts: boolean
  gstModule: boolean
  payrollRewards: boolean
  discountComplimentary: boolean
  waiterTransfer: boolean
  billCloseUx: boolean
}

export const tenantsApi = {
  list: (): Promise<TenantSummary[]> =>
    apiClient.get<TenantSummary[]>('/api/v1/tenants').then((r) => r.data),

  create: (body: { name: string; subdomain: string }): Promise<TenantSummary> =>
    apiClient.post<TenantSummary>('/api/v1/super-admin/tenants', body).then((r) => r.data),

  update: (
    slug: string,
    body: { name?: string; is_active?: boolean },
  ): Promise<TenantSummary> =>
    apiClient
      .patch<TenantSummary>(`/api/v1/super-admin/tenants/${slug}`, body)
      .then((r) => r.data),

  getFeatures: (slug: string): Promise<FeatureFlags> =>
    apiClient
      .get<FeatureFlags>(`/api/v1/super-admin/tenants/${slug}/features`)
      .then((r) => r.data),

  updateFeatures: (slug: string, body: Partial<FeatureFlags>): Promise<FeatureFlags> =>
    apiClient
      .patch<FeatureFlags>(`/api/v1/super-admin/tenants/${slug}/features`, body)
      .then((r) => r.data),

  delete: (slug: string): Promise<void> =>
    apiClient.delete(`/api/v1/super-admin/tenants/${slug}`).then(() => undefined),
}
