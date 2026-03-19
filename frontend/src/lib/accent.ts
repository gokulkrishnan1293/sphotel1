export interface AccentPreset {
  name: string
  color: string // swatch display color
  dark: { accent: string; hover: string; subtle: string }
  light: { accent: string; hover: string; subtle: string }
}

export const ACCENT_PRESETS: AccentPreset[] = [
  {
    name: 'violet',
    color: '#8b5cf6',
    dark:  { accent: '#8b5cf6', hover: '#a78bfa', subtle: '#2e1065' },
    light: { accent: '#7c3aed', hover: '#6d28d9', subtle: '#ede9fe' },
  },
  {
    name: 'blue',
    color: '#3b82f6',
    dark:  { accent: '#3b82f6', hover: '#60a5fa', subtle: '#1e3a8a' },
    light: { accent: '#2563eb', hover: '#1d4ed8', subtle: '#dbeafe' },
  },
  {
    name: 'emerald',
    color: '#10b981',
    dark:  { accent: '#10b981', hover: '#34d399', subtle: '#064e3b' },
    light: { accent: '#059669', hover: '#047857', subtle: '#d1fae5' },
  },
  {
    name: 'rose',
    color: '#f43f5e',
    dark:  { accent: '#f43f5e', hover: '#fb7185', subtle: '#4c0519' },
    light: { accent: '#e11d48', hover: '#be123c', subtle: '#ffe4e6' },
  },
  {
    name: 'amber',
    color: '#f59e0b',
    dark:  { accent: '#f59e0b', hover: '#fbbf24', subtle: '#451a03' },
    light: { accent: '#d97706', hover: '#b45309', subtle: '#fef3c7' },
  },
  {
    name: 'cyan',
    color: '#06b6d4',
    dark:  { accent: '#06b6d4', hover: '#22d3ee', subtle: '#164e63' },
    light: { accent: '#0891b2', hover: '#0e7490', subtle: '#cffafe' },
  },
]

const STORAGE_KEY = 'sphotel-accent'

export function applyAccent(preset: AccentPreset, isDark: boolean) {
  const vars = isDark ? preset.dark : preset.light
  const h = document.documentElement
  h.style.setProperty('--sphotel-accent', vars.accent)
  h.style.setProperty('--sphotel-accent-hover', vars.hover)
  h.style.setProperty('--sphotel-accent-subtle', vars.subtle)
  h.style.setProperty('--primary', vars.accent)
  h.style.setProperty('--ring', vars.accent)
  localStorage.setItem(STORAGE_KEY, preset.name)
}

export function getStoredAccent(): AccentPreset | null {
  const name = localStorage.getItem(STORAGE_KEY)
  return ACCENT_PRESETS.find((p) => p.name === name) ?? null
}
