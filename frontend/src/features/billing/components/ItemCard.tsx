import type { MenuItemResponse } from '../../admin/types/menu'
import type { BillType } from '../types/bills'

const FOOD_DOT: Record<string, string> = { veg: 'bg-emerald-500', egg: 'bg-yellow-400', non_veg: 'bg-red-500' }
const FONT_SIZES = [12, 13, 14, 15, 16, 18, 20, 22, 24]

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
  fontSizeIdx?: number
  onClick: () => void
}

export function ItemCard({ item, billType, platform, fontSizeIdx = 2, onClick }: Props) {
  const fs = FONT_SIZES[fontSizeIdx] ?? 14
  const pad = Math.round(fs * 0.85)
  const dotSize = Math.max(7, Math.round(fs * 0.55))
  const price = item.variants?.length
    ? `from ₹${Math.min(...item.variants.map((v) => pickCardPrice(v, billType, platform))) / 100}`
    : `₹${(pickCardPrice(item, billType, platform) / 100).toFixed(0)}`
  return (
    <button onClick={onClick} style={{ padding: pad, fontSize: fs }}
      className="flex flex-col items-start bg-bg-elevated border border-sphotel-border rounded-lg hover:border-sphotel-accent hover:bg-sphotel-accent-subtle transition-colors text-left w-full min-w-0">
      <div className="flex items-center gap-1.5 w-full min-w-0">
        <span className={`rounded-full shrink-0 ${FOOD_DOT[item.food_type] ?? 'bg-gray-400'}`} style={{ width: dotSize, height: dotSize }} />
        <span className="text-text-primary truncate leading-tight">{item.name}</span>
      </div>
      <span className="font-medium text-sphotel-accent mt-1" style={{ fontSize: Math.max(10, fs - 2) }}>{price}</span>
    </button>
  )
}
