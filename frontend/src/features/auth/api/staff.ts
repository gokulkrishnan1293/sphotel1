import { apiClient } from '../../../lib/api'

export type UserRole =
  | 'biller'
  | 'waiter'
  | 'kitchen_staff'
  | 'manager'
  | 'admin'
  | 'super_admin'

export interface StaffMember {
  id: string
  tenant_id: string
  name: string
  role: UserRole
  is_active: boolean
  created_at: string
}

export interface CreateStaffPayload {
  name: string
  role: UserRole
  pin: string
}

export interface ResetPinPayload {
  pin: string
}

export const staffApi = {
  list: (): Promise<StaffMember[]> =>
    apiClient.get<StaffMember[]>('/api/v1/staff').then((r) => r.data),

  create: (payload: CreateStaffPayload): Promise<StaffMember> =>
    apiClient.post<StaffMember>('/api/v1/staff', payload).then((r) => r.data),

  resetPin: (id: string, payload: ResetPinPayload): Promise<StaffMember> =>
    apiClient
      .patch<StaffMember>(`/api/v1/staff/${id}/pin`, payload)
      .then((r) => r.data),

  deactivate: (id: string): Promise<StaffMember> =>
    apiClient
      .patch<StaffMember>(`/api/v1/staff/${id}/deactivate`)
      .then((r) => r.data),

  revokeSessions: (id: string): Promise<{ message: string }> =>
    apiClient
      .delete<{ message: string }>(`/api/v1/staff/${id}/sessions`)
      .then((r) => r.data),
}
