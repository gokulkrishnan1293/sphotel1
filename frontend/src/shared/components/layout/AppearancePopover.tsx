import type { Theme } from '@/lib/theme'
import { ACCENT_PRESETS } from '@/lib/accent'

const MODES: { value: Theme; label: string }[] = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'high_contrast', label: 'Hi-C' },
]

interface Props {
  activeTheme: Theme
  activeAccent: string
  onTheme: (theme: Theme) => void
  onAccent: (name: string) => void
  onClose: () => void
}

export function AppearancePopover({ activeTheme, activeAccent, onTheme, onAccent, onClose }: Props) {
  return (
    <>
      <div className="fixed inset-0 z-40" onClick={onClose} />
      <div className="absolute bottom-0 left-full ml-2 z-50 bg-bg-elevated border border-sphotel-border rounded-xl shadow-xl p-4 w-52">
        <p className="text-xs font-medium text-text-muted uppercase tracking-wide mb-2">Mode</p>
        <div className="flex gap-1 mb-4">
          {MODES.map(({ value, label }) => (
            <button key={value} onClick={() => onTheme(value)}
              className={`flex-1 py-1.5 rounded-lg text-xs font-medium transition-colors ${activeTheme === value ? 'bg-sphotel-accent text-sphotel-accent-fg' : 'bg-bg-base text-text-secondary hover:text-text-primary'}`}>
              {label}
            </button>
          ))}
        </div>
        <p className="text-xs font-medium text-text-muted uppercase tracking-wide mb-2">Accent</p>
        <div className="grid grid-cols-6 gap-1.5">
          {ACCENT_PRESETS.map((preset) => (
            <button key={preset.name} title={preset.name} onClick={() => onAccent(preset.name)}
              style={{ backgroundColor: preset.color }}
              className={`w-7 h-7 rounded-full transition-transform hover:scale-110 ${activeAccent === preset.name ? 'ring-2 ring-white ring-offset-2 ring-offset-bg-elevated scale-110' : ''}`}
            />
          ))}
        </div>
      </div>
    </>
  )
}
