export type BillType = 'table' | 'parcel' | 'online'
export type BillStatus = 'draft' | 'kot_sent' | 'partially_sent' | 'billed' | 'void'
export type ItemStatus = 'pending' | 'sent' | 'voided'
export type PaymentMethod = 'cash' | 'card' | 'upi' | 'online' | 'other'
export type FoodType = 'veg' | 'egg' | 'non_veg'

export interface BillItemResponse {
  id: string
  menu_item_id: string | null
  name: string
  category: string
  price_paise: number
  override_price_paise: number | null
  food_type: FoodType
  quantity: number
  status: ItemStatus
  kot_ticket_id: string | null
  notes: string | null
}

export interface KotTicketResponse {
  id: string
  ticket_number: number
  fired_at: string
  item_ids: string[]
}

export interface BillResponse {
  id: string
  bill_number: number
  bill_type: BillType
  status: BillStatus
  table_id: string | null
  covers: number | null
  reference_no: string | null
  platform: string | null
  subtotal_paise: number
  discount_paise: number
  gst_paise: number
  total_paise: number
  payment_method: PaymentMethod | null
  paid_at: string | null
  notes: string | null
  created_by: string
  created_by_name: string | null
  waiter_id: string | null
  waiter_name: string | null
  created_at: string
  updated_at: string
  items: BillItemResponse[]
  kot_tickets: KotTicketResponse[]
}

export interface BillSummaryResponse {
  id: string
  bill_number: number
  bill_type: BillType
  status: BillStatus
  table_id: string | null
  covers: number | null
  reference_no: string | null
  platform: string | null
  total_paise: number
  created_by: string
  waiter_id: string | null
  waiter_name: string | null
  item_names: string[]
  created_at: string
  updated_at: string
}

export interface OpenBillRequest {
  bill_type: BillType
  table_id?: string | null
  covers?: number | null
  reference_no?: string | null
  platform?: string | null
  notes?: string | null
  waiter_id?: string | null
}

export interface AddItemRequest {
  menu_item_id?: string | null
  name: string
  category: string
  price_paise: number
  food_type?: FoodType
  quantity?: number
  notes?: string | null
}

export interface UpdateItemRequest {
  quantity?: number
  notes?: string | null
  override_price_paise?: number | null
}

export interface CloseBillRequest {
  payment_method: PaymentMethod
  discount_paise?: number
}
