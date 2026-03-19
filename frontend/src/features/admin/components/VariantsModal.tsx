import { useState } from 'react'
import { Plus, Trash2, X } from 'lucide-react'
import type { MenuVariant, VendorPrice } from '../types/menu'
import type { VendorItem } from '../../settings/api/onlineVendors'

interface Props {
  variants: MenuVariant[]
  vendors: VendorItem[]
  onSave: (variants: MenuVariant[]) => void
  onClose: () => void
}

const INPUT = 'bg-bg-base border border-sphotel-border rounded px-2 py-1.5 text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-sphotel-accent w-full'

function rupees(p: number | null | undefined) { return p != null && p > 0 ? String(p / 100) : '' }
function paise(v: string) { return v.trim() ? Math.round((Number(v) || 0) * 100) : null }
function getVP(vps: VendorPrice[] = [], slug: string) { return rupees(vps.find((v) => v.vendor_slug === slug)?.price_paise) }
function setVP(vps: VendorPrice[] = [], slug: string, val: string): VendorPrice[] {
  const p = paise(val)
  return p != null ? [...vps.filter((v) => v.vendor_slug !== slug), { vendor_slug: slug, price_paise: p }] : vps.filter((v) => v.vendor_slug !== slug)
}

export function VariantsModal({ variants: initial, vendors, onSave, onClose }: Props) {
  const [rows, setRows] = useState<MenuVariant[]>(initial)

  function update(i: number, patch: Partial<MenuVariant>) {
    setRows((prev) => prev.map((r, idx) => idx === i ? { ...r, ...patch } : r))
  }

  function handleSave() { onSave(rows.filter((r) => r.name.trim())); onClose() }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />
      <div className="relative bg-bg-elevated border border-sphotel-border rounded-2xl shadow-2xl w-full max-w-3xl flex flex-col max-h-[80vh]">
        <div className="flex items-center justify-between px-5 py-4 border-b border-sphotel-border">
          <h3 className="font-semibold text-text-primary">Variants</h3>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary"><X size={18} /></button>
        </div>

        <div className="overflow-auto flex-1 px-5 py-4">
          {rows.length > 0 && (
            <div className={`grid gap-2 text-xs text-text-muted mb-1`}
              style={{ gridTemplateColumns: `1fr 5rem 5rem${vendors.map(() => ' 5rem').join('')} 1.5rem` }}>
              <span>Name</span><span className="text-right">Price (₹)</span><span className="text-right">Parcel (₹)</span>
              {vendors.map((v) => <span key={v.slug} className="text-right truncate">{v.name} (₹)</span>)}
              <span />
            </div>
          )}

          <div className="flex flex-col gap-2">
            {rows.map((row, i) => (
              <div key={i} className="grid gap-2 items-center"
                style={{ gridTemplateColumns: `1fr 5rem 5rem${vendors.map(() => ' 5rem').join('')} 1.5rem` }}>
                <input className={INPUT} placeholder="e.g. Half" value={row.name}
                  onChange={(e) => update(i, { name: e.target.value })} />
                <input className={INPUT + ' text-right'} placeholder="0" inputMode="decimal" value={rupees(row.price_paise)}
                  onChange={(e) => update(i, { price_paise: Math.round((Number(e.target.value) || 0) * 100) })} />
                <input className={INPUT + ' text-right'} placeholder="—" inputMode="decimal" value={rupees(row.parcel_price_paise)}
                  onChange={(e) => update(i, { parcel_price_paise: paise(e.target.value) })} />
                {vendors.map((vd) => (
                  <input key={vd.slug} className={INPUT + ' text-right'} placeholder="—" inputMode="decimal"
                    value={getVP(row.vendor_prices, vd.slug)}
                    onChange={(e) => update(i, { vendor_prices: setVP(row.vendor_prices, vd.slug, e.target.value) })} />
                ))}
                <button type="button" onClick={() => setRows((r) => r.filter((_, idx) => idx !== i))}
                  className="text-text-muted hover:text-status-error flex items-center justify-center">
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>

          <button type="button" onClick={() => setRows((r) => [...r, { name: '', price_paise: 0 }])}
            className="mt-3 flex items-center gap-1 text-xs text-sphotel-accent hover:underline">
            <Plus size={12} /> Add variant
          </button>
        </div>

        <div className="flex gap-2 px-5 py-4 border-t border-sphotel-border">
          <button type="button" onClick={onClose} className="flex-1 border border-sphotel-border rounded-lg py-2 text-sm text-text-secondary">Cancel</button>
          <button type="button" onClick={handleSave} className="flex-1 bg-sphotel-accent text-sphotel-accent-fg rounded-lg py-2 text-sm font-medium">Save Variants</button>
        </div>
      </div>
    </div>
  )
}
