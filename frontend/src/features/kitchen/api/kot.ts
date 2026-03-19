import { apiClient } from '../../../lib/api'
import type { ActiveKot } from '../types/kot'

export const kotApi = {
  listActive: (): Promise<ActiveKot[]> =>
    apiClient.get<ActiveKot[]>('/api/v1/kot/active').then((r) => r.data),

  markReady: (kotId: string): Promise<void> =>
    apiClient.post(`/api/v1/kot/${kotId}/ready`).then(() => undefined),

  toggleItemReady: (kotId: string, itemId: string): Promise<string[]> =>
    apiClient.post<string[]>(`/api/v1/kot/${kotId}/items/${itemId}/ready`).then((r) => r.data),
}
