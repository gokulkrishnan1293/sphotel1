import { describe, it, expect, beforeEach } from 'vitest'
import { useFeatureFlagStore } from './featureFlagStore'

describe('useFeatureFlagStore', () => {
  beforeEach(() => {
    // Reset store to defaults before each test
    useFeatureFlagStore.getState().setFlags({
      waiterMode: false,
      suggestionEngine: false,
      telegramAlerts: false,
      gstModule: false,
      payrollRewards: false,
      discountComplimentary: false,
      waiterTransfer: false,
    })
  })

  it('initializes with all flags false', () => {
    const state = useFeatureFlagStore.getState()
    expect(state.waiterMode).toBe(false)
    expect(state.suggestionEngine).toBe(false)
    expect(state.telegramAlerts).toBe(false)
    expect(state.gstModule).toBe(false)
    expect(state.payrollRewards).toBe(false)
    expect(state.discountComplimentary).toBe(false)
    expect(state.waiterTransfer).toBe(false)
  })

  it('setFlags updates specified flags only', () => {
    useFeatureFlagStore.getState().setFlags({ waiterMode: true, gstModule: true })
    const state = useFeatureFlagStore.getState()
    expect(state.waiterMode).toBe(true)
    expect(state.gstModule).toBe(true)
    // Other flags remain false
    expect(state.suggestionEngine).toBe(false)
    expect(state.telegramAlerts).toBe(false)
  })

  it('setFlags with all flags updates them all', () => {
    useFeatureFlagStore.getState().setFlags({
      waiterMode: true,
      suggestionEngine: true,
      telegramAlerts: true,
      gstModule: true,
      payrollRewards: true,
      discountComplimentary: true,
      waiterTransfer: true,
    })
    const state = useFeatureFlagStore.getState()
    expect(state.waiterMode).toBe(true)
    expect(state.suggestionEngine).toBe(true)
    expect(state.waiterTransfer).toBe(true)
  })

  it('setFlags can disable a previously enabled flag', () => {
    useFeatureFlagStore.getState().setFlags({ waiterMode: true })
    expect(useFeatureFlagStore.getState().waiterMode).toBe(true)
    useFeatureFlagStore.getState().setFlags({ waiterMode: false })
    expect(useFeatureFlagStore.getState().waiterMode).toBe(false)
  })
})
