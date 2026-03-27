import type { MenuItemResponse } from '../../admin/types/menu'
import type { BillType } from '../types/bills'

type PriceItem = { price_paise: number; parcel_price_paise?: number | null; vendor_prices?: { vendor_slug: string; price_paise: number }[] }

export function pickPrice(it: PriceItem, bt: BillType, pl?: string | null): number {
  if (bt === 'parcel' && it.parcel_price_paise) return it.parcel_price_paise
  if (bt === 'online' && pl) { const vp = it.vendor_prices?.find((v) => v.vendor_slug === pl); if (vp) return vp.price_paise }
  return it.price_paise
}

export const dispPrice = (it: MenuItemResponse, bt: BillType, pl?: string | null) =>
  it.variants?.length ? 'from ₹' + Math.min(...it.variants.map((v) => pickPrice(v, bt, pl))) / 100 : `₹${(pickPrice(it, bt, pl) / 100).toFixed(0)}`

export const isBatch = (q: string) => { const p = q.trim().split(/\s+/); return p.length >= 2 && p.every((t) => /^\d+$/.test(t)) }

export function parse(q: string): { qty: number; searchQuery: string } {
  if (isBatch(q)) { const p = q.trim().split(/\s+/); const codes = p.filter((_, i) => i % 2 === 0); const qtys = p.filter((_, i) => i % 2 === 1); return { qty: Number(qtys[qtys.length - 1] ?? 1), searchQuery: codes[codes.length - 1] ?? '' } }
  const parts = q.trim().split(/\s+/)
  if (parts.length >= 2) { const last = parts[parts.length - 1]; const qty = Number(last); if (/^\d+$/.test(last) && qty >= 1 && qty <= 20) return { qty, searchQuery: parts.slice(0, -1).join(' ') } }
  return { qty: 1, searchQuery: q.trim() }
}

export function buildQueue(q: string, items: MenuItemResponse[]) {
  if (!isBatch(q)) return null
  const p = q.trim().split(/\s+/); const out: Array<{ item: MenuItemResponse; qty: number }> = []
  for (let i = 0; i + 1 < p.length; i += 2) { const qty = Number(p[i + 1]); if (!qty || qty > 99) continue; const found = items.find((it) => it.is_available && String(it.short_code) === p[i]); if (found) out.push({ item: found, qty }) }
  return out.length ? out : null
}
