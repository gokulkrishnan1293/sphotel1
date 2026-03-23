import { Trash2 } from 'lucide-react'
import type { MenuItemResponse } from '../types/menu'
import { Switch } from '@/shared/components/ui/switch'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/shared/components/ui/table'

const FOOD_TYPE_BADGE: Record<string, string> = {
  veg: 'bg-status-success/15 text-status-success',
  egg: 'bg-status-warning/15 text-status-warning',
  non_veg: 'bg-status-error/15 text-status-error',
}
const FOOD_TYPE_LABEL: Record<string, string> = { veg: 'Veg', egg: 'Egg', non_veg: 'Non-Veg' }

interface Props {
  items: MenuItemResponse[]
  search: string
  onEdit: (item: MenuItemResponse) => void
  onToggle: (item: MenuItemResponse) => void
  onDelete: (id: string) => void
  isUpdating: boolean
}

export function MenuItemTable({ items, search, onEdit, onToggle, onDelete, isUpdating }: Props) {
  const q = search.toLowerCase()
  const filtered = items.filter(
    (i) => i.name.toLowerCase().includes(q) || i.category.toLowerCase().includes(q) || String(i.short_code ?? '').includes(q)
  )

  return (
    <div className="border border-sphotel-border rounded-xl overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="border-sphotel-border bg-bg-elevated hover:bg-bg-elevated">
            {['Code', 'Name', 'Category', 'Type', 'Price', 'Online', 'Available', ''].map((h, i) => (
              <TableHead key={i} className={`text-text-muted text-xs uppercase tracking-wide font-medium ${h === 'Price' || h === 'Online' ? 'text-right' : h === 'Available' || h === '' ? 'text-center' : ''}`}>{h}</TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {filtered.map((item) => (
            <TableRow key={item.id} className="border-sphotel-border cursor-pointer hover:bg-bg-elevated/50 transition-colors" onClick={() => onEdit(item)}>
              <TableCell className="text-text-muted font-mono text-xs w-16">{item.short_code ?? '—'}</TableCell>
              <TableCell className="font-medium text-text-primary">{item.name}</TableCell>
              <TableCell className="text-text-secondary">{item.category}</TableCell>
              <TableCell className="w-24">
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${FOOD_TYPE_BADGE[item.food_type]}`}>{FOOD_TYPE_LABEL[item.food_type]}</span>
              </TableCell>
              <TableCell className="text-right font-mono text-text-primary w-20">₹{(item.price_paise / 100).toFixed(0)}</TableCell>
              <TableCell className="text-right font-mono text-text-muted w-20">
                {(() => { const vp = item.vendor_prices?.find(v => v.vendor_slug === 'swiggy' || v.vendor_slug === 'zomato'); return vp ? `₹${(vp.price_paise / 100).toFixed(0)}` : '—' })()}
              </TableCell>
              <TableCell className="text-center w-24" onClick={(e) => e.stopPropagation()}>
                <Switch size="sm" checked={item.is_available} onCheckedChange={() => onToggle(item)} disabled={isUpdating} aria-label={`Toggle ${item.name}`} />
              </TableCell>
              <TableCell className="text-center w-10" onClick={(e) => e.stopPropagation()}>
                <button onClick={() => onDelete(item.id)} className="text-text-muted hover:text-status-error transition-colors" aria-label={`Delete ${item.name}`}>
                  <Trash2 size={15} />
                </button>
              </TableCell>
            </TableRow>
          ))}
          {filtered.length === 0 && (
            <TableRow className="border-0">
              <TableCell colSpan={8} className="text-center text-text-muted py-8">No results for "{search}"</TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  )
}
