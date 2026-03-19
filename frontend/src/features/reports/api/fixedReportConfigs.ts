import { apiClient } from '../../../lib/api'

export type FixedReportType = 'top_items' | 'waiter_performance' | 'payment_breakdown'

export interface FixedReportConfig {
  id: string
  report_type: FixedReportType
  telegram_schedule: string | null
  is_visible: boolean
}

const BASE = '/api/v1/fixed-report-configs'

export const fixedReportConfigsApi = {
  list: (): Promise<FixedReportConfig[]> => apiClient.get(BASE).then((r) => r.data),
  update: (type: string, body: { telegram_schedule: string | null; is_visible: boolean }): Promise<FixedReportConfig> =>
    apiClient.patch(`${BASE}/${type}`, body).then((r) => r.data),
}
