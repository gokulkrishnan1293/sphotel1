import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { authApi } from '@/features/auth/api/auth'
import { applyTheme, getStoredTheme, getSystemTheme, type Theme } from '@/lib/theme'
import { applyAccent, getStoredAccent, ACCENT_PRESETS } from '@/lib/accent'

export function useAppearance() {
  const [activeTheme, setActiveTheme] = useState<Theme>(() => getStoredTheme() ?? getSystemTheme())
  const [activeAccent, setActiveAccent] = useState(() => getStoredAccent()?.name ?? 'violet')
  const isDark = activeTheme !== 'light'
  const themeMutation = useMutation({ mutationFn: (t: Theme) => authApi.updatePreferences(t) })

  function handleTheme(theme: Theme) {
    setActiveTheme(theme)
    applyTheme(theme)
    themeMutation.mutate(theme)
    const p = ACCENT_PRESETS.find((p) => p.name === activeAccent)
    if (p) applyAccent(p, theme !== 'light')
  }

  function handleAccent(name: string) {
    const p = ACCENT_PRESETS.find((p) => p.name === name)
    if (!p) return
    setActiveAccent(name)
    applyAccent(p, isDark)
  }

  return { activeTheme, activeAccent, isDark, handleTheme, handleAccent }
}
