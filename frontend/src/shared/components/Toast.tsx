import { useEffect } from 'react'
import { useToastStore } from '@/lib/toast'

export function Toast() {
  const { message, dismiss } = useToastStore()

  useEffect(() => {
    if (!message) return
    const t = setTimeout(dismiss, 3000)
    return () => clearTimeout(t)
  }, [message, dismiss])

  if (!message) return null

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 bg-bg-elevated border border-sphotel-border rounded-xl px-5 py-3 text-sm text-text-primary shadow-xl">
      {message}
    </div>
  )
}
