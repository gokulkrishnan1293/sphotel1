export type Theme = 'dark' | 'high_contrast' | 'light'

const STORAGE_KEY = 'sphotel-theme'

export function applyTheme(theme: Theme): void {
  const html = document.documentElement
  html.classList.remove('dark', 'high-contrast')
  html.setAttribute('data-theme', theme)

  if (theme === 'dark') {
    html.classList.add('dark')
  } else if (theme === 'high_contrast') {
    html.classList.add('dark', 'high-contrast')
  }
  // 'light': no classes added — [data-theme="light"] CSS handles styling

  localStorage.setItem(STORAGE_KEY, theme)
}

export function getSystemTheme(): 'dark' | 'light' {
  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light'
}

export function getStoredTheme(): Theme | null {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'dark' || stored === 'high_contrast' || stored === 'light') {
    return stored
  }
  return null
}
