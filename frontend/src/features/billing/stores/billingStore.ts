import { create } from 'zustand'

interface BillingState {
  activeBillId: string | null
  setActiveBill: (id: string | null) => void
}

export const useBillingStore = create<BillingState>((set) => ({
  activeBillId: null,
  setActiveBill: (id) => set({ activeBillId: id }),
}))
