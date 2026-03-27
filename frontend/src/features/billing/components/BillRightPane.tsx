import { ItemRow } from './ItemRow'
import { BillFooter } from './BillFooter'
import type { BillResponse, BillItemResponse, PaymentMethod } from '../types/bills'

interface Props {
  bill: BillResponse | undefined
  activeBillId: string | null
  isBiller: boolean
  pending: BillItemResponse[]
  sent: BillItemResponse[]
  hasItems: boolean
  fontSizeIdx: number
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
  onRemove: (id: string) => void
  onQtyChange: (id: string, qty: number) => void
  onPriceOverride: (id: string, price: number) => void
}

export function BillRightPane({ bill, activeBillId, isBiller, pending, sent, hasItems, fontSizeIdx, printQueued, fireKotPending, closeBillPending, printPending, onFireKot, onSettle, onVoid, onUnvoid, onPrint, onUpdateMethod, onRemove, onQtyChange, onPriceOverride }: Props) {
  const isClosed = bill ? bill.status === 'billed' || bill.status === 'void' : false
  return (
    <div className="flex flex-col min-h-0 h-full">
      {bill && <div className="order-2 md:order-1"><BillFooter bill={bill} isBiller={isBiller} hasItems={hasItems} pendingCount={pending.length} printQueued={printQueued}
        fireKotPending={fireKotPending} closeBillPending={closeBillPending} printPending={printPending}
        onFireKot={onFireKot} onSettle={onSettle} onVoid={onVoid} onUnvoid={onUnvoid} onPrint={onPrint} onUpdateMethod={onUpdateMethod} /></div>}
      <div className="order-1 md:order-2 flex-1 overflow-y-auto px-3 py-3 flex flex-col gap-0.5">
        {!activeBillId && <p className="text-text-muted text-sm text-center py-16">Select a bill type to start</p>}
        {bill && pending.length > 0 && sent.length > 0 && <p className="text-xs font-medium text-amber-400 uppercase tracking-wide mb-1">New (not sent)</p>}
        {bill && pending.map((item, i) => <ItemRow key={item.id} item={item} index={i + 1} disabled={isClosed} onRemove={() => onRemove(item.id)} onQtyChange={(q) => q < 1 ? onRemove(item.id) : onQtyChange(item.id, q)} onPriceOverride={(p) => onPriceOverride(item.id, p)} fontSizeIdx={fontSizeIdx} />)}
        {bill && sent.length > 0 && <p className={`text-xs font-medium uppercase tracking-wide mb-1 mt-2 ${pending.length > 0 ? 'text-status-success' : 'text-text-muted'}`}>{pending.length > 0 ? 'Sent to kitchen' : 'Items'}</p>}
        {bill && sent.map((item, i) => <ItemRow key={item.id} item={item} index={pending.length + i + 1} disabled={isClosed} onRemove={() => {}} onQtyChange={() => {}} readOnly onPriceOverride={(p) => onPriceOverride(item.id, p)} fontSizeIdx={fontSizeIdx} />)}
        {bill && bill.items.length === 0 && <div className="flex items-center justify-center py-16"><p className="text-text-muted text-sm">Empty — search or tap items to add</p></div>}
      </div>
    </div>
  )
}
