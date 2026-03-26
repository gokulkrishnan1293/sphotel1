import { useState } from 'react'
import { Minus, Plus, Trash2 } from 'lucide-react'
import type { BillItemResponse } from '../types/bills'

const FONT_SIZES = [12, 13, 14, 15, 16, 18, 20, 22, 24]

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
  fontSizeIdx?: number
}

export function ItemRow({ item, disabled, onRemove, onQtyChange, onPriceOverride, readOnly, fontSizeIdx = 2 }: Props) {
  const fs = FONT_SIZES[fontSizeIdx] ?? 16
  const textStyle = { fontSize: fs }
  const [editing, setEditing] = useState(false)
  const [draftRupees, setDraftRupees] = useState('')
  const effectivePaise = item.override_price_paise ?? item.price_paise
  const linePaise = effectivePaise * item.quantity

  function startEdit() {
    if (disabled || !onPriceOverride) return
    setDraftRupees(String(effectivePaise / 100))
    setEditing(true)
  }

  function commitEdit() {
    const val = parseFloat(draftRupees)
    if (!isNaN(val) && val >= 0) onPriceOverride!(Math.round(val * 100))
    setEditing(false)
  }

  return (
    <div className={`flex items-start gap-2.5 py-2.5 px-3 rounded-xl ${readOnly ? 'opacity-70' : 'hover:bg-bg-surface'}`}>
      <span className={`w-2 h-2 rounded-full shrink-0 mt-1.5 ${FOOD_DOT[item.food_type]}`} />
      <div className="flex-1 min-w-0">
        {/* Row 1: name + line total */}
        <div className="flex items-start gap-2">
          <p className="flex-1 min-w-0 text-text-primary leading-snug" style={textStyle}>{item.name}</p>
          {editing ? (
            <input
              autoFocus
              className="w-20 shrink-0 text-right text-sm font-medium bg-bg-elevated border border-sphotel-accent rounded px-1 py-0.5 text-text-primary outline-none"
              value={draftRupees}
              onChange={(e) => setDraftRupees(e.target.value)}
              onBlur={commitEdit}
              onKeyDown={(e) => { if (e.key === 'Enter') commitEdit(); if (e.key === 'Escape') setEditing(false) }}
              inputMode="decimal"
            />
          ) : (
            <span
              onClick={startEdit}
              className={`font-medium text-text-primary shrink-0 ${!disabled && onPriceOverride ? 'cursor-pointer hover:text-sphotel-accent' : ''}`}
              style={textStyle}
            >
              ₹{(linePaise / 100).toFixed(0)}
            </span>
          )}
        </div>
        {/* Row 2: unit price + qty controls */}
        <div className="flex items-center justify-between mt-1 gap-2">
          <span className="text-xs text-text-muted">
            ₹{(item.price_paise / 100).toFixed(0)}
            {item.override_price_paise != null && <span className="text-sphotel-accent ml-1">→{(item.override_price_paise / 100).toFixed(0)}</span>}
          </span>
          {!readOnly && !disabled ? (
            <div className="flex items-center gap-1">
              <button onClick={() => onQtyChange(item.quantity - 1)}
                className="w-7 h-7 flex items-center justify-center rounded-md bg-bg-elevated hover:bg-bg-base text-text-secondary">
                <Minus size={11} />
              </button>
              <span className="text-sm font-medium text-text-primary w-5 text-center">{item.quantity}</span>
              <button onClick={() => onQtyChange(item.quantity + 1)}
                className="w-7 h-7 flex items-center justify-center rounded-md bg-bg-elevated hover:bg-bg-base text-text-secondary">
                <Plus size={11} />
              </button>
              <button onClick={onRemove} className="p-1.5 ml-1 text-text-muted hover:text-status-error rounded-md">
                <Trash2 size={13} />
              </button>
            </div>
          ) : (
            <span className="text-sm text-text-muted" style={textStyle}>×{item.quantity}</span>
          )}
        </div>
        {item.notes && <p className="text-xs text-text-muted mt-0.5">{item.notes}</p>}
      </div>
    </div>
  )
}
