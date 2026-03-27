import { useState, useEffect, useRef, useMemo, useImperativeHandle, forwardRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search } from 'lucide-react'
import { menuListWithCache } from '@/lib/db/menuCache'
import { billsApi } from '../api/bills'
import { recordItemOrder } from './useFavourites'
import type { MenuItemResponse } from '../../admin/types/menu'
import type { BillType } from '../types/bills'
import { VariantPicker } from './VariantPicker'
import { pickPrice, isBatch, parse, buildQueue } from './searchHelpers'
import { SearchResultsDropdown } from './SearchResultsDropdown'

export type InlineSearchHandle = { focus: () => void }
export const InlineSearch = forwardRef<InlineSearchHandle, { billId: string; billType: BillType; platform?: string | null; onGenerateBill: () => void }>(
  function InlineSearch({ billId, billType, platform }, ref) {
    const qc = useQueryClient()
    const [query, setQuery] = useState('')
    const [idx, setIdx] = useState(0)
    const [showResults, setShowResults] = useState(false)
    const [variantItem, setVariantItem] = useState<MenuItemResponse | null>(null)
    const [variantQty, setVariantQty] = useState(1)
    const [queue, setQueue] = useState<Array<{ item: MenuItemResponse; qty: number }>>([])
    const inputRef = useRef<HTMLInputElement>(null); const containerRef = useRef<HTMLDivElement>(null)
    const [dropdownStyle, setDropdownStyle] = useState({ top: 0, left: 0, width: 0 })

    useImperativeHandle(ref, () => ({ focus: () => { inputRef.current?.focus() } }))

    const { qty, searchQuery } = useMemo(() => parse(query), [query])
    const { data: items = [] } = useQuery({ queryKey: ['menu-items'], queryFn: menuListWithCache })

    const filtered = useMemo(() => {
      const avail = items.filter((i) => i.is_available)
      if (!searchQuery.trim()) return avail.slice(0, 20)
      const q = searchQuery.toLowerCase()
      const matches = avail.filter((i) => i.name.toLowerCase().includes(q) || i.category.toLowerCase().includes(q) || String(i.short_code ?? '').includes(q))
      const score = (i: MenuItemResponse) => { const code = String(i.short_code ?? ''); const name = i.name.toLowerCase(); if (code === q) return 0; if (code.startsWith(q)) return 1; if (code.includes(q)) return 2; if (name.startsWith(q)) return 3; return 4 }
      return matches.sort((a, b) => score(a) - score(b))
    }, [items, searchQuery])

    const add = useMutation({
      mutationFn: ({ item, vName, vPrice, qtyOverride }: { item: MenuItemResponse; vName?: string; vPrice?: number; qtyOverride?: number }) =>
        billsApi.addItem(billId, { menu_item_id: item.id, name: vName ? `${item.name} (${vName})` : item.name, category: item.category, price_paise: vPrice ?? pickPrice(item, billType, platform), food_type: item.food_type as 'veg' | 'egg' | 'non_veg', quantity: qtyOverride ?? qty }),
      onSuccess: (_, vars) => { recordItemOrder(vars.item.id); qc.invalidateQueries({ queryKey: ['bill', billId] }); qc.invalidateQueries({ queryKey: ['bills', 'open'] }); setQuery(''); setShowResults(false); if (vars.vName != null) setVariantItem(null); inputRef.current?.focus() },
    })

    useEffect(() => { inputRef.current?.focus() }, []) // eslint-disable-line
    useEffect(() => { setIdx(0) }, [filtered]) // eslint-disable-line
    useEffect(() => {
      if (!queue.length || variantItem) return
      const [next, ...rest] = queue
      if (next.item.variants?.length) { setVariantItem(next.item); setVariantQty(next.qty); setQueue(rest) }
      else { add.mutate({ item: next.item, qtyOverride: next.qty }); setQueue(rest) }
    }, [queue, variantItem]) // eslint-disable-line react-hooks/exhaustive-deps
    useEffect(() => {
      if (showResults && containerRef.current) { const r = containerRef.current.getBoundingClientRect(); setDropdownStyle({ top: r.bottom, left: r.left, width: r.width }) }
    }, [showResults, query])

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

    if (variantItem) return (
      <div className="px-3 md:px-6 py-3 border-b border-sphotel-border">
        <VariantPicker item={variantItem} qty={variantQty} billType={billType}
          onSelect={(n, p) => add.mutate({ item: variantItem, vName: n, vPrice: p, qtyOverride: variantQty })}
          onBack={() => setVariantItem(null)} />
      </div>
    )

    return (
      <div ref={containerRef} className="px-3 md:px-6 border-b border-sphotel-border">
        <div className="flex items-center gap-2 py-3 md:py-2">
          <Search size={14} className="text-text-muted shrink-0" />
          <input ref={inputRef} value={query}
            onChange={(e) => { setQuery(e.target.value); setShowResults(true) }}
            onFocus={() => { if (query.length > 0) setShowResults(true) }}
            onBlur={() => setTimeout(() => setShowResults(false), 150)}
            onKeyDown={onKey}
            placeholder="Search items… or 412 2 453 1 (batch)"
            className="flex-1 bg-transparent text-sm text-text-primary placeholder-text-muted outline-none py-1" />
          {qty > 1 && <span className="text-xs bg-sphotel-accent-subtle text-sphotel-accent px-2 py-0.5 rounded-full font-medium shrink-0">×{qty}</span>}
          <span className="hidden md:inline text-xs text-text-muted shrink-0 select-none">F8 close · G bill dialog</span>
          {isBatch(query) && <span className="text-xs text-sphotel-accent shrink-0">batch</span>}
        </div>
        {showResults && filtered.length > 0 && <SearchResultsDropdown items={filtered} activeIdx={idx} style={dropdownStyle} billType={billType} platform={platform} onSelect={addItem} />}
      </div>
    )
  }
)
