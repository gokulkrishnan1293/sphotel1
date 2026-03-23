import { useRegisterSW } from 'virtual:pwa-register/react'

export function UpdateBanner() {
  const { needRefresh: [needRefresh], updateServiceWorker } = useRegisterSW()

  if (!needRefresh) return null

  return (
    <div className="sticky top-0 z-50 w-full bg-sphotel-accent px-4 py-2 flex items-center justify-between text-sm font-medium text-white">
      <span>New version available — update to get the latest changes.</span>
      <button
        onClick={() => updateServiceWorker(true)}
        className="ml-4 shrink-0 rounded bg-white/20 px-3 py-1 text-xs font-semibold hover:bg-white/30 transition-colors"
      >
        Reload now
      </button>
    </div>
  )
}
