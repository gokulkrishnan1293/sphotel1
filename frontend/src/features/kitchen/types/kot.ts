export type FoodType = 'veg' | 'egg' | 'non_veg'

export interface KotItem {
  item_id: string
  name: string
  quantity: number
  food_type: FoodType
}

export interface ActiveKot {
  id: string
  ticket_number: number
  fired_at: string
  bill_id: string
  bill_label: string
  items: KotItem[]
  ready_item_ids: string[]
}
