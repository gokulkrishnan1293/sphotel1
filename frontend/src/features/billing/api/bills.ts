import { apiClient } from '../../../lib/api'
import type {
  AddItemRequest,
  BillItemResponse,
  BillResponse,
  BillSummaryResponse,
  CloseBillRequest,
  KotTicketResponse,
  OpenBillRequest,
  UpdateItemRequest,
} from '../types/bills'

export const billsApi = {
  listOpen: (): Promise<BillSummaryResponse[]> =>
    apiClient.get<BillSummaryResponse[]>('/api/v1/bills').then((r) => r.data),

  listRecent: (): Promise<BillSummaryResponse[]> =>
    apiClient.get<BillSummaryResponse[]>('/api/v1/bills/recent').then((r) => r.data),

  open: (data: OpenBillRequest): Promise<BillResponse> =>
    apiClient.post<BillResponse>('/api/v1/bills', data).then((r) => r.data),

  get: (id: string): Promise<BillResponse> =>
    apiClient.get<BillResponse>(`/api/v1/bills/${id}`).then((r) => r.data),

  addItem: (billId: string, data: AddItemRequest): Promise<BillItemResponse> =>
    apiClient.post<BillItemResponse>(`/api/v1/bills/${billId}/items`, data).then((r) => r.data),

  updateItem: (billId: string, itemId: string, data: UpdateItemRequest): Promise<BillItemResponse> =>
    apiClient
      .patch<BillItemResponse>(`/api/v1/bills/${billId}/items/${itemId}`, data)
      .then((r) => r.data),

  removeItem: (billId: string, itemId: string): Promise<void> =>
    apiClient.delete(`/api/v1/bills/${billId}/items/${itemId}`).then(() => undefined),

  fireKot: (billId: string): Promise<KotTicketResponse> =>
    apiClient.post<KotTicketResponse>(`/api/v1/bills/${billId}/kot`).then((r) => r.data),

  close: (billId: string, data: CloseBillRequest): Promise<BillResponse> =>
    apiClient.post<BillResponse>(`/api/v1/bills/${billId}/close`, data).then((r) => r.data),

  void: (billId: string): Promise<BillResponse> =>
    apiClient.post<BillResponse>(`/api/v1/bills/${billId}/void`).then((r) => r.data),

  print: (billId: string, jobType: 'receipt' | 'kot' = 'receipt'): Promise<void> =>
    apiClient.post('/api/v1/print-jobs', { bill_id: billId, job_type: jobType }).then(() => undefined),

  updatePaymentMethod: (billId: string, payment_method: PaymentMethod): Promise<BillResponse> =>
    apiClient.patch<BillResponse>(`/api/v1/bills/${billId}/payment-method`, { payment_method }).then((r) => r.data),
}
