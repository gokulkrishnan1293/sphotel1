import { create } from 'zustand'

interface ToastState {
  message: string | null
  show: (msg: string) => void
  dismiss: () => void
}

export const useToastStore = create<ToastState>((set) => ({
  message: null,
  show: (msg) => set({ message: msg }),
  dismiss: () => set({ message: null }),
}))

export function toast(msg: string) {
  useToastStore.getState().show(msg)
}
