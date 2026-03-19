import { Plus, Trash2 } from 'lucide-react'
import type { MenuVariant, VendorPrice } from '../types/menu'

interface Props {
  variants: MenuVariant[]
  vendors: { slug: string; name: string }[]
  onChange: (variants: MenuVariant[]) => void
}

const INPUT = 'bg-bg-elevated border border-sphotel-border rounded px-2 py-1 text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-sphotel-accent'

function paise(val: string) { return val.trim() !== '' ? Math.round((Number(val) || 0) * 100) : null }
function rupees(p: number | null | undefined) { return p != null && p > 0 ? String(p / 100) : '' }

function setVendorPrice(vps: VendorPrice[] = [], slug: string, val: string): VendorPrice[] {
  const p = paise(val)
  const rest = vps.filter((v) => v.vendor_slug !== slug)
  return p != null ? [...rest, { vendor_slug: slug, price_paise: p }] : rest
}

function getVendorPrice(vps: VendorPrice[] = [], slug: string) {
  return rupees(vps.find((v) => v.vendor_slug === slug)?.price_paise)
}

export function VariantsEditor({ variants, vendors, onChange }: Props) {
  const cols = `grid-cols-[1fr_4rem_4rem${vendors.map(() => '_4rem').join('')}_1.25rem]`
  return (
    <div className="flex flex-col gap-1.5">
      {variants.length > 0 && (
        <div className={`grid ${cols} gap-1 text-xs text-text-muted px-0.5`}>
          <span>Name</span><span className="text-right">Price</span><span className="text-right">Parcel</span>
          {vendors.map((v) => <span key={v.slug} className="text-right truncate">{v.name}</span>)}
          <span />
        </div>
      )}
      {variants.map((v, i) => (
        <div key={i} className={`grid ${cols} gap-1 items-center`}>
          <input className={INPUT} placeholder="Variant name" value={v.name}
            onChange={(e) => { const n = [...variants]; n[i] = { ...n[i], name: e.target.value }; onChange(n) }} />
          <input className={INPUT + ' text-right'} placeholder="₹" inputMode="decimal" value={rupees(v.price_paise)}
            onChange={(e) => { const n = [...variants]; n[i] = { ...n[i], price_paise: Math.round((Number(e.target.value) || 0) * 100) }; onChange(n) }} />
          <input className={INPUT + ' text-right'} placeholder="—" inputMode="decimal" value={rupees(v.parcel_price_paise)}
            onChange={(e) => { const n = [...variants]; n[i] = { ...n[i], parcel_price_paise: paise(e.target.value) }; onChange(n) }} />
          {vendors.map((vd) => (
            <input key={vd.slug} className={INPUT + ' text-right'} placeholder="—" inputMode="decimal"
              value={getVendorPrice(v.vendor_prices, vd.slug)}
              onChange={(e) => { const n = [...variants]; n[i] = { ...n[i], vendor_prices: setVendorPrice(n[i].vendor_prices, vd.slug, e.target.value) }; onChange(n) }} />
          ))}
          <button type="button" onClick={() => onChange(variants.filter((_, idx) => idx !== i))}
            className="text-text-muted hover:text-status-error transition-colors flex items-center justify-center" aria-label="Remove">
            <Trash2 size={14} />
          </button>
        </div>
      ))}
      <button type="button" onClick={() => onChange([...variants, { name: '', price_paise: 0 }])}
        className="flex items-center gap-1 text-xs text-sphotel-accent hover:underline w-fit">
        <Plus size={12} /> Add variant
      </button>
    </div>
  )
}
