export interface DailySummary {
  date: string
  bill_count: number
  total_paise: number
  avg_paise: number
  discount_paise: number
  void_count: number
  payment_breakdown: Record<string, number>
  top_items: { name: string; qty: number }[]
}

export interface HeatmapCell { dow: number; hour: number; total_paise: number; count: number }

export interface VelocityItem {
  name: string
  this_week: number
  last_week: number
  change_pct: number | null
}

export interface TableTurn { table_name: string; turn_count: number; avg_minutes: number }

export interface WaiterPerf { waiter_name: string; bill_count: number; revenue_paise: number }
export interface CustomQueryRow { label: string; value: number }
