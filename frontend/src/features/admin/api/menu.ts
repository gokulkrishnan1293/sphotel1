import { apiClient } from '../../../lib/api'
import type { CategoryResponse, MenuItemCreate, MenuItemResponse, MenuItemUpdate } from '../types/menu'

export const menuApi = {
  list: (): Promise<MenuItemResponse[]> =>
    apiClient.get<MenuItemResponse[]>('/api/v1/menu/items').then((r) => r.data),

  create: (data: MenuItemCreate): Promise<MenuItemResponse> =>
    apiClient.post<MenuItemResponse>('/api/v1/menu/items', data).then((r) => r.data),

  update: (id: string, data: MenuItemUpdate): Promise<MenuItemResponse> =>
    apiClient.patch<MenuItemResponse>(`/api/v1/menu/items/${id}`, data).then((r) => r.data),

  delete: (id: string): Promise<void> =>
    apiClient.delete(`/api/v1/menu/items/${id}`).then(() => undefined),

  listCategories: (): Promise<CategoryResponse[]> =>
    apiClient.get<CategoryResponse[]>('/api/v1/menu/categories').then((r) => r.data),

  renameCategory: (oldName: string, newName: string): Promise<void> =>
    apiClient.patch(`/api/v1/menu/categories/${encodeURIComponent(oldName)}`, { new_name: newName }).then(() => undefined),

  exportCsv: (): Promise<string> =>
    apiClient.get<string>('/api/v1/menu/export', { responseType: 'text' }).then((r) => r.data as unknown as string),

  importCsv: (file: File): Promise<{ created: number; errors: string[] }> => {
    const form = new FormData()
    form.append('file', file)
    return apiClient.post<{ created: number; errors: string[] }>('/api/v1/menu/import', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data)
  },
}
