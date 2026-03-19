import { apiClient } from '../../../lib/api'
import type {
  AdminCreatedResponse,
  CreateAdminRequest,
  CreateStaffRequest,
  ResetPinRequest,
  StaffResponse,
  UpdateStaffRequest,
  WaiterView,
} from '../types/staff'

export const staffApi = {
  list: (): Promise<StaffResponse[]> =>
    apiClient.get<StaffResponse[]>('/api/v1/staff').then((r) => r.data),

  listWaiters: (): Promise<WaiterView[]> =>
    apiClient.get<WaiterView[]>('/api/v1/staff/waiters').then((r) => r.data),

  create: (data: CreateStaffRequest): Promise<StaffResponse> =>
    apiClient.post<StaffResponse>('/api/v1/staff', data).then((r) => r.data),

  update: (id: string, data: UpdateStaffRequest): Promise<StaffResponse> =>
    apiClient.patch<StaffResponse>(`/api/v1/staff/${id}`, data).then((r) => r.data),

  resetPin: (id: string, data: ResetPinRequest): Promise<StaffResponse> =>
    apiClient.patch<StaffResponse>(`/api/v1/staff/${id}/pin`, data).then((r) => r.data),

  deactivate: (id: string): Promise<StaffResponse> =>
    apiClient.patch<StaffResponse>(`/api/v1/staff/${id}/deactivate`).then((r) => r.data),

  delete: (id: string): Promise<void> =>
    apiClient.delete(`/api/v1/staff/${id}`).then(() => undefined),

  createAdmin: (data: CreateAdminRequest): Promise<AdminCreatedResponse> =>
    apiClient.post<AdminCreatedResponse>('/api/v1/staff/admin', data).then((r) => r.data),
}
