import { useState } from 'react'
import type { MenuItemCreate, MenuItemResponse, MenuItemUpdate, MenuVariant, VendorPrice } from '../types/menu'
import type { VendorItem } from '../../settings/api/onlineVendors'
import { Switch } from '@/shared/components/ui/switch'
import { VariantsModal } from './VariantsModal'
import { ChevronRight } from 'lucide-react'

interface Props {
  item?: MenuItemResponse; existingCategories: string[]; vendors: VendorItem[]
  onSubmit: (data: MenuItemCreate | MenuItemUpdate) => void; onCancel: () => void; isLoading: boolean
}

const FT = [{ value: 'veg', label: 'Veg' }, { value: 'egg', label: 'Egg' }, { value: 'non_veg', label: 'Non-Veg' }] as const
const INPUT = 'bg-bg-elevated border border-sphotel-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent w-full'
const ERR = 'text-status-error text-xs'
const r = (p?: number | null) => (p != null && p > 0 ? String(p / 100) : '')
const p = (s: string) => (s.trim() ? Math.round(Number(s.trim()) * 100) : null)

export function MenuItemForm({ item, existingCategories, vendors, onSubmit, onCancel, isLoading }: Props) {
  const isEdit = !!item
  const [name, setName] = useState(item?.name ?? '')
  const [category, setCategory] = useState(item?.category ?? '')
  const [shortCode, setSC] = useState(item?.short_code != null ? String(item.short_code) : '')
  const [price, setPrice] = useState(item != null ? String(item.price_paise / 100) : '')
  const [parcel, setParcel] = useState(r(item?.parcel_price_paise))
  const [vprices, setVprices] = useState<Record<string, string>>(() =>
    Object.fromEntries(vendors.map((v) => [v.slug, r(item?.vendor_prices?.find((x) => x.vendor_slug === v.slug)?.price_paise)])))
  const [foodType, setFoodType] = useState<'veg' | 'egg' | 'non_veg'>(item?.food_type ?? 'veg')
  const [isAvailable, setIsAvailable] = useState(item?.is_available ?? true)
  const [variants, setVariants] = useState<MenuVariant[]>(item?.variants ?? [])
  const [showVariants, setShowVariants] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  function validate() {
    const e: Record<string, string> = {}
    if (!name.trim()) e.name = 'Name is required'
    if (!category.trim()) e.category = 'Category is required'
    const sc = shortCode.trim()
    if (sc !== '') { const n = Number(sc); if (!Number.isInteger(n) || n < 1 || n > 9999) e.short_code = 'Must be 1–9999' }
    if (price.trim() === '' || isNaN(Number(price.trim())) || Number(price.trim()) < 0) e.price = 'Enter a valid price'
    setErrors(e); return Object.keys(e).length === 0
  }

  function handleSubmit(ev: React.FormEvent) {
    ev.preventDefault(); if (!validate()) return
    const vps: VendorPrice[] = vendors.filter((v) => vprices[v.slug]?.trim()).map((v) => ({ vendor_slug: v.slug, price_paise: Math.round(Number(vprices[v.slug]) * 100) }))
    onSubmit({ name: name.trim(), category: category.trim(), short_code: shortCode.trim() ? Number(shortCode.trim()) : null, price_paise: Math.round(Number(price.trim()) * 100), parcel_price_paise: p(parcel), food_type: foodType, is_available: isAvailable, variants: variants.filter((v) => v.name.trim()), vendor_prices: vps })
  }

  return (
    <>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <h2 className="font-semibold text-text-primary">{isEdit ? 'Edit Item' : 'Add Item'}</h2>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-text-secondary font-medium">Name *</label>
          <input className={INPUT} value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Chicken Biryani" maxLength={200} />
          {errors.name && <span className={ERR}>{errors.name}</span>}
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-text-secondary font-medium">Category *</label>
          <input className={INPUT} list="cat-list" value={category} onChange={(e) => setCategory(e.target.value)} placeholder="e.g. Biryani" maxLength={100} />
          <datalist id="cat-list">{existingCategories.map((c) => <option key={c} value={c} />)}</datalist>
          {errors.category && <span className={ERR}>{errors.category}</span>}
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-text-secondary font-medium">Short Code</label>
            <input className={INPUT} value={shortCode} onChange={(e) => setSC(e.target.value)} placeholder="e.g. 97" inputMode="numeric" />
            {errors.short_code && <span className={ERR}>{errors.short_code}</span>}
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-text-secondary font-medium">Price (₹) *</label>
            <input className={INPUT} value={price} onChange={(e) => setPrice(e.target.value)} placeholder="0" inputMode="decimal" />
            {errors.price && <span className={ERR}>{errors.price}</span>}
          </div>
          <div className="flex flex-col gap-1"><label className="text-xs text-text-secondary font-medium">Parcel (₹)</label><input className={INPUT} value={parcel} onChange={(e) => setParcel(e.target.value)} placeholder="—" inputMode="decimal" /></div>
          {vendors.map((v) => (
            <div key={v.slug} className="flex flex-col gap-1">
              <label className="text-xs text-text-secondary font-medium">{v.name} (₹)</label>
              <input className={INPUT} value={vprices[v.slug] ?? ''} onChange={(e) => setVprices((prev) => ({ ...prev, [v.slug]: e.target.value }))} placeholder="—" inputMode="decimal" />
            </div>
          ))}
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="text-xs text-text-secondary font-medium">Food Type</label>
          <div className="flex gap-2">{FT.map((opt) => (<button key={opt.value} type="button" onClick={() => setFoodType(opt.value)} className={`flex-1 py-1.5 rounded-lg text-xs font-medium border transition-colors ${foodType === opt.value ? 'bg-sphotel-accent text-sphotel-accent-fg border-sphotel-accent' : 'border-sphotel-border text-text-secondary hover:border-sphotel-accent'}`}>{opt.label}</button>))}</div>
        </div>
        <button type="button" onClick={() => setShowVariants(true)}
          className="flex items-center justify-between w-full border border-sphotel-border rounded-lg px-3 py-2 text-sm hover:border-sphotel-accent transition-colors">
          <span className="text-text-secondary">Variants</span>
          <span className="flex items-center gap-1 text-sphotel-accent font-medium">
            {variants.length > 0 ? `${variants.length} variant${variants.length > 1 ? 's' : ''}` : '+ Add variants'}
            <ChevronRight size={14} />
          </span>
        </button>
        <div className="flex items-center gap-2"><Switch checked={isAvailable} onCheckedChange={setIsAvailable} /><span className="text-sm text-text-secondary">Available</span></div>
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onCancel} disabled={isLoading} className="flex-1 border border-sphotel-border rounded-lg py-2 text-sm text-text-secondary">Cancel</button>
          <button type="submit" disabled={isLoading} className="flex-1 bg-sphotel-accent text-sphotel-accent-fg rounded-lg py-2 text-sm font-medium disabled:opacity-50">{isLoading ? 'Saving…' : isEdit ? 'Save Changes' : 'Add Item'}</button>
        </div>
      </form>
      {showVariants && <VariantsModal variants={variants} vendors={vendors} onSave={setVariants} onClose={() => setShowVariants(false)} />}
    </>
  )
}
