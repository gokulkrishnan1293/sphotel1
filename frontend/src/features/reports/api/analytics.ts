import { apiClient } from '../../../lib/api'
import type { DailySummary, HeatmapCell, VelocityItem, TableTurn, WaiterPerf, CustomQueryRow } from '../types'

const BASE = '/api/v1/analytics'

export const analyticsApi = {
  summary: (date?: string): Promise<DailySummary> =>
    apiClient.get<DailySummary>(`${BASE}/summary${date ? `?for_date=${date}` : ''}`).then((r) => r.data),

  heatmap: (days = 28): Promise<HeatmapCell[]> =>
    apiClient.get<HeatmapCell[]>(`${BASE}/heatmap?days=${days}`).then((r) => r.data),

  velocity: (days = 14): Promise<VelocityItem[]> =>
    apiClient.get<VelocityItem[]>(`${BASE}/velocity?days=${days}`).then((r) => r.data),

  tableTurns: (days = 7): Promise<TableTurn[]> =>
    apiClient.get<TableTurn[]>(`${BASE}/table-turns?days=${days}`).then((r) => r.data),

  waiterPerformance: (days = 7): Promise<WaiterPerf[]> =>
    apiClient.get<WaiterPerf[]>(`${BASE}/waiter-performance?days=${days}`).then((r) => r.data),

  customQuery: (body: { dimension: string; metric: string; days: number }): Promise<CustomQueryRow[]> =>
    apiClient.post<CustomQueryRow[]>(`${BASE}/custom-query`, body).then((r) => r.data),
}
