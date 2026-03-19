export type FoodType = 'veg' | 'egg' | 'non_veg'

export interface VendorPrice {
  vendor_slug: string
  price_paise: number
}

export interface MenuVariant {
  id?: string
  name: string
  price_paise: number
  parcel_price_paise?: number | null
  vendor_prices?: VendorPrice[]
}

export interface MenuItemResponse {
  id: string
  tenant_id: string
  name: string
  category: string
  short_code: number | null
  price_paise: number
  online_price_paise?: number | null
  parcel_price_paise?: number | null
  food_type: FoodType
  description: string | null
  is_available: boolean
  display_order: number
  variants?: MenuVariant[]
  vendor_prices?: VendorPrice[]
}

export interface MenuItemCreate {
  name: string
  category: string
  short_code?: number | null
  price_paise: number
  parcel_price_paise?: number | null
  food_type: FoodType
  description?: string | null
  is_available?: boolean
  display_order?: number
  variants?: MenuVariant[]
  vendor_prices?: VendorPrice[]
}

export type MenuItemUpdate = Partial<MenuItemCreate>

export interface CategoryResponse {
  name: string
  item_count: number
}

export interface CategoryRename {
  new_name: string
}
