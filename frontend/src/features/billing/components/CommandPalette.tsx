import { useState, useEffect, useRef, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search } from 'lucide-react'
import { menuApi } from '../../admin/api/menu'
import { billsApi } from '../api/bills'
import { useBillingStore } from '../stores/billingStore'
import type { MenuItemResponse } from '../../admin/types/menu'
import type { BillType } from '../types/bills'
import { VariantPicker } from './VariantPicker'

const FOOD_DOT: Record<string, string> = { veg: 'bg-emerald-500', egg: 'bg-yellow-400', non_veg: 'bg-red-500' }

type PriceItem = { price_paise: number; parcel_price_paise?: number | null; vendor_prices?: { vendor_slug: string; price_paise: number }[] }
function pickPrice(it: PriceItem, bt: BillType, pl?: string | null): number {
  if (bt === 'parcel' && it.parcel_price_paise) return it.parcel_price_paise
  if (bt === 'online' && pl) { const vp = it.vendor_prices?.find((v) => v.vendor_slug === pl); if (vp) return vp.price_paise }
  return it.price_paise
}
const dispPrice = (it: MenuItemResponse, bt: BillType, pl?: string | null) =>
  it.variants?.length ? 'from ₹' + Math.min(...it.variants.map((v) => pickPrice(v, bt, pl))) / 100 : `₹${(pickPrice(it, bt, pl) / 100).toFixed(0)}`

const isBatch = (q: string) => { const p = q.trim().split(/\s+/); return p.length >= 2 && p.every((t) => /^\d+$/.test(t)) }

function parse(q: string): { qty: number; searchQuery: string } {
  if (isBatch(q)) { const p = q.trim().split(/\s+/); const codes = p.filter((_, i) => i % 2 === 0); const qtys = p.filter((_, i) => i % 2 === 1); return { qty: Number(qtys[qtys.length - 1] ?? 1), searchQuery: codes[codes.length - 1] ?? '' } }
  const parts = q.trim().split(/\s+/)
  if (parts.length >= 2) { const last = parts[parts.length - 1]; const qty = Number(last); if (/^\d+$/.test(last) && qty >= 1 && qty <= 20) return { qty, searchQuery: parts.slice(0, -1).join(' ') } }
  return { qty: 1, searchQuery: q.trim() }
}

function buildQueue(q: string, items: MenuItemResponse[]) {
  if (!isBatch(q)) return null
  const p = q.trim().split(/\s+/); const out: Array<{ item: MenuItemResponse; qty: number }> = []
  for (let i = 0; i + 1 < p.length; i += 2) { const qty = Number(p[i + 1]); if (!qty || qty > 99) continue; const found = items.find((it) => it.is_available && String(it.short_code) === p[i]); if (found) out.push({ item: found, qty }) }
  return out.length ? out : null
}

export function CommandPalette({ billId, billType, platform }: { billId: string; billType: BillType; platform?: string | null }) {
  const qc = useQueryClient(); const { closeCommandPalette } = useBillingStore()
  const [query, setQuery] = useState(''); const [idx, setIdx] = useState(0)
  const [variantItem, setVariantItem] = useState<MenuItemResponse | null>(null); const [variantQty, setVariantQty] = useState(1)
  const [queue, setQueue] = useState<Array<{ item: MenuItemResponse; qty: number }>>([])
  const inputRef = useRef<HTMLInputElement>(null)
  const { qty, searchQuery } = useMemo(() => parse(query), [query])
  const { data: items = [] } = useQuery({ queryKey: ['menu-items'], queryFn: menuApi.list })
  const filtered = useMemo(() => {
    const avail = items.filter((i) => i.is_available); if (!searchQuery.trim()) return avail.slice(0, 20)
    const q = searchQuery.toLowerCase()
    return avail.filter((i) => i.name.toLowerCase().includes(q) || i.category.toLowerCase().includes(q) || String(i.short_code ?? '').includes(q))
  }, [items, searchQuery])
  const add = useMutation({
    mutationFn: ({ item, vName, vPrice, qtyOverride }: { item: MenuItemResponse; vName?: string; vPrice?: number; qtyOverride?: number }) =>
      billsApi.addItem(billId, { menu_item_id: item.id, name: vName ? `${item.name} (${vName})` : item.name, category: item.category, price_paise: vPrice ?? pickPrice(item, billType, platform), food_type: item.food_type as 'veg' | 'egg' | 'non_veg', quantity: qtyOverride ?? qty }),
    onSuccess: (_, vars) => { qc.invalidateQueries({ queryKey: ['bill', billId] }); qc.invalidateQueries({ queryKey: ['bills', 'open'] }); setQuery(''); if (vars.vName != null) setVariantItem(null); inputRef.current?.focus() },
  })
  useEffect(() => { inputRef.current?.focus() }, []) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { setIdx(0) }, [filtered]) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { if (!queue.length) return; const [next, ...rest] = queue; if (next.item.variants?.length) { setVariantItem(next.item); setVariantQty(next.qty); setQueue(rest) } else { add.mutate({ item: next.item, qtyOverride: next.qty }); setQueue(rest) } }, [queue]) // eslint-disable-line react-hooks/exhaustive-deps
  function onKey(e: React.KeyboardEvent) {
    if (e.key === 'ArrowDown') { e.preventDefault(); setIdx((i) => Math.min(i + 1, filtered.length - 1)) }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setIdx((i) => Math.max(i - 1, 0)) }
    else if (e.key === 'Enter') {
      if (isBatch(query)) { const batch = buildQueue(query, items); if (batch) { setQueue(batch); setQuery(''); return } }
      const item = filtered[idx]; if (item) { if (item.variants?.length) { setVariantItem(item); setVariantQty(qty) } else add.mutate({ item, vPrice: pickPrice(item, billType, platform) }) }
    } else if (e.key === 'Escape') closeCommandPalette()
  }
  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-start pt-16 px-4">
      <div className="absolute inset-0 bg-black/60" onClick={closeCommandPalette} />
      <div className="relative w-full max-w-2xl bg-bg-elevated border border-sphotel-border rounded-2xl shadow-2xl overflow-hidden">
        {variantItem ? (
          <VariantPicker item={variantItem} qty={variantQty} billType={billType} onSelect={(n, p) => add.mutate({ item: variantItem, vName: n, vPrice: p, qtyOverride: variantQty })} onBack={() => setVariantItem(null)} />
        ) : (<>
          <div className="flex items-center gap-3 px-4 py-3 border-b border-sphotel-border">
            <Search size={16} className="text-text-muted shrink-0" />
            <input ref={inputRef} value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={onKey} placeholder="Search menu… or 412 2 453 2" className="flex-1 bg-transparent text-sm text-text-primary placeholder-text-muted outline-none" />
            {qty > 1 && <span className="text-xs bg-sphotel-accent-subtle text-sphotel-accent px-2 py-0.5 rounded-full font-medium">×{qty}</span>}
          </div>
          <div className="max-h-96 overflow-y-auto">
            {filtered.length === 0 ? <p className="text-sm text-text-muted text-center py-6">No items found</p>
              : filtered.map((item, i) => (
                <button key={item.id} onClick={() => item.variants?.length ? (setVariantItem(item), setVariantQty(qty)) : add.mutate({ item, vPrice: pickPrice(item, billType, platform) })}
                  className={`w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors ${i === idx ? 'bg-sphotel-accent-subtle' : 'hover:bg-bg-base'}`}>
                  <span className={`w-2 h-2 rounded-full shrink-0 ${FOOD_DOT[item.food_type]}`} />
                  <div className="flex-1 min-w-0"><span className="text-sm text-text-primary">{item.name}</span><span className="text-xs text-text-muted ml-2">{item.category}</span></div>
                  {item.short_code && <span className="text-xs text-text-muted font-mono">#{item.short_code}</span>}
                  <span className="text-sm font-medium text-text-primary shrink-0">{dispPrice(item, billType, platform)}</span>
                </button>
              ))}
          </div>
          <div className="px-4 py-2 border-t border-sphotel-border flex items-center gap-4 text-xs text-text-muted">
            <span>↑↓ navigate</span><span>Enter add</span><span>Esc close</span>
            {isBatch(query) && <span className="text-sphotel-accent">Batch mode — Enter to add all</span>}
          </div>
        </>)}
      </div>
    </div>
  )
}
