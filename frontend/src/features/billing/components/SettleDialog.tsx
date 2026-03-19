import { useState } from 'react'
import type { BillResponse, PaymentMethod } from '../types/bills'

const ALL_METHODS: { value: PaymentMethod; label: string }[] = [
  { value: 'cash', label: 'Cash' },
  { value: 'card', label: 'Card' },
  { value: 'upi', label: 'UPI' },
  { value: 'wallet', label: 'Wallet' },
]

function methodsFor(billType: string) {
  if (billType === 'online') return ALL_METHODS.filter((m) => m.value === 'wallet')
  if (billType === 'parcel') return ALL_METHODS.filter((m) => ['cash', 'card', 'upi'].includes(m.value))
  return ALL_METHODS // table: all options
}

function defaultMethod(billType: string): PaymentMethod {
  return billType === 'online' ? 'wallet' : 'cash'
}

const fmt = (p: number) => `₹${(p / 100).toFixed(2)}`

interface Props {
  bill: BillResponse
  onClose: () => void
  onSettle: (method: PaymentMethod, discountPaise: number) => void
  isLoading: boolean
}

export function SettleDialog({ bill, onClose, onSettle, isLoading }: Props) {
  const methods = methodsFor(bill.bill_type)
  const [method, setMethod] = useState<PaymentMethod>(defaultMethod(bill.bill_type))
  const [discountRupees, setDiscountRupees] = useState('0')
  const discount = Math.round(parseFloat(discountRupees || '0') * 100)
  const total = Math.max(0, bill.subtotal_paise - discount)

  return (
    <div className="fixed inset-0 z-50 flex items-end md:items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-bg-surface border border-sphotel-border rounded-t-2xl md:rounded-2xl shadow-2xl p-6 w-full md:w-80 flex flex-col gap-4">
        <h2 className="font-semibold text-text-primary">Generate Bill</h2>

        <div className="bg-bg-elevated rounded-xl px-4 py-3 flex flex-col gap-1 text-sm">
          <div className="flex justify-between">
            <span className="text-text-secondary">Subtotal</span>
            <span className="text-text-primary">{fmt(bill.subtotal_paise)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-text-secondary">Discount</span>
            <span className="text-text-primary">-{fmt(discount)}</span>
          </div>
          <div className="flex justify-between font-semibold text-base border-t border-sphotel-border pt-2 mt-1">
            <span className="text-text-primary">Total</span>
            <span className="text-sphotel-accent">{fmt(total)}</span>
          </div>
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-xs text-text-secondary font-medium">Discount (₹)</label>
          <input
            className="bg-bg-elevated border border-sphotel-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent w-full"
            value={discountRupees}
            onChange={(e) => setDiscountRupees(e.target.value)}
            inputMode="decimal"
          />
        </div>

        <div className={`grid gap-1 ${methods.length === 1 ? 'grid-cols-1' : 'grid-cols-2'}`}>
          {methods.map(({ value, label }) => (
            <button key={value} onClick={() => setMethod(value)}
              className={`py-2 rounded-lg text-sm font-medium transition-colors ${
                method === value
                  ? 'bg-sphotel-accent text-sphotel-accent-fg'
                  : 'bg-bg-elevated text-text-secondary hover:text-text-primary'
              }`}>
              {label}
            </button>
          ))}
        </div>

        <div className="flex gap-2">
          <button onClick={onClose} className="flex-1 border border-sphotel-border rounded-lg py-2 text-sm text-text-secondary">
            Cancel
          </button>
          <button onClick={() => onSettle(method, discount)} disabled={isLoading}
            className="flex-1 bg-sphotel-accent text-sphotel-accent-fg rounded-lg py-2 text-sm font-medium disabled:opacity-50">
            {isLoading ? 'Generating…' : 'Generate Bill'}
          </button>
        </div>
      </div>
    </div>
  )
}
