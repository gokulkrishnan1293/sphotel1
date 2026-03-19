import { render, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { OnboardingChecklist } from './OnboardingChecklist'
import type { OnboardingStatus } from '../api/onboarding'

const MOCK_STATUS: OnboardingStatus = {
  completed: false,
  items: [
    { key: 'menu_items', label: 'Add menu items', completed: false, route: '/admin/menu' },
    { key: 'staff_pins', label: 'Add staff PINs', completed: true, route: '/admin/staff' },
    { key: 'tables', label: 'Configure tables', completed: false, route: '/admin/tables' },
  ],
}

describe('OnboardingChecklist', () => {
  it('renders all checklist items', () => {
    const { getByText } = render(
      <OnboardingChecklist
        status={MOCK_STATUS}
        onDismiss={vi.fn()}
        isPending={false}
      />,
    )
    expect(getByText('Add menu items')).toBeTruthy()
    expect(getByText('Add staff PINs')).toBeTruthy()
    expect(getByText('Configure tables')).toBeTruthy()
  })

  it('shows progress count', () => {
    const { getByText } = render(
      <OnboardingChecklist
        status={MOCK_STATUS}
        onDismiss={vi.fn()}
        isPending={false}
      />,
    )
    expect(getByText('1 of 3 steps complete')).toBeTruthy()
  })

  it('calls onDismiss when dismiss button clicked', () => {
    const onDismiss = vi.fn()
    const { getAllByRole } = render(
      <OnboardingChecklist
        status={MOCK_STATUS}
        onDismiss={onDismiss}
        isPending={false}
      />,
    )
    const buttons = getAllByRole('button', { name: /dismiss/i })
    fireEvent.click(buttons[0])
    expect(onDismiss).toHaveBeenCalledOnce()
  })

  it('disables dismiss buttons when isPending', () => {
    const { getAllByRole } = render(
      <OnboardingChecklist
        status={MOCK_STATUS}
        onDismiss={vi.fn()}
        isPending={true}
      />,
    )
    const dismissButtons = getAllByRole('button', { name: /dismiss|saving/i })
    dismissButtons.forEach((btn) => {
      expect(btn).toBeDisabled()
    })
  })

  it('shows Saving text when isPending', () => {
    const { getByText } = render(
      <OnboardingChecklist
        status={MOCK_STATUS}
        onDismiss={vi.fn()}
        isPending={true}
      />,
    )
    expect(getByText('Saving\u2026')).toBeTruthy()
  })
})
