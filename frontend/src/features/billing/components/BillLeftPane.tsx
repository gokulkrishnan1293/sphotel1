import { type RefObject } from 'react'
import { Search } from 'lucide-react'
import { BillContextBar } from './BillContextBar'
import { InlineBillCreator } from './InlineBillCreator'
import { InlineSearch, type InlineSearchHandle } from './InlineSearch'
import { ItemGrid } from './ItemGrid'
import type { BillResponse } from '../types/bills'

interface Props {
  activeBillId: string | null
  bill: BillResponse | undefined
  canOpenNewBill: boolean
  isClosed: boolean
  searchRef: RefObject<InlineSearchHandle>
  fontSizeIdx?: number
  onGenerateBill: () => void
  onReset: () => void
}

export function BillLeftPane({ activeBillId, bill, canOpenNewBill, isClosed, searchRef, fontSizeIdx = 2, onGenerateBill, onReset }: Props) {
  const needsTable = bill?.bill_type === 'table' && !bill?.table_id
  const needsWaiter = bill?.bill_type === 'table' && !bill?.waiter_id
  const needsRef = bill?.bill_type === 'online' && !bill?.reference_no
  const blocked = needsTable || needsWaiter || needsRef
  const blockedMsg = needsTable ? 'Add table above to search…' : needsWaiter ? 'Add waiter above to search…' : 'Add ref number above to search…'
  return (
    <div className="flex flex-col min-h-0 h-full">
      {!activeBillId
        ? <InlineBillCreator canOpen={canOpenNewBill} />
        : bill
          ? <BillContextBar key={activeBillId} bill={bill} onDone={() => searchRef.current?.focus()} onReset={onReset} />
          : <div className="px-4 py-2 border-b border-sphotel-border" />}
      {activeBillId && bill && !isClosed && !blocked
        ? <>
            <InlineSearch ref={searchRef} billId={activeBillId} billType={bill.bill_type} platform={bill.platform} onGenerateBill={onGenerateBill} />
            <div className="hidden md:flex flex-col flex-1 min-h-0">
              <ItemGrid billId={activeBillId} billType={bill.bill_type} platform={bill.platform} fontSizeIdx={fontSizeIdx} />
            </div>
          </>
        : <div className="px-4 border-b border-sphotel-border flex items-center gap-2 py-3">
            <Search size={14} className="text-text-muted shrink-0" />
            <input disabled placeholder={blocked ? blockedMsg : activeBillId ? 'Loading…' : 'Open a bill above to search items…'}
              className="flex-1 bg-transparent text-sm text-text-muted outline-none py-1 opacity-50" />
          </div>}
    </div>
  )
}
