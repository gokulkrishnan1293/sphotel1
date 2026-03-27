import { Flame, CreditCard, Ban, RotateCcw, Printer } from 'lucide-react'
import type { BillResponse, PaymentMethod } from '../types/bills'
import { useShortcutStore } from '@/lib/shortcutStore'

const fmt = (p: number) => `₹${(p / 100).toFixed(2)}`

interface Props {
  bill: BillResponse
  isBiller: boolean
  hasItems: boolean
  pendingCount: number
  printQueued: boolean
  fireKotPending: boolean
  closeBillPending: boolean
  printPending: boolean
  onFireKot: () => void
  onSettle: () => void
  onVoid: () => void
  onUnvoid: () => void
  onPrint: () => void
  onUpdateMethod: (m: PaymentMethod) => void
}

export function BillFooter({ bill, isBiller, hasItems, pendingCount, printQueued, fireKotPending, closeBillPending, printPending, onFireKot, onSettle, onVoid, onUnvoid, onPrint, onUpdateMethod }: Props) {
  const sc = useShortcutStore((s) => s.shortcuts)
  const isClosed = bill.status === 'billed' || bill.status === 'void'
  return (
    <>
      {!isClosed && (
        <div className="px-4 py-3 md:px-6 md:py-4 border-b border-sphotel-border flex flex-col gap-3">
          <div className="flex justify-between text-sm">
            <span className="text-text-secondary">Subtotal <span className="text-text-muted text-xs">· {bill.items.length} items</span></span>
            <span className="font-medium text-text-primary">{fmt(bill.subtotal_paise)}</span>
          </div>
          <div className="flex gap-2">
            {pendingCount > 0 && bill.bill_type === 'table' && <button onClick={onFireKot} disabled={fireKotPending} className="flex-1 py-3 md:py-2.5 bg-amber-500 text-white rounded-xl text-sm font-medium hover:bg-amber-600 disabled:opacity-50 flex items-center justify-center gap-1.5"><Flame size={14} />Fire KOT<kbd className="hidden md:inline text-xs opacity-50 font-mono ml-1">⌘K</kbd></button>}
            <button onClick={onSettle} disabled={!hasItems || closeBillPending} className="flex-1 py-3 md:py-2.5 bg-sphotel-accent text-sphotel-accent-fg rounded-xl text-sm font-medium hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-1.5"><CreditCard size={14} />Generate Bill<kbd className="hidden md:inline text-xs opacity-50 font-mono ml-1">{sc.generate_bill.toUpperCase()}</kbd><span className="hidden md:inline text-xs opacity-50">·</span><kbd className="hidden md:inline text-xs opacity-50 font-mono">{sc.close_bill.toUpperCase()}</kbd></button>
          </div>
        </div>
      )}
      {isClosed && (
        <div className="px-4 py-3 md:px-6 md:py-4 border-b border-sphotel-border flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          {bill.status === 'billed' ? (
            <span className="text-sm font-medium text-sphotel-accent flex items-center gap-1.5">
              Settled · {fmt(bill.total_paise)} via
              <select value={bill.payment_method ?? 'cash'} onChange={(e) => onUpdateMethod(e.target.value as PaymentMethod)} className="bg-transparent text-sphotel-accent font-medium text-sm border-0 outline-none cursor-pointer">
                {(['cash','card','upi','online'] as PaymentMethod[]).map(m => <option key={m} value={m} className="bg-bg-surface text-text-primary">{m}</option>)}
              </select>
            </span>
          ) : (
            <p className="text-sm font-medium text-status-error">This bill has been voided</p>
          )}
          <div className="flex items-center gap-3">
            {isBiller && bill.status === 'billed' && <button onClick={onVoid} className="flex items-center gap-1.5 text-xs text-status-error hover:opacity-80 py-1"><Ban size={12} />Void bill</button>}
            {isBiller && bill.status === 'void' && <button onClick={onUnvoid} className="flex items-center gap-1.5 text-xs text-status-success hover:opacity-80 py-1"><RotateCcw size={12} />Unvoid bill</button>}
            {bill.status === 'billed' && <button onClick={onPrint} disabled={printPending} className="flex items-center gap-1.5 text-xs text-text-muted hover:text-text-primary disabled:opacity-50"><Printer size={13} />{printQueued ? 'Printing…' : printPending ? 'Queued…' : 'Reprint'}</button>}
          </div>
        </div>
      )}
    </>
  )
}
