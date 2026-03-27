import type { MenuItemResponse } from '../../admin/types/menu'
import type { BillType } from '../types/bills'

const FOOD_DOT: Record<string, string> = { veg: 'bg-emerald-500', egg: 'bg-yellow-400', non_veg: 'bg-red-500' }

type PriceCtx = { price_paise: number; parcel_price_paise?: number | null; vendor_prices?: { vendor_slug: string; price_paise: number }[] }

export function pickCardPrice(it: PriceCtx, bt: BillType, pl?: string | null): number {
  if (bt === 'parcel' && it.parcel_price_paise) return it.parcel_price_paise
  if (bt === 'online' && pl) { const vp = it.vendor_prices?.find((v) => v.vendor_slug === pl); if (vp) return vp.price_paise }
  return it.price_paise
}

interface Props {
  item: MenuItemResponse
  billType: BillType
  platform?: string | null
  onClick: () => void
}

export function ItemCard({ item, billType, platform, onClick }: Props) {
  const price = item.variants?.length
    ? `from ₹${Math.min(...item.variants.map((v) => pickCardPrice(v, billType, platform))) / 100}`
    : `₹${(pickCardPrice(item, billType, platform) / 100).toFixed(0)}`
  return (
    <button
      onClick={onClick}
      className="flex flex-col items-start p-2.5 bg-bg-elevated border border-sphotel-border rounded-lg hover:border-sphotel-accent hover:bg-sphotel-accent-subtle transition-colors text-left w-full min-w-0"
    >
      <div className="flex items-center gap-1.5 w-full min-w-0">
        <span className={`w-2 h-2 rounded-full shrink-0 ${FOOD_DOT[item.food_type] ?? 'bg-gray-400'}`} />
        <span className="text-sm text-text-primary truncate leading-tight">{item.name}</span>
      </div>
      <span className="text-xs font-medium text-sphotel-accent mt-1">{price}</span>
    </button>
  )
}
