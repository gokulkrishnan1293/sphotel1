import { useState, useEffect, useRef } from 'react'
import type { MenuItemResponse } from '../../admin/types/menu'
import type { BillType } from '../types/bills'

interface Props {
  item: MenuItemResponse
  qty: number
  billType: BillType
  onSelect: (variantName: string, pricePaise: number) => void
  onBack: () => void
}

function pickPrice(v: { price_paise: number; parcel_price_paise?: number | null; online_price_paise?: number | null }, billType: BillType): number {
  if (billType === 'parcel' && v.parcel_price_paise) return v.parcel_price_paise
  if (billType === 'online' && v.online_price_paise) return v.online_price_paise
  return v.price_paise
}

export function VariantPicker({ item, qty, billType, onSelect, onBack }: Props) {
  const [idx, setIdx] = useState(0)
  const containerRef = useRef<HTMLDivElement>(null)
  const variants = item.variants ?? []

  useEffect(() => { containerRef.current?.focus() }, [])

  function onKey(e: React.KeyboardEvent) {
    if (e.key === 'ArrowDown') { e.preventDefault(); setIdx((i) => Math.min(i + 1, variants.length - 1)) }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setIdx((i) => Math.max(i - 1, 0)) }
    else if (e.key === 'Enter') { const v = variants[idx]; if (v) onSelect(v.name, pickPrice(v, billType)) }
    else if (e.key === 'Escape') onBack()
  }

  return (
    <div ref={containerRef} tabIndex={-1} onKeyDown={onKey} className="outline-none">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-sphotel-border">
        <button onClick={onBack} className="text-text-muted hover:text-text-primary transition-colors text-sm">←</button>
        <span className="text-sm font-medium text-text-primary">{item.name}</span>
        {qty > 1 && <span className="ml-auto text-xs bg-sphotel-accent-subtle text-sphotel-accent px-2 py-0.5 rounded-full font-medium">×{qty}</span>}
      </div>

      <div className="max-h-80 overflow-y-auto">
        {variants.map((v, i) => {
          const price = pickPrice(v, billType)
          return (
            <button key={v.name} onClick={() => onSelect(v.name, price)}
              className={`w-full flex items-center justify-between px-4 py-2.5 text-left transition-colors ${i === idx ? 'bg-sphotel-accent-subtle' : 'hover:bg-bg-base'}`}>
              <span className="text-sm text-text-primary">{v.name}</span>
              <span className="text-sm font-medium text-text-primary">₹{Math.floor(price / 100)}</span>
            </button>
          )
        })}
      </div>

      <div className="px-4 py-2 border-t border-sphotel-border flex items-center gap-4 text-xs text-text-muted">
        <span>↑↓ navigate</span><span>Enter select</span><span>Esc back</span>
      </div>
    </div>
  )
}
