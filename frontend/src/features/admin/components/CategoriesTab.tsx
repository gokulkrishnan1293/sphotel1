import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Check, Pencil, Tag } from 'lucide-react'
import { menuApi } from '../api/menu'

const INPUT = 'bg-transparent text-sm text-text-primary border-b border-sphotel-accent outline-none w-full'

export function CategoriesTab() {
  const qc = useQueryClient()
  const { data: categories = [], isLoading } = useQuery({
    queryKey: ['menu-categories'],
    queryFn: menuApi.listCategories,
  })

  const renameMutation = useMutation({
    mutationFn: ({ old: o, new: n }: { old: string; new: string }) => menuApi.renameCategory(o, n),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['menu-categories'] })
      qc.invalidateQueries({ queryKey: ['menu-items'] })
    },
  })

  const [editingName, setEditingName] = useState<string | null>(null)
  const [draftName, setDraftName] = useState('')

  function startEdit(name: string) { setEditingName(name); setDraftName(name) }

  function save(oldName: string) {
    const trimmed = draftName.trim()
    if (trimmed && trimmed !== oldName) renameMutation.mutate({ old: oldName, new: trimmed })
    setEditingName(null)
  }

  if (isLoading) return <div className="p-6 text-sm text-text-muted">Loading…</div>

  return (
    <div className="flex flex-col gap-4">
      {categories.length === 0 && (
        <p className="text-sm text-text-muted py-4">No categories yet. Add menu items to see categories here.</p>
      )}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {categories.map((cat) => (
          <div key={cat.name} className="bg-bg-elevated border border-sphotel-border rounded-xl p-4 flex flex-col gap-2 group">
            <div className="flex items-start justify-between gap-2">
              <div className="w-8 h-8 rounded-lg bg-sphotel-accent-subtle flex items-center justify-center shrink-0">
                <Tag size={14} className="text-sphotel-accent" />
              </div>
              {editingName === cat.name ? (
                <button onClick={() => save(cat.name)} disabled={renameMutation.isPending}
                  className="text-sphotel-accent hover:opacity-80 disabled:opacity-50 mt-1">
                  <Check size={14} />
                </button>
              ) : (
                <button onClick={() => startEdit(cat.name)}
                  className="text-text-muted hover:text-text-primary transition-colors opacity-0 group-hover:opacity-100 mt-1">
                  <Pencil size={13} />
                </button>
              )}
            </div>
            {editingName === cat.name ? (
              <input autoFocus className={INPUT} value={draftName} onChange={(e) => setDraftName(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') save(cat.name); if (e.key === 'Escape') setEditingName(null) }} />
            ) : (
              <span className="text-sm font-semibold text-text-primary leading-tight">{cat.name}</span>
            )}
            <span className="text-xs text-text-muted">{cat.item_count} item{cat.item_count !== 1 ? 's' : ''}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
