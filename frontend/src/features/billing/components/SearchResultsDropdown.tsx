import { createPortal } from 'react-dom'
import type { MenuItemResponse } from '../../admin/types/menu'
import type { BillType } from '../types/bills'
import { dispPrice } from './searchHelpers'

const FOOD_DOT: Record<string, string> = { veg: 'bg-emerald-500', egg: 'bg-yellow-400', non_veg: 'bg-red-500' }

interface Props {
  items: MenuItemResponse[]
  activeIdx: number
  style: { top: number; left: number; width: number }
  billType: BillType
  platform?: string | null
  onSelect: (item: MenuItemResponse) => void
}

export function SearchResultsDropdown({ items, activeIdx, style, billType, platform, onSelect }: Props) {
  return createPortal(
    <div style={{ position: 'fixed', top: style.top, left: style.left, width: style.width, zIndex: 9999 }}
      className="bg-bg-elevated border border-sphotel-border border-t-0 rounded-b-xl shadow-xl max-h-64 overflow-y-auto">
      {items.map((item, i) => (
        <button key={item.id} onMouseDown={() => onSelect(item)}
          className={`w-full flex items-center gap-3 px-4 py-2 text-left transition-colors ${i === activeIdx ? 'bg-sphotel-accent-subtle' : 'hover:bg-bg-base'}`}>
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
    </div>,
    document.body
  )
}
