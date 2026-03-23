import { getDb } from './schema'
import type { VendorItem } from '../../features/settings/api/onlineVendors'
import { apiClient } from '../api'

const STALE_MS = 24 * 60 * 60 * 1000

export async function writeVendorsCache(vendors: VendorItem[]): Promise<void> {
  const db = await getDb()
  const tx = db.transaction('vendors_cache', 'readwrite')
  await tx.store.clear()
  await Promise.all(vendors.map((v) =>
    tx.store.put({ id: v.slug, data: v, cachedAt: Date.now() })
  ))
  await tx.done
}

export async function readVendorsCache(): Promise<VendorItem[] | null> {
  const db = await getDb()
  const all = await db.getAll('vendors_cache')
  if (!all.length) return null
  if (Date.now() - all[0].cachedAt > STALE_MS) return null
  return all.map((r) => r.data as VendorItem)
}

/** Drop-in replacement for vendorsApi.list() — caches on success, serves IDB on failure. */
export async function vendorsListWithCache(): Promise<VendorItem[]> {
  try {
    const vendors = (await apiClient.get<VendorItem[]>('/api/v1/tenants/me/online-vendors')).data
    writeVendorsCache(vendors).catch(() => {})
    return vendors
  } catch {
    const cached = await readVendorsCache()
    if (cached) return cached
    throw new Error('Vendors not available offline — load the app once while connected')
  }
}
