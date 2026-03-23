import { getDb } from './schema'
import type { WaiterView } from '../../features/admin/types/staff'
import { apiClient } from '../api'

const STALE_MS = 24 * 60 * 60 * 1000

export async function writeWaitersCache(waiters: WaiterView[]): Promise<void> {
  const db = await getDb()
  const tx = db.transaction('waiters_cache', 'readwrite')
  await tx.store.clear()
  await Promise.all(waiters.map((w) =>
    tx.store.put({ id: w.id, data: w, cachedAt: Date.now() })
  ))
  await tx.done
}

export async function readWaitersCache(): Promise<WaiterView[] | null> {
  const db = await getDb()
  const all = await db.getAll('waiters_cache')
  if (!all.length) return null
  if (Date.now() - all[0].cachedAt > STALE_MS) return null
  return all.map((r) => r.data as WaiterView)
}

/** Drop-in replacement for staffApi.listWaiters() — caches on success, serves IDB on failure. */
export async function waitersListWithCache(): Promise<WaiterView[]> {
  try {
    const waiters = (await apiClient.get<WaiterView[]>('/api/v1/staff/waiters')).data
    writeWaitersCache(waiters).catch(() => {})
    return waiters
  } catch {
    const cached = await readWaitersCache()
    if (cached) return cached
    throw new Error('Waiters not available offline — load the app once while connected')
  }
}
