import { create } from 'zustand'

export interface ShortcutMap {
  open_search: string
  fire_kot: string
  generate_bill: string
  close_bill: string
  new_bill: string
}

export const DEFAULT_SHORTCUTS: ShortcutMap = {
  open_search: 'Space',
  fire_kot: 'ctrl+k',
  generate_bill: 'g',
  close_bill: 'Enter',
  new_bill: 'n',
}

interface ShortcutState {
  shortcuts: ShortcutMap
  setShortcuts: (s: Partial<ShortcutMap>) => void
}

export const useShortcutStore = create<ShortcutState>((set) => ({
  shortcuts: { ...DEFAULT_SHORTCUTS },
  setShortcuts: (s) => set((st) => ({ shortcuts: { ...st.shortcuts, ...s } })),
}))

export function matchKey(e: KeyboardEvent, shortcut: string): boolean {
  const parts = shortcut.toLowerCase().split('+')
  const mod = parts.length > 1 ? parts[0] : null
  const key = parts[parts.length - 1]
  if (mod === 'ctrl' && !e.ctrlKey && !e.metaKey) return false
  if (mod === 'shift' && !e.shiftKey) return false
  if (mod === 'alt' && !e.altKey) return false
  if (key === 'space') return e.code === 'Space'
  if (/^f\d+$/.test(key)) return e.key.toLowerCase() === key
  return e.key.toLowerCase() === key
}
