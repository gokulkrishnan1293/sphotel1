export type StaffRole = 'waiter' | 'biller' | 'kitchen_staff' | 'manager' | 'admin' | 'super_admin'

export interface StaffResponse {
  id: string
  tenant_id: string
  name: string
  role: StaffRole
  short_code: number | null
  is_active: boolean
  created_at: string
}

export interface CreateStaffRequest {
  name: string
  role: StaffRole
  pin: string
  short_code?: number | null
}

export interface UpdateStaffRequest {
  name?: string
  role?: StaffRole
  is_active?: boolean
  short_code?: number | null
}

export interface ResetPinRequest {
  pin: string
}

export interface WaiterView {
  id: string
  name: string
  short_code: number | null
}

export interface CreateAdminRequest {
  tenant_slug: string
  name: string
  email: string
  password: string
}

export interface AdminCreatedResponse extends StaffResponse {
  totp_uri: string
}
