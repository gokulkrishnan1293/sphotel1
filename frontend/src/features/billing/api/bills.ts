import { apiClient } from '../../../lib/api'
import { writeBill, writeBillSummaries, readBill, readOpenBills, optimisticAddItem, optimisticRemoveItem, optimisticUpdateItem, optimisticFireKot } from '../../../lib/db/billsCache'
import { localPrintKot } from '../../../lib/localPrint'
import { enqueue } from '../../../lib/db/offlineQueue'
import { useNetworkStore } from '../../../lib/networkStatus'
import type {
  AddItemRequest, BillItemResponse, BillResponse,
  BillSummaryResponse, CloseBillRequest, KotTicketResponse,
  OpenBillRequest, PaymentMethod, UpdateItemRequest,
} from '../types/bills'

const offline = () => !useNetworkStore.getState().isOnline

export const billsApi = {
  listOpen: (): Promise<BillSummaryResponse[]> =>
    apiClient.get<BillSummaryResponse[]>('/api/v1/bills').then((r) => { writeBillSummaries(r.data).catch(() => {}); return r.data }).catch(() => readOpenBills()),
  listRecent: (): Promise<BillSummaryResponse[]> =>
    apiClient.get<BillSummaryResponse[]>('/api/v1/bills/recent').then((r) => r.data),
  listHistory: (q?: string, status?: string, limit = 50, offset = 0): Promise<BillSummaryResponse[]> =>
    apiClient.get<BillSummaryResponse[]>('/api/v1/bills/history', { params: { q, status, limit, offset } }).then((r) => r.data),

  open: async (data: OpenBillRequest): Promise<BillResponse> => {
    if (!offline()) return apiClient.post<BillResponse>('/api/v1/bills', data).then((r) => { writeBill(r.data).catch(() => {}); return r.data })
    const cached = await readOpenBills()
    const maxNum = cached.reduce((m, b) => Math.max(m, b.bill_number), 0)
    const tempId = 'offline_' + Date.now()
    const tempBill: BillResponse = {
      id: tempId, bill_number: maxNum + 1, bill_type: data.bill_type, status: 'draft',
      table_id: data.table_id ?? null, covers: data.covers ?? null,
      reference_no: data.reference_no ?? null, platform: data.platform ?? null,
      subtotal_paise: 0, discount_paise: 0, gst_paise: 0, total_paise: 0,
      payment_method: null, paid_at: null, notes: data.notes ?? null,
      created_by: 'offline', created_by_name: null, waiter_id: data.waiter_id ?? null,
      waiter_name: null, created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
      items: [], kot_tickets: [],
    }
    await enqueue('openBill', { tempId, data })
    await writeBill(tempBill)
    return tempBill
  },

  get: (id: string): Promise<BillResponse> =>
    apiClient.get<BillResponse>(`/api/v1/bills/${id}`).then((r) => { writeBill(r.data).catch(() => {}); return r.data }).catch(() => readBill(id).then((b) => { if (!b) throw new Error('Bill not cached for offline'); return b })),

  addItem: async (billId: string, data: AddItemRequest): Promise<BillItemResponse> => {
    if (offline()) {
      await enqueue('addItem', { billId, data })
      const item: BillItemResponse = { id: 'ol_item_' + Date.now(), menu_item_id: data.menu_item_id ?? null, name: data.name, category: data.category, price_paise: data.price_paise, override_price_paise: null, food_type: data.food_type ?? 'veg', quantity: data.quantity ?? 1, status: 'pending', kot_ticket_id: null, notes: data.notes ?? null }
      await optimisticAddItem(billId, item)
      return item
    }
    return apiClient.post<BillItemResponse>(`/api/v1/bills/${billId}/items`, data).then((r) => r.data)
  },

  updateItem: async (billId: string, itemId: string, data: UpdateItemRequest): Promise<BillItemResponse> => {
    if (offline()) { await enqueue('updateItem', { billId, itemId, data }); const u = await optimisticUpdateItem(billId, itemId, data); if (!u) throw new Error('Bill not in cache'); return u }
    return apiClient.patch<BillItemResponse>(`/api/v1/bills/${billId}/items/${itemId}`, data).then((r) => r.data)
  },

  removeItem: async (billId: string, itemId: string): Promise<void> => {
    if (offline()) { await enqueue('removeItem', { billId, itemId }); await optimisticRemoveItem(billId, itemId); return }
    return apiClient.delete(`/api/v1/bills/${billId}/items/${itemId}`).then(() => undefined)
  },

  fireKot: async (billId: string): Promise<KotTicketResponse> => {
    if (offline()) {
      await enqueue('fireKot', { billId })
      const pendingIds = await optimisticFireKot(billId)
      const ticket: KotTicketResponse = { id: 'ol_kot_' + Date.now(), ticket_number: Date.now(), fired_at: new Date().toISOString(), item_ids: pendingIds }
      readBill(billId).then((b) => { if (b) localPrintKot(b, pendingIds).catch(() => {}) })
      return ticket
    }
    return apiClient.post<KotTicketResponse>(`/api/v1/bills/${billId}/kot`).then((r) => r.data)
  },

  close: async (billId: string, data: CloseBillRequest): Promise<BillResponse> => {
    if (offline()) {
      await enqueue('closeBill', { billId, data })
      const cached = await readBill(billId)
      if (cached) {
        const settled: BillResponse = { ...cached, status: 'billed', payment_method: data.payment_method, discount_paise: data.discount_paise ?? 0, total_paise: Math.max(0, cached.subtotal_paise - (data.discount_paise ?? 0)) }
        await writeBill(settled)
        return settled
      }
      throw Object.assign(new Error('Queued offline'), { queued: true })
    }
    return apiClient.post<BillResponse>(`/api/v1/bills/${billId}/close`, data)
      .then((r) => { writeBill(r.data).catch(() => {}); return r.data })
  },

  void: async (billId: string): Promise<BillResponse> => { if (offline()) { await enqueue('voidBill', { billId }); throw Object.assign(new Error('Queued offline'), { queued: true }) }; return apiClient.post<BillResponse>(`/api/v1/bills/${billId}/void`).then((r) => r.data) },
  unvoid: async (billId: string): Promise<BillResponse> => { if (offline()) { await enqueue('unvoidBill', { billId }); throw Object.assign(new Error('Queued offline'), { queued: true }) }; return apiClient.post<BillResponse>(`/api/v1/bills/${billId}/unvoid`).then((r) => r.data) },
  print: (billId: string, jobType: 'receipt' | 'kot' = 'receipt'): Promise<void> =>
    apiClient.post('/api/v1/print-jobs', { bill_id: billId, job_type: jobType }).then(() => undefined),
  updatePaymentMethod: (billId: string, payment_method: PaymentMethod): Promise<BillResponse> =>
    apiClient.patch<BillResponse>(`/api/v1/bills/${billId}/payment-method`, { payment_method }).then((r) => r.data),
}
