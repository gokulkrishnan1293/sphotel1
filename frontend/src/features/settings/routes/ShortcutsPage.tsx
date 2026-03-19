import { useState, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { shortcutsApi } from '../api/shortcuts'
import { useShortcutStore, DEFAULT_SHORTCUTS } from '@/lib/shortcutStore'
import type { ShortcutMap } from '@/lib/shortcutStore'

const LABELS: Record<keyof ShortcutMap, string> = {
  open_search: 'Open item search',
  fire_kot: 'Fire KOT',
  generate_bill: 'Open bill dialog',
  close_bill: 'Quick close bill',
  new_bill: 'New bill',
}

const INPUT = 'bg-bg-elevated border border-sphotel-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent font-mono w-32'

export function ShortcutsPage() {
  const { data: saved } = useQuery({ queryKey: ['shortcuts'], queryFn: shortcutsApi.get })
  const setShortcuts = useShortcutStore((s) => s.setShortcuts)
  const [form, setForm] = useState<ShortcutMap>({ ...DEFAULT_SHORTCUTS })
  const [msg, setMsg] = useState('')

  useEffect(() => {
    if (saved) { setForm(saved); setShortcuts(saved) }
  }, [saved, setShortcuts])

  const save = useMutation({
    mutationFn: () => shortcutsApi.update(form),
    onSuccess: (data) => { setShortcuts(data); setMsg('Saved') },
    onError: () => setMsg('Save failed'),
  })

  return (
    <div className="max-w-lg mx-auto px-4 md:px-8 py-6 space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-text-primary">Keyboard Shortcuts</h1>
        <p className="text-sm text-text-muted mt-1">
          Use a letter like <code className="font-mono text-xs">g</code>, a modifier combo like{' '}
          <code className="font-mono text-xs">ctrl+k</code>, or a function key like{' '}
          <code className="font-mono text-xs">F3</code>.
        </p>
      </div>

      <div className="space-y-3">
        {(Object.keys(LABELS) as (keyof ShortcutMap)[]).map((k) => (
          <div key={k} className="flex items-center justify-between gap-4">
            <label className="text-sm text-text-primary">{LABELS[k]}</label>
            <input
              className={INPUT}
              value={form[k]}
              onChange={(e) => setForm((f) => ({ ...f, [k]: e.target.value }))}
              placeholder={DEFAULT_SHORTCUTS[k]}
            />
          </div>
        ))}
      </div>

      {msg && <p className="text-sm text-sphotel-accent">{msg}</p>}

      <div className="flex gap-3">
        <button
          onClick={() => { setMsg(''); save.mutate() }}
          disabled={save.isPending}
          className="px-4 py-2 bg-sphotel-accent text-sphotel-accent-fg rounded-lg text-sm font-medium hover:opacity-90 disabled:opacity-50"
        >
          {save.isPending ? 'Saving…' : 'Save shortcuts'}
        </button>
        <button
          onClick={() => { setForm({ ...DEFAULT_SHORTCUTS }); setMsg('') }}
          className="px-4 py-2 bg-bg-elevated border border-sphotel-border rounded-lg text-sm text-text-secondary hover:text-text-primary"
        >
          Reset to defaults
        </button>
      </div>
    </div>
  )
}
