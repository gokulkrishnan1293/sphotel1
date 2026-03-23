import { useEffect, useRef } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useNetworkStore } from '@/lib/networkStatus'
import { peekAll, dequeue } from '@/lib/db/offlineQueue'
import { getDb } from '@/lib/db/schema'
import { billsApi } from '../api/bills'
import { toast } from '@/lib/toast'
import type { QueueEntry } from '@/lib/db/offlineQueue'

/**
 * idMap: maps offline temp bill IDs → real server IDs.
 * Built up as openBill ops are replayed; subsequent addItem/close ops use it.
 */
async function replayOp(entry: QueueEntry, idMap: Record<string, string>): Promise<void> {
  const p = entry.payload as any
  const billId = idMap[p.billId] ?? p.billId

  if (entry.op === 'openBill') {
    const real = await billsApi.open(p.data)   // offline() is false now — goes to server
    idMap[p.tempId] = real.id
    const db = await getDb()
    await db.delete('bills', p.tempId)         // remove temp bill from IDB
    return
  }
  if (entry.op === 'addItem')    return billsApi.addItem(billId, p.data).then(() => undefined)
  if (entry.op === 'removeItem') return billsApi.removeItem(billId, p.itemId)
  if (entry.op === 'updateItem') return billsApi.updateItem(billId, p.itemId, p.data).then(() => undefined)
  if (entry.op === 'closeBill')  return billsApi.close(billId, p.data).then(() => undefined)
  if (entry.op === 'voidBill')   return billsApi.void(billId).then(() => undefined)
  if (entry.op === 'fireKot')    return billsApi.fireKot(billId).then(() => undefined)
  throw new Error('Unknown queued op: ' + entry.op)
}

export function useOfflineSync() {
  const isOnline = useNetworkStore((s) => s.isOnline)
  const qc = useQueryClient()
  const wasOffline = useRef(false)

  useEffect(() => {
    if (!isOnline) { wasOffline.current = true; return }
    if (!wasOffline.current) return
    wasOffline.current = false
    ;(async () => {
      const ops = await peekAll()
      if (!ops.length) return
      const idMap: Record<string, string> = {}
      let synced = 0
      for (const { key, entry } of ops) {
        try { await replayOp(entry, idMap); await dequeue(key); synced++ }
        catch { break } // stop on first failure; remaining ops retry on next reconnect
      }
      if (synced) {
        qc.invalidateQueries({ queryKey: ['bills'] })
        qc.invalidateQueries({ queryKey: ['bill'] })
        toast(`Synced ${synced} offline operation${synced > 1 ? 's' : ''} ✓`)
      }
    })().catch(console.error)
  }, [isOnline, qc])
}
