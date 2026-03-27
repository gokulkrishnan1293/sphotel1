import { useState, useEffect, useRef, useMemo, useImperativeHandle, forwardRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search } from 'lucide-react'
import { menuListWithCache } from '@/lib/db/menuCache'
import { billsApi } from '../api/bills'
import { recordItemOrder } from './useFavourites'
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

export type InlineSearchHandle = { focus: () => void }

interface Props {
  billId: string
  billType: BillType
  platform?: string | null
  onGenerateBill: () => void
}

export const InlineSearch = forwardRef<InlineSearchHandle, Props>(
  function InlineSearch({ billId, billType, platform, onGenerateBill }, ref) {
    const qc = useQueryClient()
    const [query, setQuery] = useState('')
    const [idx, setIdx] = useState(0)
    const [showResults, setShowResults] = useState(false)
    const [variantItem, setVariantItem] = useState<MenuItemResponse | null>(null)
    const [variantQty, setVariantQty] = useState(1)
    const [queue, setQueue] = useState<Array<{ item: MenuItemResponse; qty: number }>>([])
    const inputRef = useRef<HTMLInputElement>(null)

    useImperativeHandle(ref, () => ({ focus: () => { inputRef.current?.focus() } }))

    const { qty, searchQuery } = useMemo(() => parse(query), [query])
    const { data: items = [] } = useQuery({ queryKey: ['menu-items'], queryFn: menuListWithCache })

    const filtered = useMemo(() => {
      const avail = items.filter((i) => i.is_available)
      if (!searchQuery.trim()) return avail.slice(0, 20)
      const q = searchQuery.toLowerCase()
      const matches = avail.filter((i) => i.name.toLowerCase().includes(q) || i.category.toLowerCase().includes(q) || String(i.short_code ?? '').includes(q))
      const score = (i: MenuItemResponse) => {
        const code = String(i.short_code ?? ''); const name = i.name.toLowerCase()
        if (code === q) return 0
        if (code.startsWith(q)) return 1
        if (code.includes(q)) return 2
        if (name.startsWith(q)) return 3
        return 4
      }
      return matches.sort((a, b) => score(a) - score(b))
    }, [items, searchQuery])

    const add = useMutation({
      mutationFn: ({ item, vName, vPrice, qtyOverride }: { item: MenuItemResponse; vName?: string; vPrice?: number; qtyOverride?: number }) =>
        billsApi.addItem(billId, { menu_item_id: item.id, name: vName ? `${item.name} (${vName})` : item.name, category: item.category, price_paise: vPrice ?? pickPrice(item, billType, platform), food_type: item.food_type as 'veg' | 'egg' | 'non_veg', quantity: qtyOverride ?? qty }),
      onSuccess: (_, vars) => { recordItemOrder(vars.item.id); qc.invalidateQueries({ queryKey: ['bill', billId] }); qc.invalidateQueries({ queryKey: ['bills', 'open'] }); setQuery(''); setShowResults(false); if (vars.vName != null) setVariantItem(null); inputRef.current?.focus() },
    })

    useEffect(() => { inputRef.current?.focus() }, []) // eslint-disable-line react-hooks/exhaustive-deps
    useEffect(() => { setIdx(0) }, [filtered]) // eslint-disable-line react-hooks/exhaustive-deps
    useEffect(() => {
      if (!queue.length || variantItem) return
      const [next, ...rest] = queue
      if (next.item.variants?.length) { setVariantItem(next.item); setVariantQty(next.qty); setQueue(rest) }
      else { add.mutate({ item: next.item, qtyOverride: next.qty }); setQueue(rest) }
    }, [queue, variantItem]) // eslint-disable-line react-hooks/exhaustive-deps

    function addItem(item: MenuItemResponse) {
      if (item.variants?.length) { setVariantItem(item); setVariantQty(qty) }
      else add.mutate({ item, vPrice: pickPrice(item, billType, platform) })
    }

    function onKey(e: React.KeyboardEvent) {
      if (e.key === 'ArrowDown') { e.preventDefault(); setIdx((i) => Math.min(i + 1, filtered.length - 1)) }
      else if (e.key === 'ArrowUp') { e.preventDefault(); setIdx((i) => Math.max(i - 1, 0)) }
      else if (e.key === 'Enter') {
        if (isBatch(query)) { const batch = buildQueue(query, items); if (batch) { setQueue(batch); setQuery(''); return } }
        const item = filtered[idx]; if (item) addItem(item)
      }
    }

    if (variantItem) {
      return (
        <div className="px-3 md:px-6 py-3 border-b border-sphotel-border">
          <VariantPicker item={variantItem} qty={variantQty} billType={billType}
            onSelect={(n, p) => add.mutate({ item: variantItem, vName: n, vPrice: p, qtyOverride: variantQty })}
            onBack={() => setVariantItem(null)} />
        </div>
      )
    }

    return (
      <div className="px-3 md:px-6 border-b border-sphotel-border relative">
        <div className="flex items-center gap-2 py-3 md:py-2">
          <Search size={14} className="text-text-muted shrink-0" />
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => { setQuery(e.target.value); setShowResults(true) }}
            onFocus={() => { if (query.length > 0) setShowResults(true) }}
            onBlur={() => setTimeout(() => setShowResults(false), 150)}
            onKeyDown={onKey}
            placeholder="Search items… or 412 2 453 1 (batch)"
            className="flex-1 bg-transparent text-sm text-text-primary placeholder-text-muted outline-none py-1"
          />
          {qty > 1 && <span className="text-xs bg-sphotel-accent-subtle text-sphotel-accent px-2 py-0.5 rounded-full font-medium shrink-0">×{qty}</span>}
          <span className="hidden md:inline text-xs text-text-muted shrink-0 select-none">F8 close · G bill dialog</span>
          {isBatch(query) && <span className="text-xs text-sphotel-accent shrink-0">batch</span>}
        </div>
        {showResults && filtered.length > 0 && (
          <div className="absolute left-0 right-0 top-full bg-bg-elevated border border-sphotel-border border-t-0 rounded-b-xl shadow-xl z-10 max-h-64 overflow-y-auto">
            {filtered.map((item, i) => (
              <button key={item.id} onMouseDown={() => addItem(item)}
                className={`w-full flex items-center gap-3 px-4 py-2 text-left transition-colors ${i === idx ? 'bg-sphotel-accent-subtle' : 'hover:bg-bg-base'}`}>
                <span className={`w-2 h-2 rounded-full shrink-0 ${FOOD_DOT[item.food_type]}`} />
                <div className="flex-1 min-w-0">
                  <span className="text-sm text-text-primary">{item.name}</span>
                  <span className="text-xs text-text-muted ml-2">{item.category}</span>
                </div>
                {item.short_code && <span className="text-xs text-text-muted font-mono">#{item.short_code}</span>}
                <span className="text-sm font-medium text-text-primary shrink-0">{dispPrice(item, billType, platform)}</span>
              </button>
            ))}
            <div className="hidden md:flex px-4 py-1.5 border-t border-sphotel-border text-xs text-text-muted gap-4">
              <span>↑↓ navigate</span><span>Enter add</span><span>F8 close · G bill dialog</span>
            </div>
          </div>
        )}
      </div>
    )
  }
)
