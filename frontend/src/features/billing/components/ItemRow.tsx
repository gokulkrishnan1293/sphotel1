import { useState } from 'react'
import { Minus, Plus, Trash2 } from 'lucide-react'
import type { BillItemResponse } from '../types/bills'

const FOOD_DOT: Record<string, string> = {
  veg: 'bg-emerald-500',
  egg: 'bg-yellow-400',
  non_veg: 'bg-red-500',
}

interface Props {
  item: BillItemResponse
  disabled: boolean
  onRemove: () => void
  onQtyChange: (qty: number) => void
  onPriceOverride?: (paise: number) => void
  readOnly?: boolean
}

export function ItemRow({ item, disabled, onRemove, onQtyChange, onPriceOverride, readOnly }: Props) {
  const [editing, setEditing] = useState(false)
  const [draftRupees, setDraftRupees] = useState('')
  const effectivePaise = item.override_price_paise ?? item.price_paise
  const linePaise = effectivePaise * item.quantity

  function startEdit() {
    if (readOnly || disabled || !onPriceOverride) return
    setDraftRupees(String(effectivePaise / 100))
    setEditing(true)
  }

  function commitEdit() {
    const val = parseFloat(draftRupees)
    if (!isNaN(val) && val >= 0) onPriceOverride!(Math.round(val * 100))
    setEditing(false)
  }

  return (
    <div className={`flex items-center gap-3 py-2 px-3 rounded-xl group ${readOnly ? 'opacity-70' : 'hover:bg-bg-surface'}`}>
      <span className={`w-2 h-2 rounded-full shrink-0 ${FOOD_DOT[item.food_type]}`} />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-text-primary truncate">{item.name}</p>
        {item.notes && <p className="text-xs text-text-muted">{item.notes}</p>}
      </div>
      <span className="text-xs text-text-muted shrink-0">
        ₹{(item.price_paise / 100).toFixed(0)}
        {item.override_price_paise != null && <span className="text-sphotel-accent ml-1">→{(item.override_price_paise / 100).toFixed(0)}</span>}
      </span>

      {!readOnly && !disabled ? (
        <div className="flex items-center gap-1">
          <button onClick={() => onQtyChange(item.quantity - 1)}
            className="w-6 h-6 flex items-center justify-center rounded-md bg-bg-elevated hover:bg-bg-base text-text-secondary">
            <Minus size={10} />
          </button>
          <span className="text-sm font-medium text-text-primary w-5 text-center">{item.quantity}</span>
          <button onClick={() => onQtyChange(item.quantity + 1)}
            className="w-6 h-6 flex items-center justify-center rounded-md bg-bg-elevated hover:bg-bg-base text-text-secondary">
            <Plus size={10} />
          </button>
        </div>
      ) : (
        <span className="text-sm font-medium text-text-primary w-5 text-center">×{item.quantity}</span>
      )}

      {editing ? (
        <input autoFocus className="w-16 text-right text-sm font-medium bg-bg-elevated border border-sphotel-accent rounded px-1 py-0.5 text-text-primary outline-none"
          value={draftRupees} onChange={(e) => setDraftRupees(e.target.value)}
          onBlur={commitEdit} onKeyDown={(e) => { if (e.key === 'Enter') commitEdit(); if (e.key === 'Escape') setEditing(false) }}
          inputMode="decimal" />
      ) : (
        <span onClick={startEdit}
          className={`text-sm font-medium text-text-primary w-16 text-right shrink-0 ${!readOnly && !disabled && onPriceOverride ? 'cursor-pointer hover:text-sphotel-accent' : ''}`}>
          ₹{(linePaise / 100).toFixed(0)}
        </span>
      )}

      {!readOnly && !disabled && (
        <button onClick={onRemove} className="md:opacity-0 md:group-hover:opacity-100 p-1 text-text-muted hover:text-status-error rounded">
          <Trash2 size={13} />
        </button>
      )}
    </div>
  )
}
