import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2 } from 'lucide-react'
import { vendorsApi } from '../api/onlineVendors'

const INPUT = 'bg-bg-base border border-sphotel-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-sphotel-accent'

const PRESETS = [
  { slug: 'swiggy', name: 'Swiggy' },
  { slug: 'zomato', name: 'Zomato' },
  { slug: 'magicpin', name: 'Magicpin' },
  { slug: 'eatsure', name: 'EatSure' },
]

export function OnlineVendorsCard() {
  const qc = useQueryClient()
  const { data: vendors = [], isLoading } = useQuery({ queryKey: ['online-vendors'], queryFn: vendorsApi.list })
  const inv = () => qc.invalidateQueries({ queryKey: ['online-vendors'] })
  const addMut = useMutation({ mutationFn: vendorsApi.add, onSuccess: inv })
  const removeMut = useMutation({ mutationFn: vendorsApi.remove, onSuccess: inv })

  const [slug, setSlug] = useState('')
  const [name, setName] = useState('')

  function addPreset(p: { slug: string; name: string }) {
    if (vendors.some((v) => v.slug === p.slug)) return
    addMut.mutate(p)
  }

  function handleAdd(e: React.FormEvent) {
    e.preventDefault()
    const s = slug.trim().toLowerCase().replace(/\s+/g, '-')
    const n = name.trim()
    if (!s || !n) return
    addMut.mutate({ slug: s, name: n }, { onSuccess: () => { setSlug(''); setName('') } })
  }

  const existing = new Set(vendors.map((v) => v.slug))

  return (
    <div className="bg-bg-elevated border border-sphotel-border rounded-xl p-6 flex flex-col gap-4">
      <div>
        <h2 className="text-base font-semibold text-text-primary">Online Vendors</h2>
        <p className="text-sm text-text-muted mt-0.5">Platforms used for online orders. Used to select per-item online pricing.</p>
      </div>

      <div className="flex gap-2 flex-wrap">
        {PRESETS.map((p) => (
          <button key={p.slug} onClick={() => addPreset(p)} disabled={existing.has(p.slug) || addMut.isPending}
            className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${existing.has(p.slug) ? 'border-sphotel-accent text-sphotel-accent bg-sphotel-accent/10 cursor-default' : 'border-sphotel-border text-text-secondary hover:border-sphotel-accent hover:text-sphotel-accent'}`}>
            {p.name}{existing.has(p.slug) ? ' ✓' : ' +'}
          </button>
        ))}
      </div>

      {isLoading ? <p className="text-sm text-text-muted">Loading…</p> : (
        <div className="flex flex-col gap-1">
          {vendors.map((v) => (
            <div key={v.slug} className="flex items-center gap-3 py-2 px-3 bg-bg-base rounded-lg">
              <span className="text-sm text-text-primary flex-1">{v.name}</span>
              <span className="text-xs text-text-muted font-mono">{v.slug}</span>
              <button onClick={() => removeMut.mutate(v.slug)} disabled={removeMut.isPending}
                className="text-text-muted hover:text-status-error transition-colors p-0.5">
                <Trash2 size={14} />
              </button>
            </div>
          ))}
          {vendors.length === 0 && <p className="text-sm text-text-muted">No vendors added yet.</p>}
        </div>
      )}

      <form onSubmit={handleAdd} className="flex gap-2 pt-2 border-t border-sphotel-border">
        <input className={INPUT + ' w-28'} placeholder="slug" value={slug} onChange={(e) => setSlug(e.target.value)} />
        <input className={INPUT + ' flex-1'} placeholder="Display name" value={name} onChange={(e) => setName(e.target.value)} />
        <button type="submit" disabled={addMut.isPending || !slug.trim() || !name.trim()}
          className="flex items-center gap-1 px-3 py-2 bg-sphotel-accent text-sphotel-accent-fg rounded-lg text-sm font-medium disabled:opacity-50">
          <Plus size={14} /> Add
        </button>
      </form>
      {addMut.isError && <p className="text-xs text-status-error">Failed to add vendor — slug may already exist.</p>}
    </div>
  )
}
