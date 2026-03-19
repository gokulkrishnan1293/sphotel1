import { render } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'
import { FeatureGate } from './FeatureGate'
import { useFeatureFlagStore } from '@/lib/featureFlagStore'

describe('FeatureGate', () => {
  beforeEach(() => {
    // Reset all flags to false before each test
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

  it('renders children when flag is enabled', () => {
    useFeatureFlagStore.getState().setFlags({ waiterMode: true })
    const { getByText } = render(
      <FeatureGate flag="waiterMode">
        <span>Waiter Surface</span>
      </FeatureGate>
    )
    expect(getByText('Waiter Surface')).toBeTruthy()
  })

  it('renders null when flag is disabled', () => {
    const { container } = render(
      <FeatureGate flag="waiterMode">
        <span>Waiter Surface</span>
      </FeatureGate>
    )
    expect(container.firstChild).toBeNull()
  })

  it('renders fallback when flag is disabled and fallback provided', () => {
    const { getByText, queryByText } = render(
      <FeatureGate flag="gstModule" fallback={<span>Not Available</span>}>
        <span>GST Module</span>
      </FeatureGate>
    )
    expect(getByText('Not Available')).toBeTruthy()
    expect(queryByText('GST Module')).toBeNull()
  })

  it('renders children not fallback when flag is enabled', () => {
    useFeatureFlagStore.getState().setFlags({ gstModule: true })
    const { getByText, queryByText } = render(
      <FeatureGate flag="gstModule" fallback={<span>Not Available</span>}>
        <span>GST Module</span>
      </FeatureGate>
    )
    expect(getByText('GST Module')).toBeTruthy()
    expect(queryByText('Not Available')).toBeNull()
  })

  it('works for all seven flag keys', () => {
    const flags = [
      'waiterMode',
      'suggestionEngine',
      'telegramAlerts',
      'gstModule',
      'payrollRewards',
      'discountComplimentary',
      'waiterTransfer',
    ] as const

    for (const flag of flags) {
      useFeatureFlagStore.getState().setFlags({ [flag]: true })
      const { getByText } = render(
        <FeatureGate flag={flag}>
          <span>{flag}</span>
        </FeatureGate>
      )
      expect(getByText(flag)).toBeTruthy()
      // Reset for next iteration
      useFeatureFlagStore.getState().setFlags({ [flag]: false })
    }
  })
})
