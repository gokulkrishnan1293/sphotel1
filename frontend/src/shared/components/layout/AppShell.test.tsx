import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AppShell } from './AppShell'

function wrapper({ children }: { children: React.ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

describe('AppShell', () => {
  it('renders a sidebar and main content area', () => {
    const { container } = render(<AppShell />, { wrapper })
    expect(container.querySelector('aside')).toBeTruthy()
    expect(container.querySelector('main')).toBeTruthy()
  })

  it('renders children inside main content', () => {
    const { getByText } = render(<AppShell><span>hello</span></AppShell>, { wrapper })
    expect(getByText('hello')).toBeTruthy()
  })

  it('sidebar has 240px width class', () => {
    const { container } = render(<AppShell />, { wrapper })
    const aside = container.querySelector('aside')
    expect(aside?.className).toContain('w-60')
  })
})
