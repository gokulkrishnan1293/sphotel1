import { apiClient } from '../../../lib/api'

export interface CustomReport {
  id: string
  name: string
  metric: string
  chart_type: string
  telegram_schedule: string | null
  dimension: string | null
  days: number
}

export interface ReportBody {
  name: string
  metric: string
  chart_type: string
  telegram_schedule: string | null
  dimension: string | null
  days: number
}

export const DIMENSIONS = [
  { value: 'waiter', label: 'Waiter' },
  { value: 'table', label: 'Table' },
  { value: 'payment_method', label: 'Payment Method' },
  { value: 'item', label: 'Item' },
  { value: 'category', label: 'Category' },
  { value: 'date', label: 'Date' },
  { value: 'hour', label: 'Hour of Day' },
]

export const REPORT_METRICS = [
  { value: 'revenue', label: 'Revenue' },
  { value: 'bill_count', label: 'Bill Count' },
  { value: 'avg_bill', label: 'Avg Bill Value' },
  { value: 'item_qty', label: 'Item Quantity' },
]

export const CHART_TYPES = ['bar', 'line', 'pie', 'table']

const BASE = '/api/v1/custom-reports'
export const customReportsApi = {
  list: (): Promise<CustomReport[]> => apiClient.get(BASE).then((r) => r.data),
  create: (body: ReportBody): Promise<CustomReport> => apiClient.post(BASE, body).then((r) => r.data),
  update: (id: string, body: ReportBody): Promise<CustomReport> => apiClient.patch(`${BASE}/${id}`, body).then((r) => r.data),
  remove: (id: string): Promise<void> => apiClient.delete(`${BASE}/${id}`).then(() => undefined),
}
