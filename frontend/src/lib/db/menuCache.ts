import { getDb } from './schema'
import type { MenuItemResponse } from '../../features/admin/types/menu'
import { apiClient } from '../api'

const STALE_MS = 24 * 60 * 60 * 1000

export async function writeMenuCache(items: MenuItemResponse[]): Promise<void> {
  const db = await getDb()
  const tx = db.transaction('menu_cache', 'readwrite')
  await tx.store.clear()
  await Promise.all(items.map((item) =>
    tx.store.put({ id: item.id, data: item, cachedAt: Date.now() })
  ))
  await tx.done
}

export async function readMenuCache(): Promise<MenuItemResponse[] | null> {
  const db = await getDb()
  const all = await db.getAll('menu_cache')
  if (!all.length) return null
  if (Date.now() - all[0].cachedAt > STALE_MS) return null
  return all.map((r) => r.data as MenuItemResponse)
}

/** Drop-in replacement for menuApi.list() — caches on success, serves IDB on failure. */
export async function menuListWithCache(): Promise<MenuItemResponse[]> {
  try {
    const items = (await apiClient.get<MenuItemResponse[]>('/api/v1/menu/items')).data
    writeMenuCache(items).catch(() => {})
    return items
  } catch {
    const cached = await readMenuCache()
    if (cached) return cached
    throw new Error('Menu not available offline — load the app once while connected')
  }
}
