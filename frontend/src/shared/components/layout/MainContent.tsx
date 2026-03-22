import { type ReactNode } from 'react'

interface MainContentProps {
  children?: ReactNode
}

export function MainContent({ children }: MainContentProps) {
  return (
    <main className="flex-1 min-h-0 overflow-hidden flex flex-col bg-bg-base pb-14 md:pb-0">
      {children}
    </main>
  )
}
