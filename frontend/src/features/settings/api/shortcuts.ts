import { apiClient } from '@/lib/api'
import type { ShortcutMap } from '@/lib/shortcutStore'

export const shortcutsApi = {
  get: (): Promise<ShortcutMap> =>
    apiClient.get<ShortcutMap>('/api/v1/keyboard-shortcuts').then((r) => r.data),
  update: (data: Partial<ShortcutMap>): Promise<ShortcutMap> =>
    apiClient.patch<ShortcutMap>('/api/v1/keyboard-shortcuts', data).then((r) => r.data),
}
