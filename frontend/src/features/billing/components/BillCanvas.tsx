import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Flame, Plus, CreditCard, Ban, UtensilsCrossed, Printer } from 'lucide-react'
import { billsApi } from '../api/bills'
import { useBillingStore } from '../stores/billingStore'
import { CommandPalette } from './CommandPalette'
import { SettleDialog } from './SettleDialog'
import { ItemRow } from './ItemRow'
import { BillHeader } from './BillHeader'
import type { PaymentMethod } from '../types/bills'
import { useAuthStore } from '../../auth/stores/authStore'
import { useShortcutStore, matchKey } from '@/lib/shortcutStore'
import { useFeatureFlagStore } from '@/lib/featureFlagStore'
import { toast } from '@/lib/toast'
import { localPrint } from '@/lib/localPrint'
const fmt = (p: number) => `₹${(p / 100).toFixed(2)}`; const defaultMethod = (billType: string): PaymentMethod => billType === 'online' ? 'online' : 'cash'

export function BillCanvas({ fontSizeIdx = 1 }: { fontSizeIdx?: number }) {
  const qc = useQueryClient()
  const { activeBillId, commandPaletteOpen, openCommandPalette, closeCommandPalette } = useBillingStore()
  const role = useAuthStore((s) => s.currentUser?.role ?? '')
  const isAdmin = ['admin', 'super_admin'].includes(role)
  const isBiller = role === 'biller' || isAdmin
  const [settleOpen, setSettleOpen] = useState(false)
  const [printQueued, setPrintQueued] = useState(false)

  const { data: bill, isLoading } = useQuery({
    queryKey: ['bill', activeBillId], queryFn: () => billsApi.get(activeBillId!),
    enabled: !!activeBillId, refetchInterval: 10_000,
  })

  const inv = () => { qc.invalidateQueries({ queryKey: ['bill', activeBillId] }); qc.invalidateQueries({ queryKey: ['bills', 'open'] }) }
  const fireKot = useMutation({ mutationFn: () => billsApi.fireKot(activeBillId!), onSuccess: inv })
  const closeBill = useMutation({
    mutationFn: ({ method, discount }: { method: PaymentMethod; discount: number }) =>
      billsApi.close(activeBillId!, { payment_method: method, discount_paise: discount }),
    onSuccess: (closedBill) => { inv(); setSettleOpen(false); billsApi.print(activeBillId!).catch(() => localPrint(closedBill).catch(() => {})); if (useFeatureFlagStore.getState().billCloseUx) { toast('Bill settled ✓  Printing…'); setPrintQueued(true); setTimeout(() => setPrintQueued(false), 5000) } else useBillingStore.getState().setActiveBill(null) },
  })
  const removeItem = useMutation({ mutationFn: (id: string) => billsApi.removeItem(activeBillId!, id), onSuccess: inv })
  const updateQty = useMutation({ mutationFn: ({ itemId, quantity }: { itemId: string; quantity: number }) => billsApi.updateItem(activeBillId!, itemId, { quantity }), onSuccess: inv })
  const updatePrice = useMutation({ mutationFn: ({ itemId, override_price_paise }: { itemId: string; override_price_paise: number }) => billsApi.updateItem(activeBillId!, itemId, { override_price_paise }), onSuccess: inv })
  const voidBill = useMutation({
    mutationFn: () => billsApi.void(activeBillId!),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['bill', activeBillId] }); qc.invalidateQueries({ queryKey: ['bills', 'open'] }); qc.invalidateQueries({ queryKey: ['bills', 'recent'] }) },
  })
  const printBill = useMutation({ mutationFn: () => billsApi.print(activeBillId!).catch(() => bill ? localPrint(bill) : Promise.reject(new Error('no bill'))) })
  const updateMethod = useMutation({ mutationFn: (m: PaymentMethod) => billsApi.updatePaymentMethod(activeBillId!, m), onSuccess: inv })

  useEffect(() => {
    if (!activeBillId) return
    const handle = (e: KeyboardEvent) => {
      if (['INPUT','TEXTAREA','SELECT'].includes((e.target as HTMLElement).tagName)) return
      const sc = useShortcutStore.getState().shortcuts
      if (matchKey(e, sc.open_search)) { e.preventDefault(); commandPaletteOpen ? closeCommandPalette() : openCommandPalette() }
      if (e.key === 'Escape') closeCommandPalette()
      if (matchKey(e, sc.fire_kot)) { e.preventDefault(); if (bill?.items.some((i) => i.status === 'pending')) fireKot.mutate() }
      if (!commandPaletteOpen && matchKey(e, sc.generate_bill)) { e.preventDefault(); if (bill && bill.status !== 'billed' && bill.status !== 'void') setSettleOpen(true) }
      if (!commandPaletteOpen && matchKey(e, sc.close_bill)) { e.preventDefault(); if (bill && bill.status !== 'billed' && bill.status !== 'void' && bill.items.some((i) => i.status !== 'voided') && !closeBill.isPending) closeBill.mutate({ method: defaultMethod(bill.bill_type), discount: 0 }) }
    }
    window.addEventListener('keydown', handle)
    return () => window.removeEventListener('keydown', handle)
  }, [activeBillId, commandPaletteOpen, bill, closeBill.isPending])

  if (!activeBillId) return (
    <div className="flex-1 flex flex-col items-center justify-center gap-3 text-center">
      <UtensilsCrossed size={40} className="text-text-muted opacity-30" /><p className="text-text-secondary font-medium">No bill selected</p><p className="text-xs text-text-muted bg-bg-surface border border-sphotel-border px-3 py-1.5 rounded-full">Press <kbd className="font-mono">Space</kbd> to add items</p>
    </div>)
  if (isLoading || !bill) return <div className="flex-1 flex items-center justify-center text-text-muted text-sm">Loading…</div>

  const isClosed = bill.status === 'billed' || bill.status === 'void'
  const pending = bill.items.filter((i) => i.status === 'pending')
  const sent = bill.items.filter((i) => i.status === 'sent')
  const hasItems = bill.items.some((i) => i.status !== 'voided')

  return (
    <div className="flex-1 flex flex-col min-h-0">
      <BillHeader bill={bill} />
      <div className="flex-1 overflow-y-auto px-3 py-3 md:px-6 md:py-4 flex flex-col gap-0.5">
        {pending.length > 0 && sent.length > 0 && <p className="text-xs font-medium text-amber-400 uppercase tracking-wide mb-1">New (not sent)</p>}
        {pending.map((item) => <ItemRow key={item.id} item={item} disabled={isClosed} onRemove={() => removeItem.mutate(item.id)} onQtyChange={(q) => q < 1 ? removeItem.mutate(item.id) : updateQty.mutate({ itemId: item.id, quantity: q })} onPriceOverride={(p) => updatePrice.mutate({ itemId: item.id, override_price_paise: p })} fontSizeIdx={fontSizeIdx} />)}
        {sent.length > 0 && <p className={`text-xs font-medium uppercase tracking-wide mb-1 mt-2 ${pending.length > 0 ? 'text-status-success' : 'text-text-muted'}`}>{pending.length > 0 ? 'Sent to kitchen' : 'Items'}</p>}
        {sent.map((item) => <ItemRow key={item.id} item={item} disabled={isClosed} onRemove={() => {}} onQtyChange={() => {}} readOnly fontSizeIdx={fontSizeIdx} />)}
        {bill.items.length === 0 && <div className="flex flex-col items-center justify-center py-16"><p className="text-text-muted text-sm">Bill is empty</p><button onClick={openCommandPalette} className="mt-2 text-sm text-sphotel-accent">Press Space to add items</button></div>}
      </div>

      {!isClosed && (
        <div className="px-4 py-3 md:px-6 md:py-4 border-t border-sphotel-border flex flex-col gap-3">
          <div className="flex justify-between text-sm"><span className="text-text-secondary">Subtotal</span><span className="font-medium text-text-primary">{fmt(bill.subtotal_paise)}</span></div>
          <div className="flex gap-2">
            <button onClick={openCommandPalette} className="flex-1 py-3 md:py-2.5 bg-bg-elevated border border-sphotel-border rounded-xl text-sm text-text-secondary hover:text-text-primary flex items-center justify-center gap-1.5"><Plus size={14} />Add<kbd className="hidden md:inline text-xs opacity-50 font-mono ml-1">Space</kbd></button>
            {pending.length > 0 && bill.bill_type === 'table' && <button onClick={() => fireKot.mutate()} disabled={fireKot.isPending} className="flex-1 py-3 md:py-2.5 bg-amber-500 text-white rounded-xl text-sm font-medium hover:bg-amber-600 disabled:opacity-50 flex items-center justify-center gap-1.5"><Flame size={14} />Fire KOT<kbd className="hidden md:inline text-xs opacity-50 font-mono ml-1">⌘K</kbd></button>}
            <button onClick={() => setSettleOpen(true)} disabled={!hasItems || closeBill.isPending} className="flex-1 py-3 md:py-2.5 bg-sphotel-accent text-sphotel-accent-fg rounded-xl text-sm font-medium hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-1.5"><CreditCard size={14} />Generate Bill<kbd className="hidden md:inline text-xs opacity-50 font-mono ml-1">G</kbd><span className="hidden md:inline text-xs opacity-50">·</span><kbd className="hidden md:inline text-xs opacity-50 font-mono">↵</kbd></button>
          </div>
          {isBiller && <button onClick={() => { if (confirm('Void this bill?')) voidBill.mutate() }} className="flex items-center justify-center gap-1.5 text-xs text-status-error hover:opacity-80 py-1"><Ban size={12} />Void bill</button>}
        </div>
      )}
      {isClosed && (
        <div className="px-4 py-3 md:px-6 md:py-4 border-t border-sphotel-border flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          {bill.status === 'billed' ? (
            <span className="text-sm font-medium text-sphotel-accent flex items-center gap-1.5">
              Settled · {fmt(bill.total_paise)} via
              <select value={bill.payment_method ?? 'cash'} onChange={(e) => updateMethod.mutate(e.target.value as PaymentMethod)} className="bg-transparent text-sphotel-accent font-medium text-sm border-0 outline-none cursor-pointer">
                {(['cash','card','upi','online'] as PaymentMethod[]).map(m => <option key={m} value={m} className="bg-bg-surface text-text-primary">{m}</option>)}
              </select>
            </span>
          ) : (
            <p className="text-sm font-medium text-status-error">This bill has been voided</p>
          )}
          <div className="flex items-center gap-3">
            {isBiller && bill.status === 'billed' && <button onClick={() => { if (confirm('Void this bill?')) voidBill.mutate() }} className="flex items-center gap-1.5 text-xs text-status-error hover:opacity-80 py-1"><Ban size={12} />Void bill</button>}
            {bill.status === 'billed' && <button onClick={() => printBill.mutate()} disabled={printBill.isPending} className="flex items-center gap-1.5 text-xs text-text-muted hover:text-text-primary disabled:opacity-50"><Printer size={13} />{printQueued ? 'Printing…' : printBill.isPending ? 'Queued…' : 'Reprint'}</button>}
          </div>
        </div>
      )}

      {commandPaletteOpen && <CommandPalette billId={activeBillId} billType={bill.bill_type} platform={bill.platform} />}
      {settleOpen && <SettleDialog bill={bill} onClose={() => setSettleOpen(false)} onSettle={(m, d) => closeBill.mutate({ method: m, discount: d })} isLoading={closeBill.isPending} />}
    </div>
  )
}
