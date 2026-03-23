import { openDB, type IDBPDatabase } from 'idb'

interface SphotelDB {
  bills: {
    key: string
    value: { id: string; data: any; updatedAt: number }
  }
  menu_cache: {
    key: string
    value: { id: string; data: any; cachedAt: number }
  }
  snapshots: {
    key: string
    value: { billId: string; data: any; savedAt: number }
  }
  offline_queue: {
    key: number
    value: { op: string; payload: any; createdAt: number }
    autoIncrement: true
  }
  waiters_cache: {
    key: string
    value: { id: string; data: any; cachedAt: number }
  }
  vendors_cache: {
    key: string
    value: { id: string; data: any; cachedAt: number }
  }
}

let dbPromise: Promise<IDBPDatabase<SphotelDB>> | null = null

export function getDb(): Promise<IDBPDatabase<SphotelDB>> {
  if (!dbPromise) {
    dbPromise = openDB<SphotelDB>('sphotel', 2, {
      upgrade(db) {
        if (!db.objectStoreNames.contains('bills')) {
          db.createObjectStore('bills', { keyPath: 'id' })
        }
        if (!db.objectStoreNames.contains('menu_cache')) {
          db.createObjectStore('menu_cache', { keyPath: 'id' })
        }
        if (!db.objectStoreNames.contains('snapshots')) {
          db.createObjectStore('snapshots', { keyPath: 'billId' })
        }
        if (!db.objectStoreNames.contains('offline_queue')) {
          db.createObjectStore('offline_queue', { autoIncrement: true })
        }
        if (!db.objectStoreNames.contains('waiters_cache')) {
          db.createObjectStore('waiters_cache', { keyPath: 'id' })
        }
        if (!db.objectStoreNames.contains('vendors_cache')) {
          db.createObjectStore('vendors_cache', { keyPath: 'id' })
        }
      },
    })
  }
  return dbPromise
}
