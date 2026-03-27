import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Printer, Ban, RotateCcw, ShoppingBag, Laptop, UtensilsCrossed } from 'lucide-react'
import { billsApi } from '../api/bills'
import { localPrint } from '@/lib/localPrint'
import { useAuthStore } from '../../auth/stores/authStore'
import type { BillType, PaymentMethod } from '../types/bills'

const ICON: Record<BillType, React.ElementType> = { table: UtensilsCrossed, parcel: ShoppingBag, online: Laptop }
const fmt = (p: number) => `₹${(p / 100).toFixed(2)}`
const METHODS: PaymentMethod[] = ['cash', 'card', 'upi', 'online', 'other']

export function BillDetailPanel({ billId }: { billId: string }) {
  const qc = useQueryClient()
  const role = useAuthStore((s) => s.currentUser?.role ?? '')
  const isBiller = ['biller', 'admin', 'super_admin'].includes(role)
  const { data: bill, isLoading } = useQuery({ queryKey: ['bill', billId], queryFn: () => billsApi.get(billId) })
  const inv = () => qc.invalidateQueries({ queryKey: ['bill', billId] })
  const print = useMutation({ mutationFn: () => billsApi.print(billId).catch(() => bill ? localPrint(bill) : Promise.reject(new Error('no bill'))) })
  const voidBill = useMutation({ mutationFn: () => billsApi.void(billId), onSuccess: inv })
  const unvoidBill = useMutation({ mutationFn: () => billsApi.unvoid(billId), onSuccess: inv })
  const updateMethod = useMutation({ mutationFn: (m: PaymentMethod) => billsApi.updatePaymentMethod(billId, m), onSuccess: inv })

  const Icon = bill ? ICON[bill.bill_type] : null
  const typeLabel = bill?.bill_type === 'table' ? 'Dine In' : bill?.bill_type === 'parcel' ? 'Parcel' : bill?.platform ?? 'Online'
  const items = bill?.items.filter((i) => i.status !== 'voided') ?? []

  return (
    <>
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-sphotel-border shrink-0">
        <div className="flex items-center gap-2">
          {Icon && <Icon size={13} className="text-text-muted" />}
          <span className="text-sm font-semibold text-text-primary">
            {bill ? `${typeLabel} #${bill.bill_number ?? '—'}` : 'Loading…'}
          </span>
          {bill && <span className={`text-xs px-2 py-0.5 rounded-full ${bill.status === 'billed' ? 'bg-sphotel-accent-subtle text-sphotel-accent' : bill.status === 'cancelled' ? 'bg-text-muted/20 text-text-muted' : 'bg-status-error/10 text-status-error'}`}>
            {bill.status === 'billed' ? 'Settled' : bill.status === 'cancelled' ? 'Cancelled' : 'Void'}
          </span>}
        </div>
        <div className="flex items-center gap-3">
          {bill?.status === 'billed' && isBiller && <button onClick={() => { if (confirm('Void this bill?')) voidBill.mutate() }} disabled={voidBill.isPending}
            className="flex items-center gap-1 text-xs text-status-error hover:opacity-80 disabled:opacity-50">
            <Ban size={13} /> Void
          </button>}
          {bill?.status === 'void' && isBiller && bill.bill_number != null && <button onClick={() => { if (confirm('Restore this bill?')) unvoidBill.mutate() }} disabled={unvoidBill.isPending}
            className="flex items-center gap-1 text-xs text-status-success hover:opacity-80 disabled:opacity-50">
            <RotateCcw size={13} /> Unvoid
          </button>}
          {bill?.status === 'billed' && <button onClick={() => print.mutate()} disabled={print.isPending}
            className="flex items-center gap-1 text-xs text-text-muted hover:text-text-primary disabled:opacity-50">
            <Printer size={13} /> {print.isPending ? 'Printing…' : 'Reprint'}
          </button>}
        </div>
      </div>
      {isLoading && <p className="text-xs text-text-muted px-4 py-8 text-center">Loading…</p>}
      {bill && <>
        <div className="px-4 py-2 border-b border-sphotel-border shrink-0 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-text-muted">
          {bill.waiter_name && <span>Waiter: {bill.waiter_name}</span>}
          {bill.reference_no && <span>Ref: {bill.reference_no}</span>}
          <span className="ml-auto">{new Date(bill.paid_at ?? bill.created_at).toLocaleString()}</span>
        </div>
        <div className="flex-1 overflow-y-auto px-4 py-2 min-h-0">
          {items.map((item) => (
            <div key={item.id} className="flex items-center justify-between py-2 border-b border-sphotel-border/40">
              <div className="flex-1 min-w-0">
                <span className="text-sm text-text-primary">{item.name}</span>
                <span className="text-xs text-text-muted ml-2">×{item.quantity}</span>
              </div>
              <span className="text-sm font-medium text-text-primary shrink-0">{fmt((item.override_price_paise ?? item.price_paise) * item.quantity)}</span>
            </div>
          ))}
        </div>
        <div className="px-4 py-3 border-t border-sphotel-border shrink-0 flex flex-col gap-1 text-sm">
          <div className="flex justify-between text-text-secondary"><span>Subtotal</span><span>{fmt(bill.subtotal_paise)}</span></div>
          {bill.discount_paise > 0 && <div className="flex justify-between text-status-success"><span>Discount</span><span>−{fmt(bill.discount_paise)}</span></div>}
          {bill.gst_paise > 0 && <div className="flex justify-between text-text-secondary"><span>GST</span><span>{fmt(bill.gst_paise)}</span></div>}
          <div className="flex justify-between font-semibold text-text-primary border-t border-sphotel-border pt-1.5 mt-0.5">
            <span>Total</span><span>{fmt(bill.total_paise)}</span>
          </div>
          {bill.status === 'billed' && (
            <div className="flex items-center justify-between mt-1.5 flex-wrap gap-1">
              <span className="text-xs text-text-muted">Paid via</span>
              <div className="flex gap-1 flex-wrap">
                {METHODS.map((m) => (
                  <button key={m} onClick={() => updateMethod.mutate(m)} disabled={updateMethod.isPending}
                    className={`px-2 py-0.5 rounded text-xs capitalize transition-colors ${bill.payment_method === m ? 'bg-sphotel-accent text-sphotel-accent-fg' : 'bg-bg-elevated text-text-muted hover:text-text-primary'}`}>
                    {m}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </>}
    </>
  )
}
