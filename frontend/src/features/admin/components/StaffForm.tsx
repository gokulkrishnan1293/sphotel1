import { useState } from 'react'
import type { CreateStaffRequest, StaffResponse, StaffRole } from '../types/staff'

const ROLES: { value: StaffRole; label: string }[] = [
  { value: 'waiter', label: 'Waiter' },
  { value: 'biller', label: 'Biller' },
  { value: 'kitchen_staff', label: 'Kitchen' },
  { value: 'manager', label: 'Manager' },
  { value: 'admin', label: 'Admin' },
]

const INPUT = 'bg-bg-elevated border border-sphotel-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent w-full'

interface Props {
  onSubmit: (data: CreateStaffRequest) => void
  onCancel: () => void
  isPending: boolean
  editTarget?: StaffResponse
}

export function StaffForm({ onSubmit, onCancel, isPending, editTarget }: Props) {
  const [name, setName] = useState(editTarget?.name ?? '')
  const [role, setRole] = useState<StaffRole>(editTarget?.role ?? 'waiter')
  const [pin, setPin] = useState('')
  const [shortCode, setShortCode] = useState(editTarget?.short_code != null ? String(editTarget.short_code) : '')

  function submit() {
    if (!name.trim()) return
    if (!editTarget && pin.length < 4) return
    const sc = shortCode.trim()
    const parsed = sc !== '' ? Number(sc) : null
    onSubmit({ name: name.trim(), role, pin, short_code: parsed })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-bg-elevated border border-sphotel-border rounded-xl p-5 w-80 flex flex-col gap-4 shadow-xl">
        <h2 className="font-semibold text-text-primary">{editTarget ? 'Edit Staff' : 'Add Staff'}</h2>

        <div className="flex flex-col gap-3">
          <input className={INPUT} placeholder="Full name" value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') submit() }} autoFocus />

          <select className={INPUT} value={role} onChange={(e) => setRole(e.target.value as StaffRole)}>
            {ROLES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
          </select>

          <input className={INPUT} placeholder={editTarget ? 'New PIN (leave blank to keep)' : 'PIN (4–8 digits)'}
            type="password" inputMode="numeric" value={pin}
            onChange={(e) => setPin(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') submit() }} />

          <input className={INPUT} placeholder="Short code (e.g. 1, 2, 3…)" inputMode="numeric"
            value={shortCode} onChange={(e) => setShortCode(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') submit() }} />
        </div>

        <div className="flex gap-2 justify-end">
          <button onClick={onCancel}
            className="px-3 py-1.5 border border-sphotel-border rounded-lg text-sm text-text-secondary hover:bg-bg-base">
            Cancel
          </button>
          <button onClick={submit} disabled={isPending || !name.trim()}
            className="px-4 py-1.5 bg-sphotel-accent text-sphotel-accent-fg rounded-lg text-sm font-medium disabled:opacity-50">
            {editTarget ? 'Save' : 'Add'}
          </button>
        </div>
      </div>
    </div>
  )
}
