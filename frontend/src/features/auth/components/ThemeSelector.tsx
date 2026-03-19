import { useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import { authApi } from '../api/auth'
import { applyTheme, type Theme } from '../../../lib/theme'

const THEMES: { value: Theme; label: string }[] = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'high_contrast', label: 'High Contrast' },
]

export function ThemeSelector() {
  const currentUser = useAuthStore((s) => s.currentUser)
  const setCurrentUser = useAuthStore((s) => s.setCurrentUser)
  const currentTheme = currentUser?.preferences?.theme as Theme | undefined
  const [pending, setPending] = useState(false)

  async function handleSelect(theme: Theme) {
    if (pending) return
    setPending(true)
    try {
      applyTheme(theme) // Apply instantly (optimistic)
      const updated = await authApi.updatePreferences(theme)
      setCurrentUser(updated)
    } finally {
      setPending(false)
    }
  }

  return (
    <div className="flex gap-2">
      {THEMES.map(({ value, label }) => (
        <button
          key={value}
          onClick={() => handleSelect(value)}
          disabled={pending}
          className={[
            'px-3 py-1.5 rounded text-sm font-medium transition-colors',
            currentTheme === value
              ? 'bg-[var(--sphotel-accent)] text-white'
              : 'bg-[var(--bg-elevated)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]',
          ].join(' ')}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
