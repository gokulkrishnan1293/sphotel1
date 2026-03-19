import { create } from 'zustand'

export type FeatureFlagKey =
  | 'waiterMode'
  | 'suggestionEngine'
  | 'telegramAlerts'
  | 'gstModule'
  | 'payrollRewards'
  | 'discountComplimentary'
  | 'waiterTransfer'
  | 'billCloseUx'

interface FeatureFlagsData {
  waiterMode: boolean
  suggestionEngine: boolean
  telegramAlerts: boolean
  gstModule: boolean
  payrollRewards: boolean
  discountComplimentary: boolean
  waiterTransfer: boolean
  billCloseUx: boolean
}

interface FeatureFlagsState extends FeatureFlagsData {
  setFlags: (flags: Partial<FeatureFlagsData>) => void
}

const defaultFlags: FeatureFlagsData = {
  waiterMode: false,
  suggestionEngine: false,
  telegramAlerts: false,
  gstModule: false,
  payrollRewards: false,
  discountComplimentary: false,
  waiterTransfer: false,
  billCloseUx: false,
}

export const useFeatureFlagStore = create<FeatureFlagsState>((set) => ({
  ...defaultFlags,
  setFlags: (flags) => set((state) => ({ ...state, ...flags })),
}))
