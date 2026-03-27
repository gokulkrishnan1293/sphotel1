import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { menuListWithCache } from '@/lib/db/menuCache'
import { billsApi } from '../api/bills'
import type { MenuItemResponse } from '../../admin/types/menu'
import type { BillType } from '../types/bills'
import { ItemCard, pickCardPrice } from './ItemCard'
import { recordItemOrder, getFavouriteIds } from './useFavourites'
import { VariantPicker } from './VariantPicker'

interface Props { billId: string; billType: BillType; platform?: string | null; fontSizeIdx?: number }

export function ItemGrid({ billId, billType, platform, fontSizeIdx = 2 }: Props) {
  const [tab, setTab] = useState('Favourites')
  const [variantItem, setVariantItem] = useState<MenuItemResponse | null>(null)
  const qc = useQueryClient()
  const { data: items = [] } = useQuery({ queryKey: ['menu-items'], queryFn: menuListWithCache })
  const favIds = useMemo(() => new Set(getFavouriteIds(16)), [])
  const avail = useMemo(() => items.filter((i) => i.is_available), [items])
  const categories = useMemo(() => ['Favourites', ...Array.from(new Set(avail.map((i) => i.category)))], [avail])
  const displayed = useMemo(() => {
    if (tab === 'Favourites') { const favs = avail.filter((i) => favIds.has(i.id)); return favs.length ? favs : avail.slice(0, 16) }
    return avail.filter((i) => i.category === tab)
  }, [avail, tab, favIds])

  const add = useMutation({
    mutationFn: ({ item, vName, vPrice }: { item: MenuItemResponse; vName?: string; vPrice?: number }) =>
      billsApi.addItem(billId, { menu_item_id: item.id, name: vName ? `${item.name} (${vName})` : item.name, category: item.category, price_paise: vPrice ?? pickCardPrice(item, billType, platform), food_type: item.food_type, quantity: 1 }),
    onSuccess: (_, { item }) => { recordItemOrder(item.id); qc.invalidateQueries({ queryKey: ['bill', billId] }); qc.invalidateQueries({ queryKey: ['bills', 'open'] }) },
  })

  if (variantItem) return (
    <div className="flex-1 overflow-y-auto border-t border-sphotel-border">
      <VariantPicker item={variantItem} qty={1} billType={billType}
        onSelect={(n, p) => { add.mutate({ item: variantItem, vName: n, vPrice: p }); setVariantItem(null) }}
        onBack={() => setVariantItem(null)} />
    </div>
  )

  return (
    <div className="flex flex-col flex-1 min-h-0">
      <div className="flex gap-1 px-3 py-2 overflow-x-auto shrink-0 border-b border-sphotel-border">
        {categories.map((c) => (
          <button key={c} onClick={() => setTab(c)}
            className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${tab === c ? 'bg-sphotel-accent text-sphotel-accent-fg' : 'bg-bg-elevated text-text-muted hover:text-text-primary'}`}>
            {c}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-y-auto p-3 grid grid-cols-3 xl:grid-cols-4 gap-2 content-start">
        {displayed.map((item) => (
          <ItemCard key={item.id} item={item} billType={billType} platform={platform} fontSizeIdx={fontSizeIdx}
            onClick={() => item.variants?.length ? setVariantItem(item) : add.mutate({ item })} />
        ))}
        {displayed.length === 0 && tab === 'Favourites' && (
          <p className="col-span-full text-xs text-text-muted text-center py-8">Start adding items to build your favourites</p>
        )}
      </div>
    </div>
  )
}
