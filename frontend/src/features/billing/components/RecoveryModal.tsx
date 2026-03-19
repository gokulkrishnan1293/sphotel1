import { useEffect, useState } from 'react'
import { getDb } from '@/lib/db/schema'
import { useBillingStore } from '@/features/billing/stores/billingStore'

interface Snapshot {
  billId: string
  data: { activeBillId: string | null }
  savedAt: number
}

export function RecoveryModal() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null)
  const setActiveBill = useBillingStore((s) => s.setActiveBill)

  useEffect(() => {
    const check = async () => {
      const db = await getDb()
      const all = await db.getAll('snapshots')
      const cutoff = Date.now() - 10 * 60 * 1000
      const recent = all.find((s) => s.savedAt > cutoff)
      if (recent) setSnapshot(recent as Snapshot)
    }
    check().catch(console.error)
  }, [])

  if (!snapshot) return null

  const minutesAgo = Math.round((Date.now() - snapshot.savedAt) / 60_000)

  const dismiss = async () => {
    const db = await getDb()
    await db.delete('snapshots', snapshot.billId)
    setSnapshot(null)
  }

  const restore = async () => {
    setActiveBill(snapshot.data.activeBillId)
    await dismiss()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-sm rounded-2xl bg-bg-elevated border border-sphotel-border p-6 shadow-2xl">
        <h2 className="mb-2 text-base font-semibold text-text-primary">Recover unsaved session?</h2>
        <p className="mb-6 text-sm text-text-secondary">
          Found a session from {minutesAgo} minute{minutesAgo !== 1 ? 's' : ''} ago with a bill open. Restore it?
        </p>
        <div className="flex justify-end gap-3">
          <button onClick={dismiss} className="rounded-lg px-4 py-2 text-sm text-text-secondary border border-sphotel-border hover:bg-bg-base">
            Dismiss
          </button>
          <button onClick={restore} className="rounded-lg bg-sphotel-accent text-sphotel-accent-fg px-4 py-2 text-sm font-medium">
            Restore
          </button>
        </div>
      </div>
    </div>
  )
}
