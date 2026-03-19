import { useState } from 'react'
import {
  useCreateStaff,
  useDeactivateStaff,
  useResetPin,
  useRevokeSessions,
  useStaffList,
} from './hooks/useStaff'
import type { CreateStaffPayload, StaffMember, UserRole } from './api/staff'

// Roles that can be assigned by Admin (FR87: strictly below Admin level = 3)
const ASSIGNABLE_ROLES: UserRole[] = ['biller', 'waiter', 'kitchen_staff', 'manager']

const ROLE_LABELS: Record<UserRole, string> = {
  biller: 'Biller',
  waiter: 'Waiter',
  kitchen_staff: 'Kitchen Staff',
  manager: 'Manager',
  admin: 'Admin',
  super_admin: 'Super Admin',
}

const ROLE_BADGE_CLASS: Record<UserRole, string> = {
  biller: 'bg-blue-100 text-blue-800',
  waiter: 'bg-purple-100 text-purple-800',
  kitchen_staff: 'bg-orange-100 text-orange-800',
  manager: 'bg-green-100 text-green-800',
  admin: 'bg-red-100 text-red-800',
  super_admin: 'bg-gray-900 text-white',
}

// ── Create Staff Modal ────────────────────────────────────────────────────────
interface CreateModalProps {
  onClose: () => void
}

function CreateStaffModal({ onClose }: CreateModalProps) {
  const [name, setName] = useState('')
  const [role, setRole] = useState<UserRole>('biller')
  const [pin, setPin] = useState('')
  const [error, setError] = useState('')

  const { mutate: createStaff, isPending } = useCreateStaff()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (pin.length < 4 || pin.length > 8) {
      setError('PIN must be 4–8 digits')
      return
    }
    const payload: CreateStaffPayload = { name, role, pin }
    createStaff(payload, {
      onSuccess: () => onClose(),
      onError: (err) => setError(err.message),
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800">
        <h2 className="mb-4 text-lg font-semibold">Add Staff Member</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Name</label>
            <input
              className="w-full rounded border px-3 py-2 text-sm"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              minLength={1}
              maxLength={100}
              placeholder="Full name"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Role</label>
            <select
              className="w-full rounded border px-3 py-2 text-sm"
              value={role}
              onChange={(e) => setRole(e.target.value as UserRole)}
            >
              {ASSIGNABLE_ROLES.map((r) => (
                <option key={r} value={r}>
                  {ROLE_LABELS[r]}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">PIN (4–8 digits)</label>
            <input
              className="w-full rounded border px-3 py-2 text-sm"
              type="password"
              inputMode="numeric"
              pattern="[0-9]{4,8}"
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))}
              required
              minLength={4}
              maxLength={8}
              placeholder="••••"
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded border px-4 py-2 text-sm"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isPending}
              className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {isPending ? 'Creating…' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ── Reset PIN Modal ───────────────────────────────────────────────────────────
interface ResetPinModalProps {
  staff: StaffMember
  onClose: () => void
}

function ResetPinModal({ staff, onClose }: ResetPinModalProps) {
  const [pin, setPin] = useState('')
  const [error, setError] = useState('')
  const { mutate: resetPin, isPending } = useResetPin()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (pin.length < 4 || pin.length > 8) {
      setError('PIN must be 4–8 digits')
      return
    }
    resetPin(
      { id: staff.id, payload: { pin } },
      {
        onSuccess: () => onClose(),
        onError: (err) => setError(err.message),
      },
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-sm rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800">
        <h2 className="mb-4 text-lg font-semibold">
          Reset PIN — {staff.name}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">New PIN (4–8 digits)</label>
            <input
              className="w-full rounded border px-3 py-2 text-sm"
              type="password"
              inputMode="numeric"
              pattern="[0-9]{4,8}"
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))}
              required
              minLength={4}
              maxLength={8}
              placeholder="••••"
              autoFocus
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex justify-end gap-2">
            <button type="button" onClick={onClose} className="rounded border px-4 py-2 text-sm">
              Cancel
            </button>
            <button
              type="submit"
              disabled={isPending}
              className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {isPending ? 'Saving…' : 'Save PIN'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ── Staff Row Actions ─────────────────────────────────────────────────────────
interface RowActionsProps {
  member: StaffMember
  onResetPin: (m: StaffMember) => void
}

function StaffRowActions({ member, onResetPin }: RowActionsProps) {
  const { mutate: deactivate, isPending: isDeactivating } = useDeactivateStaff()
  const { mutate: revoke, isPending: isRevoking } = useRevokeSessions()

  return (
    <div className="flex gap-2">
      <button
        className="rounded border px-2 py-1 text-xs hover:bg-gray-50"
        onClick={() => onResetPin(member)}
      >
        Reset PIN
      </button>
      {member.is_active && (
        <button
          className="rounded border border-yellow-400 px-2 py-1 text-xs text-yellow-700 hover:bg-yellow-50 disabled:opacity-50"
          disabled={isDeactivating}
          onClick={() => deactivate(member.id)}
        >
          {isDeactivating ? '…' : 'Deactivate'}
        </button>
      )}
      <button
        className="rounded border border-red-400 px-2 py-1 text-xs text-red-700 hover:bg-red-50 disabled:opacity-50"
        disabled={isRevoking}
        onClick={() => revoke(member.id)}
      >
        {isRevoking ? '…' : 'Revoke Sessions'}
      </button>
    </div>
  )
}

// ── Main Component ────────────────────────────────────────────────────────────
export function StaffManagement() {
  const { data: staff, isLoading, isError } = useStaffList()
  const [showCreate, setShowCreate] = useState(false)
  const [resetTarget, setResetTarget] = useState<StaffMember | null>(null)

  if (isLoading) {
    return <div className="p-8 text-sm text-gray-500">Loading staff…</div>
  }

  if (isError) {
    return (
      <div className="p-8 text-sm text-red-600">
        Failed to load staff. Please refresh.
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold">Staff Management</h1>
        <button
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          onClick={() => setShowCreate(true)}
        >
          + Add Staff
        </button>
      </div>

      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:bg-gray-700">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Role</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
            {staff?.length === 0 && (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-gray-400">
                  No staff members yet. Add one to get started.
                </td>
              </tr>
            )}
            {staff?.map((member) => (
              <tr key={member.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td className="px-4 py-3 font-medium">{member.name}</td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${ROLE_BADGE_CLASS[member.role]}`}
                  >
                    {ROLE_LABELS[member.role]}
                  </span>
                </td>
                <td className="px-4 py-3">
                  {member.is_active ? (
                    <span className="text-green-600">Active</span>
                  ) : (
                    <span className="text-gray-400">Inactive</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <StaffRowActions
                    member={member}
                    onResetPin={setResetTarget}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showCreate && <CreateStaffModal onClose={() => setShowCreate(false)} />}
      {resetTarget && (
        <ResetPinModal
          staff={resetTarget}
          onClose={() => setResetTarget(null)}
        />
      )}
    </div>
  )
}
