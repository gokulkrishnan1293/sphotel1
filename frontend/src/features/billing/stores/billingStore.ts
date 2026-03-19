import { create } from 'zustand'

interface BillingState {
  activeBillId: string | null
  commandPaletteOpen: boolean
  setActiveBill: (id: string | null) => void
  openCommandPalette: () => void
  closeCommandPalette: () => void
}

export const useBillingStore = create<BillingState>((set) => ({
  activeBillId: null,
  commandPaletteOpen: false,
  setActiveBill: (id) => set({ activeBillId: id }),
  openCommandPalette: () => set({ commandPaletteOpen: true }),
  closeCommandPalette: () => set({ commandPaletteOpen: false }),
}))
