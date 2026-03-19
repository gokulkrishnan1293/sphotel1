import { useEffect } from 'react'
import { queryClient } from '@/lib/queryClient'
import { getDb } from '@/lib/db/schema'
import { useNetworkStore } from '@/lib/networkStatus'

const TEN_MINUTES = 10 * 60 * 1000

async function clearOldSnapshots() {
  const db = await getDb()
  const all = await db.getAll('snapshots')
  const cutoff = Date.now() - TEN_MINUTES
  await Promise.all(
    all
      .filter((s) => s.savedAt < cutoff)
      .map((s) => db.delete('snapshots', s.billId)),
  )
}

async function saveSnapshot(activeBillId: string | null) {
  const db = await getDb()
  const bills = queryClient.getQueryData(['bills'])
  const billId = activeBillId ?? 'session'
  await db.put('snapshots', {
    billId,
    data: { activeBillId, bills, savedAt: Date.now() },
    savedAt: Date.now(),
  })
}

export function useAutoSave(activeBillId: string | null) {
  const isOnline = useNetworkStore((s) => s.isOnline)

  useEffect(() => {
    clearOldSnapshots().catch(console.error)
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      saveSnapshot(activeBillId).catch(console.error)
    }, 30_000)
    return () => clearInterval(interval)
  }, [activeBillId, isOnline])
}
