import { useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { billsApi } from '../api/bills'
import { useBillingStore } from '../stores/billingStore'
import { SettleDialog } from './SettleDialog'
import { BillTabBar } from './BillTabBar'
import { BillLeftPane } from './BillLeftPane'
import { BillRightPane } from './BillRightPane'
import { useBillCanvasShortcuts } from './useBillCanvasShortcuts'
import type { InlineSearchHandle } from './InlineSearch'
import type { PaymentMethod } from '../types/bills'
import { useAuthStore } from '../../auth/stores/authStore'
import { useFeatureFlagStore } from '@/lib/featureFlagStore'
import { toast } from '@/lib/toast'
import { localPrint } from '@/lib/localPrint'

const defaultMethod = (billType: string): PaymentMethod => billType === 'online' ? 'online' : 'cash'

export function BillCanvas({ fontSizeIdx = 1, canOpenNewBill = true }: { fontSizeIdx?: number; canOpenNewBill?: boolean }) {
  const qc = useQueryClient()
  const { activeBillId, setActiveBill } = useBillingStore()
  const role = useAuthStore((s) => s.currentUser?.role ?? '')
  const isAdmin = ['admin', 'super_admin'].includes(role)
  const isBiller = role === 'biller' || isAdmin
  const [settleOpen, setSettleOpen] = useState(false)
  const [printQueued, setPrintQueued] = useState(false)
  const searchRef = useRef<InlineSearchHandle>(null)

  const { data: bill } = useQuery({ queryKey: ['bill', activeBillId], queryFn: () => billsApi.get(activeBillId!), enabled: !!activeBillId, refetchInterval: 10_000 })

  const inv = () => { qc.invalidateQueries({ queryKey: ['bill', activeBillId] }); qc.invalidateQueries({ queryKey: ['bills', 'open'] }) }
  const fireKot = useMutation({ mutationFn: () => billsApi.fireKot(activeBillId!), onSuccess: inv })
  const closeBill = useMutation({
    mutationFn: ({ method, discount }: { method: PaymentMethod; discount: number }) => billsApi.close(activeBillId!, { payment_method: method, discount_paise: discount }),
    onSuccess: (closedBill) => { inv(); setSettleOpen(false); billsApi.print(activeBillId!).catch(() => localPrint(closedBill).catch(() => {})); if (useFeatureFlagStore.getState().billCloseUx) { toast('Bill settled ✓  Printing…'); setPrintQueued(true); setTimeout(() => { setPrintQueued(false); setActiveBill(null) }, 5000) } else setActiveBill(null) },
  })
  const removeItem = useMutation({ mutationFn: (id: string) => billsApi.removeItem(activeBillId!, id), onSuccess: inv })
  const updateQty = useMutation({ mutationFn: ({ itemId, quantity }: { itemId: string; quantity: number }) => billsApi.updateItem(activeBillId!, itemId, { quantity }), onSuccess: inv })
  const updatePrice = useMutation({ mutationFn: ({ itemId, opp }: { itemId: string; opp: number }) => billsApi.updateItem(activeBillId!, itemId, { override_price_paise: opp }), onSuccess: inv })
  const invBill = () => { qc.invalidateQueries({ queryKey: ['bill', activeBillId] }); qc.invalidateQueries({ queryKey: ['bills', 'open'] }); qc.invalidateQueries({ queryKey: ['bills', 'recent'] }) }
  const voidBill = useMutation({ mutationFn: () => billsApi.void(activeBillId!), onSuccess: invBill })
  const unvoidBill = useMutation({ mutationFn: () => billsApi.unvoid(activeBillId!), onSuccess: invBill })
  const cancelBill = useMutation({ mutationFn: () => billsApi.cancel(activeBillId!), onSuccess: () => { invBill(); setActiveBill(null) } })
  const printBill = useMutation({ mutationFn: () => billsApi.print(activeBillId!).catch(() => bill ? localPrint(bill) : Promise.reject(new Error('no bill'))) })
  const updateMethod = useMutation({ mutationFn: (m: PaymentMethod) => billsApi.updatePaymentMethod(activeBillId!, m), onSuccess: inv })

  useBillCanvasShortcuts(activeBillId, bill, () => searchRef.current?.focus(), () => fireKot.mutate(), (m) => closeBill.mutate({ method: m, discount: 0 }), closeBill.isPending, setSettleOpen, defaultMethod)

  function handleReset() {
    const hasSent = bill?.items.some((i) => i.status === 'sent')
    if (!hasSent || confirm('This bill has sent items. Cancel and discard?')) { cancelBill.mutate() }
  }

  const isClosed = bill ? bill.status === 'billed' || bill.status === 'void' : false
  const pending = bill?.items.filter((i) => i.status === 'pending') ?? []
  const sent = bill?.items.filter((i) => i.status === 'sent') ?? []
  const hasItems = bill?.items.some((i) => i.status !== 'voided') ?? false

  return (
    <div className="flex-1 flex flex-col min-h-0">
      <BillTabBar canOpenNewBill={canOpenNewBill} onNewBill={() => setActiveBill(null)} />
      <div className="grid grid-rows-[auto_1fr] md:grid-rows-[1fr] md:grid-cols-[1fr_1fr] flex-1 min-h-0 overflow-hidden">
        <div className="flex flex-col min-h-0 border-r border-sphotel-border overflow-hidden">
          <BillLeftPane activeBillId={activeBillId} bill={bill} canOpenNewBill={canOpenNewBill} isClosed={isClosed} searchRef={searchRef} onGenerateBill={() => setSettleOpen(true)} onReset={handleReset} />
        </div>
        <div className="flex flex-col min-h-0 overflow-hidden">
          <BillRightPane bill={bill} activeBillId={activeBillId} isBiller={isBiller} pending={pending} sent={sent} hasItems={hasItems} fontSizeIdx={fontSizeIdx} printQueued={printQueued}
            fireKotPending={fireKot.isPending} closeBillPending={closeBill.isPending} printPending={printBill.isPending}
            onFireKot={() => fireKot.mutate()} onSettle={() => setSettleOpen(true)}
            onVoid={() => { if (confirm('Void this bill?')) voidBill.mutate() }}
            onUnvoid={() => { if (confirm('Restore this bill?')) unvoidBill.mutate() }}
            onPrint={() => printBill.mutate()} onUpdateMethod={(m) => updateMethod.mutate(m)}
            onRemove={(id) => removeItem.mutate(id)}
            onQtyChange={(id, qty) => updateQty.mutate({ itemId: id, quantity: qty })}
            onPriceOverride={(id, opp) => updatePrice.mutate({ itemId: id, opp })} />
        </div>
      </div>
      {settleOpen && bill && <SettleDialog bill={bill} onClose={() => setSettleOpen(false)} onSettle={(m, d) => closeBill.mutate({ method: m, discount: d })} isLoading={closeBill.isPending} />}
    </div>
  )
}
