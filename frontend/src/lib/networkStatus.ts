import { useEffect } from 'react'
import { create } from 'zustand'

interface NetworkState {
  isOnline: boolean
  setOnline: (v: boolean) => void
}

export const useNetworkStore = create<NetworkState>((set) => ({
  isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
  setOnline: (v) => set({ isOnline: v }),
}))

export function useNetworkWatcher(): void {
  const setOnline = useNetworkStore((s) => s.setOnline)

  useEffect(() => {
    setOnline(navigator.onLine)

    const handleOnline = () => setOnline(true)
    const handleOffline = () => setOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    const poll = setInterval(async () => {
      try {
        const res = await fetch('/api/v1/health', { method: 'HEAD' })
        setOnline(res.ok)
      } catch {
        setOnline(false)
      }
    }, 30_000)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
      clearInterval(poll)
    }
  }, [setOnline])
}
