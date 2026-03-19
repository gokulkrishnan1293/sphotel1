import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { Providers } from './providers'

describe('Providers', () => {
  it('renders children without crashing', () => {
    const { getByText } = render(
      <Providers><div>child content</div></Providers>
    )
    expect(getByText('child content')).toBeTruthy()
  })
})
