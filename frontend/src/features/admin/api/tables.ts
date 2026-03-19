import { apiClient } from '../../../lib/api'
import type { SectionCreate, SectionResponse, TableCreate, TableResponse, TableUpdate } from '../types/tables'

export const tablesApi = {
  listSections: (): Promise<SectionResponse[]> =>
    apiClient.get<SectionResponse[]>('/api/v1/tables/sections').then((r) => r.data),

  createSection: (data: SectionCreate): Promise<SectionResponse> =>
    apiClient.post<SectionResponse>('/api/v1/tables/sections', data).then((r) => r.data),

  updateSection: (id: string, data: Partial<SectionCreate>): Promise<SectionResponse> =>
    apiClient.patch<SectionResponse>(`/api/v1/tables/sections/${id}`, data).then((r) => r.data),

  deleteSection: (id: string): Promise<void> =>
    apiClient.delete(`/api/v1/tables/sections/${id}`).then(() => undefined),

  listTables: (): Promise<TableResponse[]> =>
    apiClient.get<TableResponse[]>('/api/v1/tables/layouts').then((r) => r.data),

  createTable: (data: TableCreate): Promise<TableResponse> =>
    apiClient.post<TableResponse>('/api/v1/tables/layouts', data).then((r) => r.data),

  updateTable: (id: string, data: TableUpdate): Promise<TableResponse> =>
    apiClient.patch<TableResponse>(`/api/v1/tables/layouts/${id}`, data).then((r) => r.data),

  deleteTable: (id: string): Promise<void> =>
    apiClient.delete(`/api/v1/tables/layouts/${id}`).then(() => undefined),
}
