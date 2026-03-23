import { getDb } from './schema'

export type OpName = 'openBill' | 'addItem' | 'removeItem' | 'updateItem' | 'closeBill' | 'voidBill' | 'fireKot'

export interface QueueEntry {
  op: OpName
  payload: unknown
  createdAt: number
}

export async function enqueue(op: OpName, payload: unknown): Promise<void> {
  const db = await getDb()
  await db.add('offline_queue', { op, payload, createdAt: Date.now() })
}

export async function peekAll(): Promise<Array<{ key: number; entry: QueueEntry }>> {
  const db = await getDb()
  const [keys, values] = await Promise.all([
    db.getAllKeys('offline_queue'),
    db.getAll('offline_queue'),
  ])
  return (keys as number[]).map((key, i) => ({ key, entry: values[i] as QueueEntry }))
}

export async function dequeue(key: number): Promise<void> {
  const db = await getDb()
  await db.delete('offline_queue', key)
}

export async function queueSize(): Promise<number> {
  const db = await getDb()
  return db.count('offline_queue')
}
