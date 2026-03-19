import { apiClient } from '../../../lib/api'

export interface VendorItem {
  slug: string
  name: string
}

export const vendorsApi = {
  list: (): Promise<VendorItem[]> =>
    apiClient.get<VendorItem[]>('/api/v1/tenants/me/online-vendors').then((r) => r.data),

  add: (vendor: VendorItem): Promise<VendorItem[]> =>
    apiClient.post<VendorItem[]>('/api/v1/tenants/me/online-vendors', vendor).then((r) => r.data),

  remove: (slug: string): Promise<void> =>
    apiClient.delete(`/api/v1/tenants/me/online-vendors/${slug}`).then(() => undefined),
}
