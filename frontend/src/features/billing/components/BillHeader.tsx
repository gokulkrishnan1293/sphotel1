import { UtensilsCrossed, ShoppingBag, Laptop } from 'lucide-react'
import type { BillResponse } from '../types/bills'

const STATUS_BADGE: Record<string, string> = {
  draft: 'text-text-muted', kot_sent: 'text-status-success',
  partially_sent: 'text-amber-400', billed: 'text-sphotel-accent', void: 'text-status-error',
}
const STATUS_LABEL: Record<string, string> = {
  draft: 'Draft', kot_sent: 'KOT Sent', partially_sent: 'Partial KOT', billed: 'Settled', void: 'Void',
}

function asUtc(iso: string): Date {
  if (!iso.endsWith('Z') && !iso.includes('+') && !/\d{2}:\d{2}$/.test(iso)) return new Date(iso + 'Z')
  return new Date(iso)
}
function fmtTime(iso: string) {
  return asUtc(iso).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true })
}
function fmtDate(iso: string) {
  return asUtc(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
}

export function BillHeader({ bill }: { bill: BillResponse }) {
  const Icon = bill.bill_type === 'table' ? UtensilsCrossed : bill.bill_type === 'parcel' ? ShoppingBag : Laptop
  const title = bill.bill_type === 'table' ? 'Table Bill' : bill.bill_type === 'parcel' ? 'Parcel' : bill.platform ?? 'Online'
  const staffName = bill.waiter_name ?? bill.created_by_name
  const timeStr = bill.paid_at ? `${fmtDate(bill.paid_at)} ${fmtTime(bill.paid_at)}` : `${fmtDate(bill.created_at)} ${fmtTime(bill.created_at)}`

  return (
    <div className="px-6 py-4 border-b border-sphotel-border flex items-center gap-3">
      <Icon size={18} className="text-text-muted shrink-0" />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-semibold text-text-primary">{title}</span>
          <span className="text-xs text-text-muted font-mono">#{bill.bill_number}</span>
          {bill.reference_no && <span className="text-xs text-text-muted">· {bill.reference_no}</span>}
          {bill.covers != null && <span className="text-xs text-text-muted">{bill.covers} guests</span>}
        </div>
        <div className="flex items-center gap-2 mt-0.5">
          <span className={`text-xs font-medium ${STATUS_BADGE[bill.status]}`}>{STATUS_LABEL[bill.status]}</span>
          <span className="text-xs text-text-muted">· {timeStr}</span>
          {staffName && <span className="text-xs text-text-muted">· {staffName}</span>}
        </div>
      </div>
      <div className="text-right shrink-0">
        <p className="text-lg font-bold text-text-primary">₹{(bill.total_paise / 100).toFixed(2)}</p>
        <p className="text-xs text-text-muted">{bill.items.filter((i) => i.status !== 'voided').length} items</p>
      </div>
    </div>
  )
}
